import { ConversationList } from "@/schemas/conversation.interface";
import { sendRequest } from "@/utils/api";

export async function getAllConversations(notebookId: string) {
  return sendRequest<ConversationList[]>({
    url: `${process.env.NEXT_PUBLIC_API_URL}/conversations/getAll/${notebookId}`,
    method: "GET",
  });
}