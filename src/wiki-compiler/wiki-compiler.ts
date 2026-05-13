import * as fs from 'fs';
import * as path from 'path';
import { KnowledgeDatabase } from '../database.js';
import { AIFactory } from '../ai-factory.js';
import { AIProvider } from '../ai-types.js';
import { AtomicUnit } from '../types.js';
import { BatchProcessor } from '../batch-processor.js';

export interface WikiCompilerOptions {
  outputDir: string;
  batchConcurrency?: number;
  provider?: AIProvider;
  maxTopics?: number;
}

export class WikiCompiler {
  private db: KnowledgeDatabase;
  private options: WikiCompilerOptions;
  private ai: AIProvider;
  private outputDir: string;

  constructor(db: KnowledgeDatabase, options: WikiCompilerOptions) {
    this.db = db;
    this.options = options;
    this.outputDir = path.resolve(options.outputDir);
    this.ai = options.provider || AIFactory.getConfiguredProvider();
  }

  public async compile(): Promise<void> {
    console.log(`Starting Wiki Compilation pipeline...`);
    console.log(`Output directory: ${this.outputDir}`);

    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }

    // Step 1: Gather raw material
    console.log(`Fetching all atomic units...`);
    const allUnits = this.db.getAllAtomicUnits();
    console.log(`Found ${allUnits.length} units to compile.`);

    if (allUnits.length === 0) {
      console.log(`No units found. Aborting compilation.`);
      return;
    }

    // Phase A: Topic Extraction & Clustering
    console.log(`\nPhase A: Topic Extraction & Clustering`);
    const topicsMap = await this.extractTopics(allUnits);

    // Phase B: Page Synthesis
    console.log(`\nPhase B: Page Synthesis`);
    await this.synthesizePages(topicsMap);

    // Phase C: Cross-linking
    console.log(`\nPhase C: Cross-linking`);
    await this.crossLinkPages(Object.keys(topicsMap));

