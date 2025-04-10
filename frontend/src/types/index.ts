
export interface KeywordString {
  id: string;
  name: string;
  keywords: string[];
  isActive: boolean;
  collectedContent: string[] | undefined;
  lastCollectedAt?: Date;
  prompts: string
}

export interface DialogueMessage {
  id: string;
  sender: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export interface DialogueSession {
  id: string;
  keywordStringId: string;
  messages: DialogueMessage[];
  createdAt: Date;
}
