import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { ConversationList } from "@/schemas/conversation.interface";
import * as conversationApi from "@/lib/api/conversationApi";

export function useConversation(initialConversations: ConversationList[], notebookId: string) {
  const [conversations, setConversations] = useState(initialConversations);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const router = useRouter();

  const fetchConversations = async () => {
    try {
      const data = await conversationApi.getAllConversations(notebookId);
      setConversations(data);
    } catch {
      toast.error("Failed to fetch conversations");
    }
  };

  const createConversation = async () => {
    try {
      const newConversation = await conversationApi.createConversationApi(notebookId);
      setConversations([newConversation, ...conversations]);
      setSelectedId(newConversation.id);
      router.push(`/notebook/${notebookId}/${newConversation.id}`);
    } catch {
      toast.error("Failed to create conversation");
    }
  };

  const deleteConversation = async (id: string) => {
    try {
      await conversationApi.deleteConversationApi(id);
      const updated = conversations.filter((c) => c.id !== id);
      setConversations(updated);

      if (selectedId === id) {
        const nextId = updated[0]?.id || "1";
        setSelectedId(nextId);
        router.replace(`/notebook/${notebookId}/${nextId}`);
      }
    } catch {
      toast.error("Failed to delete conversation");
    }
  };

  return {
    conversations,
    setConversations,
    selectedId,
    setSelectedId,
    fetchConversations,
    createConversation,
    deleteConversation,
  };
}
