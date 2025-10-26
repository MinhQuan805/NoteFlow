export type RoleType = "user" | "system" | "assistant";

export interface MessagePart {
  type: "text" | "code" | "image" | "source-url" | "reasoning";
  text: string;
}

export interface MessageItem {
  id: string;
  role: RoleType;
  parts: MessagePart[];
}

export interface Conversation {
  title: string;
  notebookId: string;
  messages: MessageItem[];
  created_at: Date;
  updated_at: Date;
  deleted?: boolean;
  deleted_at?: Date | null;
  expireAt?: Date | null;
}