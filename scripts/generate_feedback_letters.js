#!/usr/bin/env node
/**
 * generate_feedback_letters.js
 *
 * Generates personalized feedback letters from template + data source.
 * Reads a CSV/JSON data file of recipients and merges with a template.
 *
 * Usage:
 *   node scripts/generate_feedback_letters.js --data recipients.json --template letter.txt --output ./letters/
 *   node scripts/generate_feedback_letters.js --data recipients.csv --output ./letters/ --format html
 */

const fs = require('node:fs');
const path = require('node:path');

const PROJECT_ROOT = path.resolve(__dirname, '..');

// --- Argument parsing ---
const args = process.argv.slice(2);
function getArg(flag, fallback = null) {
  const idx = args.indexOf(flag);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : fallback;
}

const dataFile = getArg('--data');
const templateFile = getArg('--template');
const outputDir = getArg('--output', path.join(PROJECT_ROOT, 'output', 'letters'));
const format = getArg('--format', 'txt');
const dryRun = args.includes('--dry-run');

if (!dataFile) {
  console.error('Usage: node generate_feedback_letters.js --data <file> [--template <file>] [--output <dir>] [--format txt|html] [--dry-run]');
  process.exit(1);
}

// --- Template engine ---
function renderTemplate(template, vars) {
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return vars[key] !== undefined ? String(vars[key]) : match;
  });
}

// --- Default template ---
const DEFAULT_TEMPLATE = `Dear {{name}},

Thank you for your participation. Below is your feedback summary:

{{feedback}}

Key strengths identified:
{{strengths}}

Areas for growth:
{{areas_for_growth}}

Next steps:
{{next_steps}}

Best regards,
The Team

Generated: {{date}}
`;

// --- Parse data file ---
function loadData(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const content = fs.readFileSync(filePath, 'utf-8');

  if (ext === '.json') {
    const data = JSON.parse(content);
    return Array.isArray(data) ? data : [data];
  }

  if (ext === '.csv') {
    const lines = content.split('\n').filter(l => l.trim());
    if (lines.length < 2) return [];
    const headers = lines[0].split(',').map(h => h.trim().replace(/^"/, '').replace(/"$/, ''));
    return lines.slice(1).map(line => {
      const values = line.split(',').map(v => v.trim().replace(/^"/, '').replace(/"$/, ''));
      const record = {};
      headers.forEach((h, i) => { record[h] = values[i] || ''; });
      return record;
    });
  }

  throw new Error(`Unsupported data format: ${ext}`);
}

// --- Main ---
function main() {
  console.log('=== Feedback Letter Generator ===\n');

  // Load data
  const recipients = loadData(path.resolve(dataFile));
  console.log(`Loaded ${recipients.length} recipient(s) from ${dataFile}`);

  // Load template
  let template = DEFAULT_TEMPLATE;
  if (templateFile) {
    template = fs.readFileSync(path.resolve(templateFile), 'utf-8');
    console.log(`Using template: ${templateFile}`);
  } else {
    console.log('Using default template');
  }

  // Create output directory
  if (!dryRun) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Generate letters
  const now = new Date().toISOString().split('T')[0];
  let generated = 0;

  for (const recipient of recipients) {
    const vars = {
      ...recipient,
      date: now,
      name: recipient.name || recipient.Name || 'Participant',
    };

    const letter = renderTemplate(template, vars);
    const safeName = (vars.name || `recipient-${generated}`)
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
    const filename = `feedback-${safeName}-${now}.${format}`;
    const outPath = path.join(outputDir, filename);

    if (dryRun) {
      console.log(`  [dry-run] Would write: ${filename} (${letter.length} chars)`);
    } else {
      fs.writeFileSync(outPath, letter, 'utf-8');
      console.log(`  Created: ${filename}`);
    }

    generated++;
  }

  console.log(`\nGenerated ${generated} letter(s) -> ${outputDir}`);
}

main();
