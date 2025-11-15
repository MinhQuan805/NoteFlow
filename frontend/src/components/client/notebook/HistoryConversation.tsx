'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import ActionTrigger from "@/components/client/ActionTrigger"
import { ConversationList } from "@/schemas/conversation.interface"
import { useConversation } from '@/hooks/useConversation'
import { CirclePlus } from 'lucide-react'

export default function HistoryConversation({ initialConversations }: { initialConversations: ConversationList[] }) {
  const params = useParams<{ notebookId: string; conversationId: string }>()
  const router = useRouter()

  const {
    conversations,
    selectedId,
    setSelectedId,
    createConversation,
    deleteConversation,
  } = useConversation(initialConversations, params.notebookId)

  const handleClick = (conversationId: string) => {
    setSelectedId(conversationId)
    router.replace(`/notebook/${params.notebookId}/${conversationId}`)
  }

  useEffect(() => {
    setSelectedId(params.conversationId)
    if (!params.conversationId || params.conversationId === '1') {
      createConversation()
    }
  }, [params.conversationId])

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
        {conversations.map((item) => (
          <div
            key={item.id}
            onClick={() => handleClick(item.id)}
            className={`flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer transition ${
              selectedId === item.id ? 'bg-gray-100' : 'hover:bg-gray-50'
            }`}
          >
            <span className="text-gray-700 text-sm">{item.title ?? 'New chat'}</span>
            <ActionTrigger
              className="text-gray-500"
              apiLink={`conversations`}
              onDelete={() => deleteConversation(item.id)}
              id={item.id}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