    console.log(`\nWiki compilation complete. Output saved to: ${this.outputDir}`);
  }

  private async extractTopics(units: AtomicUnit[]): Promise<Record<string, AtomicUnit[]>> {
    const topicsMap: Record<string, AtomicUnit[]> = {};
    const processor = new BatchProcessor('.batch-checkpoints/wiki-topics', {
      concurrency: this.options.batchConcurrency || 3,
    });

    const topicPrompt = (unit: AtomicUnit) => `Extract 1-3 topic labels from this text. Reply with ONLY a comma-separated list. No preamble, no explanation, no quotes.

Example input: "How to set up Node.js authentication with JWT tokens"
Example output: Node.js, Authentication, JWT

Text: ${unit.title} ${unit.content.slice(0, 500)}

Topics:`;

    let results: Map<number, any>;
    if (processor.hasCheckpoint()) {
      const { results: initialResults } = processor.loadCheckpoint();
      results = await processor.processWithState(units, async (unit) => {
        const response = await this.ai.chat([{ role: 'user', content: topicPrompt(unit) }], { maxTokens: 60, temperature: 0.1 });
        const topics = this.parseTopicResponse(response);
        return { unit, topics };
      }, initialResults);
    } else {
      results = await processor.process(units, async (unit) => {
        const response = await this.ai.chat([{ role: 'user', content: topicPrompt(unit) }], { maxTokens: 60, temperature: 0.1 });
        const topics = this.parseTopicResponse(response);
        return { unit, topics };
      });
    }

    for (const [_, res] of results) {
      if (res.success && res.result) {
        const { unit, topics } = res.result;
        for (const topic of topics) {
          const canonical = this.normalizeTopicName(topic);
          if (!topicsMap[canonical]) {
            topicsMap[canonical] = [];
          }
          topicsMap[canonical].push(unit);
        }
      }
    }

    const allTopics = Object.keys(topicsMap);
    const maxTopics = this.options.maxTopics || 25;
    console.log(`Extracted ${allTopics.length} unique topics. Filtering to top ${maxTopics} for synthesis...`);

    // Sort topics by number of units (descending) and take top N
    const topTopics = allTopics
      .sort((a, b) => topicsMap[b].length - topicsMap[a].length)
      .slice(0, maxTopics);

    // Log selected topics
    for (const topic of topTopics) {
      console.log(`  → ${topic} (${topicsMap[topic].length} units)`);
    }

    const filteredTopicsMap: Record<string, AtomicUnit[]> = {};
    for (const topic of topTopics) {
      filteredTopicsMap[topic] = topicsMap[topic];
    }

    return filteredTopicsMap;
  }

  /**
   * Parse a topic extraction response, stripping any verbose preambles
   * that small models tend to produce.
   */
  private parseTopicResponse(response: string): string[] {
    let text = response.trim();

    // Strip common preamble patterns from small models
    // e.g. "I would identify the following core TOPICS or ENTITIES:\n\nTopic1, Topic2"
    // e.g. "Based on the provided knowledge unit, the topics are:\n\nTopic1, Topic2"
    const preamblePatterns = [
      /^.*?(?:topics?|entities?|labels?)\s*(?:are|is|:)\s*/is,
      /^(?:I would identify|Based on|Here are|The following).*?:\s*/is,
      /^.*?comma-separated list.*?:\s*/is,
    ];

    for (const pattern of preamblePatterns) {
      text = text.replace(pattern, '');
    }

    // Take only the first line that looks like a comma-separated list
    const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
    const candidateLine = lines[0] || text;

    return candidateLine
      .split(',')
      .map(t => t.trim())
      .map(t => t.replace(/^["'\-*•\d.]+\s*/, '')) // strip leading bullets/quotes/numbers
      .map(t => t.replace(/["']+$/g, '')) // strip trailing quotes
      .filter(t => t.length > 1 && t.length < 60) // reject empty or absurdly long "topics"
      .slice(0, 3); // max 3 topics
  }

  private async synthesizePages(topicsMap: Record<string, AtomicUnit[]>): Promise<void> {
    const topics = Object.keys(topicsMap);

    // Create an index page
    let indexContent = `# Knowledge Wiki Index\n\n`;
    const sortedTopics = [...topics].sort();
    for (const topic of sortedTopics) {
      const slug = this.slugify(topic);
      indexContent += `- [${topic}](./${slug}.md) (${topicsMap[topic].length} units)\n`;
    }
    fs.writeFileSync(path.join(this.outputDir, 'index.md'), indexContent);

    const processor = new BatchProcessor('.batch-checkpoints/wiki-pages', {
      concurrency: this.options.batchConcurrency || 3,
    });

    await processor.process(topics, async (topic) => {
      const slug = this.slugify(topic);
      const units = topicsMap[topic];

      // Limit to 15 most relevant units to avoid overwhelming the model
      const selectedUnits = units.slice(0, 15);
      const unitsText = selectedUnits.map((u, i) => `--- Unit ${i + 1} ---\nTitle: ${u.title}\n${u.content}`).join('\n\n');

      const prompt = `Write a wiki article about "${topic}" using ONLY the source material below. Do not invent facts. Synthesize the information into a structured markdown document with headings and paragraphs. Stay faithful to the source material.

Source Material:
${unitsText}

Write the article now:`;

      const response = await this.ai.chat([{ role: 'user', content: prompt }], { maxTokens: 4000, temperature: 0.3 });

      const filePath = path.join(this.outputDir, `${slug}.md`);
      fs.writeFileSync(filePath, `# ${topic}\n\n${response}`);

      return slug;
    });
  }

  private async crossLinkPages(topics: string[]): Promise<void> {
    // This is a naive cross-linking approach: finding exact topic names in the markdown and replacing them with links.
    // For a more advanced approach, the LLM could be used to intelligently insert links.
    const sortedTopics = [...topics].sort((a, b) => b.length - a.length); // Longest first to avoid partial matches

    for (const file of fs.readdirSync(this.outputDir)) {
      if (!file.endsWith('.md') || file === 'index.md') continue;

      const filePath = path.join(this.outputDir, file);
      let content = fs.readFileSync(filePath, 'utf-8');

      let modified = false;
      const currentSlug = file.replace('.md', '');

      for (const topic of sortedTopics) {
        const slug = this.slugify(topic);
        if (slug === currentSlug) continue; // Don't link to self

        // Simple regex to match the topic whole word, not inside an existing link
        const regex = new RegExp(`(?<!\\[)(?:\\b)(${this.escapeRegExp(topic)})(?:\\b)(?!\\]|\\()`, 'gi');

        if (regex.test(content)) {
          content = content.replace(regex, `[$1](./${slug}.md)`);
          modified = true;
        }
      }

      if (modified) {
        fs.writeFileSync(filePath, content);
      }
    }
  }

  private normalizeTopicName(topic: string): string {
    return topic.trim().replace(/^["']|["']$/g, '');
  }

  private slugify(text: string): string {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '');
  }

  private escapeRegExp(string: string): string {
    return string.replace(/[.*+?^$\{}()|[\]\\]/g, '\\$&');
  }
}
