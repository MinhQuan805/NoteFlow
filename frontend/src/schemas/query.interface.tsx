import { MessageItem } from '@/schemas/conversation.interface'

export interface QueryRequest {
  message: MessageItem;
  query: string;
  file_filters?: string[] | null;
}

export interface QueryResponse {
  response_message: MessageItem;
  intent: string;
  mode: string;
}
