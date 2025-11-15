import { ConversationList } from "@/schemas/conversation.interface";
import { sendRequest } from "@/utils/api";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getAllConversations(notebookId: string) {
  return sendRequest<ConversationList[]>({
    url: `${process.env.NEXT_PUBLIC_API_URL}/conversations/getAll/${notebookId}`,
    method: "GET",
  });
}

export const createConversationApi = async (notebookId: string): Promise<ConversationList> => {
  const res = await axios.post(
    `${API_URL}/conversations/create/${notebookId}`,
    {},
    { headers: { "Content-Type": "application/json" } }
  );
  return {
    id: res.data.conversationId,
    title: res.data.title,
  };
};

export const deleteConversationApi = async (id: string) => {
  await axios.delete(`${API_URL}/conversations/delete/${id}`);
};