import { IntakePolicyEngine } from './intake-policy.js';

export const CHAT_THREAD_CONTENT_HASH_VERSION = 2;

export interface HashableChatTurn {
  turnIndex: number;
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
}

export function createChatThreadContentHash(input: {
  turns: HashableChatTurn[];
}): string {
  const turns = input.turns
    .filter((turn) => turn.content.trim().length > 0)
    .slice()
    .sort((left, right) => left.turnIndex - right.turnIndex)
    .map((turn) => ({
      role: turn.role,
      content: turn.content.trim(),
    }));

  return IntakePolicyEngine.contentHash(
    JSON.stringify({
      turns,
    }),
  );
}
