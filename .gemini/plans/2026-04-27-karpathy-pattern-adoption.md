# Spec: Karpathy LLM-Wiki Pattern Adoption for `my-knowledge-base`

## Origin & Context
- **Trigger**: Audit of potential system substrates (2026-04-27) flagged Andrej Karpathy's LLM-wiki architecture as a highest-leverage move for `my-knowledge-base`.
- **Core Principle**: Shift the complexity of knowledge assembly from "query-time" (traditional RAG) to "compile-time". Instead of retrieving vector-fragmented chunks and relying on the LLM to synthesize them on the fly, the system uses an LLM as a "compiler" to pre-process raw transcripts into a structured, hyperlinked, human-readable wiki.

## Current vs. Target State
- **Current State (`my-knowledge-base`)**: Operates on a traditional retrieval paradigm. It atomizes conversations into chunks (`AtomicUnit`), stores them in ChromaDB (semantic) and SQLite FTS5 (keyword), and uses RRF fusion to retrieve them. While it has an LLM Intelligence layer (`InsightExtractor`, `SmartTagger`), it fundamentally retrieves scattered fragments at query-time.
- **Target State (Karpathy Pattern)**: A new "Compiler" subsystem that acts on the ingested federated sources to produce a static, interconnected set of markdown documents (the Wiki). Retrieval becomes primarily a navigation task (reading the compiled wiki) rather than a dynamic synthesis task.

## Architectural Additions

### 1. The Wiki Compiler Subsystem
Introduce a new `WikiCompiler` class (`src/wiki-compiler/`) that operates sequentially over the corpus.
- **Phase A (Topic Extraction & Clustering)**: LLM scans raw conversations and atomic units, clustering them into canonical "Topics" or "Entities".
- **Phase B (Page Synthesis)**: For each Topic, the LLM generates a comprehensive, narrative markdown page synthesizing all relevant insights, decisions, and code snippets across the corpus.
- **Phase C (Cross-linking)**: The LLM processes the generated pages to inject markdown cross-links (`[Topic B](./topic-b.md)`) whenever a concept is referenced, forming a dense knowledge graph.

### 2. Output Format (The Compiled Wiki)
- **Directory Structure**: A static output directory (`/compiled-wiki/`) containing `.md` files.
- **Index Generation**: An auto-generated `index.md` serving as the root ontology.
- **Integration with ORGAN-V (Logos)**: The compiled markdown files can be directly ingested into Jekyll/Astro sites for public or semi-public distribution, perfectly aligning with POSSE.

### 3. Workflow Modifications
- `npm run compile:wiki`: New CLI command to trigger the pipeline.
- The pipeline relies heavily on the `BatchProcessor` and `AIFactory` already present, but introduces a multi-step reduce operation (Map raw units -> Reduce to Topic Pages -> Refine links).

## Strategic Leverage
1. **Zero-Latency Retrieval**: The user navigates pre-computed pages instantly.
2. **Higher Quality Synthesis**: The LLM has the full time and context to synthesize a cohesive narrative during the build step, avoiding query-time context window limits and hallucinations.
3. **Artifact Portability**: The output is just markdown files, deeply compatible with Obsidian, GitHub, and standard SSGs.
