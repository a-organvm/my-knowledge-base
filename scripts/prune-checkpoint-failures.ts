/**
 * Utility script to prune failed entries from batch-progress.json
 * to allow Resuming with a different model.
 */

import * as fs from 'fs';
import * as path from 'path';

const checkpointPath = '.batch-checkpoints/wiki-topics/.batch-progress.json';
const backupPath = checkpointPath + '.bak';

async function prune() {
  if (!fs.existsSync(checkpointPath)) {
    console.error('Checkpoint file not found');
    return;
  }

  console.log(`Pruning failures from ${checkpointPath}...`);
  
  // Backup
  fs.copyFileSync(checkpointPath, backupPath);
  console.log(`Backup created at ${backupPath}`);

  const data = JSON.parse(fs.readFileSync(checkpointPath, 'utf-8'));
  const results = data.results;
  const newResults: Record<string, any> = {};
  
  let prunedCount = 0;
  let successCount = 0;

  for (const [id, res] of Object.entries(results)) {
    if ((res as any).success === true) {
      newResults[id] = res;
      successCount++;
    } else {
      prunedCount++;
    }
  }

  console.log(`Successes: ${successCount}`);
  console.log(`Pruned Failures: ${prunedCount}`);

  data.results = newResults;
  data.progress.failed = 0;
  data.progress.processed = successCount;
  data.progress.succeeded = successCount;

  fs.writeFileSync(checkpointPath, JSON.stringify(data, null, 2));
  console.log('Checkpoint file updated successfully.');
}

prune().catch(console.error);
