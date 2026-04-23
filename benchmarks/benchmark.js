/**
 * Benchmark suite for the knowledge base operations.
 * Measures throughput and latency of key pipeline stages.
 *
 * Usage:
 *   node benchmarks/benchmark.js
 *   node benchmarks/benchmark.js --only ingest
 *   node benchmarks/benchmark.js --iterations 100
 */

const { performance, PerformanceObserver } = require('node:perf_hooks');
const { readFileSync, readdirSync, statSync } = require('node:fs');
const path = require('node:path');

const PROJECT_ROOT = path.resolve(__dirname, '..');

// --- Configuration ---
const DEFAULT_ITERATIONS = 50;
const args = process.argv.slice(2);
const iterations = parseInt(args.find((_, i, a) => a[i - 1] === '--iterations') || DEFAULT_ITERATIONS);
const only = args.find((_, i, a) => a[i - 1] === '--only') || null;

// --- Utilities ---
function formatMs(ms) {
  if (ms < 1) return `${(ms * 1000).toFixed(0)}us`;
  if (ms < 1000) return `${ms.toFixed(2)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

function stats(times) {
  const sorted = [...times].sort((a, b) => a - b);
  const sum = sorted.reduce((a, b) => a + b, 0);
  return {
    min: sorted[0],
    max: sorted[sorted.length - 1],
    mean: sum / sorted.length,
    median: sorted[Math.floor(sorted.length / 2)],
    p95: sorted[Math.floor(sorted.length * 0.95)],
    p99: sorted[Math.floor(sorted.length * 0.99)],
  };
}

function runBench(name, fn, iters = iterations) {
  if (only && name !== only) return null;

  const times = [];
  // Warmup
  for (let i = 0; i < 3; i++) fn();

  for (let i = 0; i < iters; i++) {
    const start = performance.now();
    fn();
    times.push(performance.now() - start);
  }

  const s = stats(times);
  console.log(`  ${name}:`);
  console.log(`    mean=${formatMs(s.mean)}  median=${formatMs(s.median)}  p95=${formatMs(s.p95)}  min=${formatMs(s.min)}  max=${formatMs(s.max)}`);
  return s;
}

// --- Benchmarks ---
console.log(`\n=== Knowledge Base Benchmarks (${iterations} iterations) ===\n`);

// 1. JSON parsing throughput
const sampleJsonPath = path.join(PROJECT_ROOT, 'orchestrator_state.json');
if (statSync(sampleJsonPath, { throwIfNoEntry: false })) {
  const jsonContent = readFileSync(sampleJsonPath, 'utf-8');
  runBench('json-parse', () => JSON.parse(jsonContent));
  runBench('json-roundtrip', () => JSON.stringify(JSON.parse(jsonContent)));
}

// 2. File listing (simulated intake scan)
const intakeDir = path.join(PROJECT_ROOT, 'intake');
try {
  statSync(intakeDir);
  runBench('intake-scan', () => {
    readdirSync(intakeDir, { recursive: true });
  });
} catch {
  console.log('  intake-scan: SKIPPED (no intake/ directory)');
}

// 3. Content hashing
const crypto = require('node:crypto');
const testPayload = Buffer.alloc(1024 * 64, 'a'); // 64KB
runBench('sha256-64kb', () => {
  crypto.createHash('sha256').update(testPayload).digest('hex');
});

const largePayload = Buffer.alloc(1024 * 1024, 'b'); // 1MB
runBench('sha256-1mb', () => {
  crypto.createHash('sha256').update(largePayload).digest('hex');
});

// 4. JSONL line parsing
const sampleLines = Array.from({ length: 1000 }, (_, i) =>
  JSON.stringify({ id: i, status: 'OPEN', content: `Atom ${i} content here` })
).join('\n');

runBench('jsonl-parse-1000', () => {
  sampleLines.split('\n').map(line => JSON.parse(line));
});

// 5. String search (simulated dedup check)
const haystack = Array.from({ length: 10000 }, (_, i) => `entry-${i}-${crypto.randomBytes(8).toString('hex')}`);
const needle = haystack[7777];
runBench('linear-search-10k', () => {
  haystack.indexOf(needle);
});

const haystackSet = new Set(haystack);
runBench('set-lookup-10k', () => {
  haystackSet.has(needle);
});

console.log('\n=== Benchmarks complete ===\n');
