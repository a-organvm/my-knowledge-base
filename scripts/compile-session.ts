import * as fs from 'fs';
import * as path from 'path';
import { randomUUID } from 'crypto';
import { KnowledgeDatabase } from '../src/database.js';
import { DocumentAtomizer } from '../src/document-atomizer.js';
import { WikiCompiler } from '../src/wiki-compiler/wiki-compiler.js';

const dbPath = '/tmp/wiki.db';
const intakeDir = '/tmp/wiki-compile-intake';
const outputDir = '/tmp/wiki-compiled';

async function run() {
  if (fs.existsSync(dbPath)) fs.unlinkSync(dbPath);
  
  const db = new KnowledgeDatabase(dbPath);
  const atomizer = new DocumentAtomizer();
  
  const files = fs.readdirSync(intakeDir);
  
  for (const file of files) {
    if (!file.endsWith('.md')) continue;
    const content = fs.readFileSync(path.join(intakeDir, file), 'utf8');
    
    const doc = {
      id: randomUUID(),
      title: file.replace('.md', ''),
      content,
      created: new Date(),
      modified: new Date(),
      format: 'markdown' as const,
      metadata: {}
    };
    
    db.insertDocument(doc);
    
    const units = atomizer.atomizeDocument(doc);
    for (const unit of units) {
      db.insertAtomicUnit(unit);
    }
    console.log(`Ingested ${file} into ${units.length} units`);
  }
  
  const compiler = new WikiCompiler(db, {
    outputDir,
    batchConcurrency: 3
  });
  
  await compiler.compile();
  
  db.close();
}

run().catch(console.error);
