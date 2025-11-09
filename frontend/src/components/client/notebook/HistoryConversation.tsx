'use client'

// React hooks
import { useRouter } from "next/navigation"
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { CirclePlus, MoreVertical } from 'lucide-react'
import axios from 'axios'
import ActionTrigger from "@/components/client/ActionTrigger"
import { ConversationList } from "@/schemas/conversation.interface"
import { toast } from "react-toastify"


export default function HistoryConversation({ initialConversations }: { initialConversations: ConversationList[] }) {
  const router = useRouter()
  const params = useParams<{ notebookId: string, conversationId: string }>()
  const [conversations, setConversations] = useState(initialConversations)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const handleClick = (conversationId: string) => {
    setSelectedId(conversationId)
    router.replace(`/notebook/${params.notebookId}/${conversationId}`)
  }

  
  // useEffect(() => {
  //   if (!params?.notebookId) return
  //   const fetchData = async () => {
  //     const res = await axios.get(
  //       `${process.env.NEXT_PUBLIC_API_URL}/conversations/getAll/${params.notebookId}`
  //     )
  //     setConversations(res.data)
  //   }
  //   fetchData()
  // }, [params.notebookId])

  useEffect(() => {
    setSelectedId(params.conversationId)
    // If no conversationId in URL or it's "1", create a new conversation
    if (!params.conversationId || params.conversationId === "1") {
      createConversation()
    }
  }, [params.conversationId])

  const createConversation = async () => {
    const resCon = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/conversations/create/${params.notebookId}`, 
      {},
      { headers: { 'Content-Type': 'application/json' } }
    );
    const newConversation: ConversationList = {
      id: resCon.data.conversationId,
      title: resCon.data.title
    };
    setConversations([newConversation, ...conversations]);
    setSelectedId(newConversation.id)
    router.push(`/notebook/${params.notebookId}/${newConversation.id}`)
  }

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/conversations/delete/${id}`);
      
      // Filter remained conversation 
      const updatedConversations = conversations.filter(c => c.id !== id);
      setConversations(updatedConversations);

      var newId = selectedId
      if (selectedId === id) {
        if (updatedConversations.length > 0) {
          newId = updatedConversations[0].id;
        }
        else {
          // When no conversation left, create a new one
          newId = "1";
        }
        setSelectedId(newId);
        router.replace(`/notebook/${params.notebookId}/${newId}`);
      }

    } catch (error) {
      toast.error("Failed to delete conversation:");
    }
  };


  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center p-3 mb-2 sticky top-0 bg-white z-10 border-b">
        <p className="text-lg font-semibold text-gray-800">History</p>
        <CirclePlus
          className="text-gray-500 cursor-pointer hover:text-blue-500 transition-colors"
          size={22}
          onClick={createConversation}
        />
      </div>

      {/* Conversation list */}
      <div
        className="flex-1 overflow-y-auto space-y-1 p-3"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {conversations.map(item => (
          <div
            key={item.id}
            onClick={() => handleClick(item.id)}
            className={`flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer transition ${
              selectedId === item.id ? 'bg-gray-100' : 'hover:bg-gray-50'
            }`}
          >
            <span className="text-gray-700 text-sm">{item.title ?? "New chat"}</span>
            <ActionTrigger className="text-gray-500" apiLink={`conversations`} onDelete={() => handleDelete(item.id)} id={item.id}/>
          </div>
        ))}
      </div>
    </div>
  )
}