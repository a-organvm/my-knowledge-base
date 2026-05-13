import { AIFactory } from './src/ai-factory.js';
import { getConfig } from './src/config.js';

async function test() {
  const config = getConfig().getAll();
  console.log('Config LLM:', JSON.stringify(config.llm, null, 2));
  
  const provider = AIFactory.getConfiguredProvider();
  console.log('Provider ID:', provider.id);
  console.log('Provider Name:', provider.name);
  // @ts-ignore
  console.log('Provider Default Model:', provider.defaultModel);
}

test().catch(console.error);
