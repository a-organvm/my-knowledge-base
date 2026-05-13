import { KnowledgeDatabase } from '../database.js';
import { WikiCompiler } from './wiki-compiler.js';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
  const args = process.argv.slice(2);
  const dbPath = process.env.DB_PATH || './db/knowledge.db';
  const outputDir = args[0] || './compiled-wiki';
  
  console.log(`Starting Wiki Compiler CLI...`);
  console.log(`Database: ${dbPath}`);
  console.log(`Output Directory: ${outputDir}`);
  
  const db = new KnowledgeDatabase(dbPath);
  
  try {
    const compiler = new WikiCompiler(db, {
      outputDir,
      batchConcurrency: 10
    });
    
    await compiler.compile();
    
    console.log(`\nWiki compiled successfully.`);
  } catch (error) {
    console.error('Error during wiki compilation:', error);
    process.exit(1);
  } finally {
    db.close();
  }
}

main().catch(console.error);
