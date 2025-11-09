// app/notebook/[notebookId]/layout.tsx

import SourceFileUpload from '@/components/client/notebook/source/SourceFileUpload'
import HistoryConversation from '@/components/client/notebook/HistoryConversation'
import { Button } from '@/components/ui/button'
import { getAllNotes } from '@/lib/noteFetch'
import NoteContainer from '@/components/client/notebook/note/NoteContainer'
import { getAllFiles } from '@/lib/fileFetch'
import { getAllConversations } from '@/lib/conversationFetch'


export default async function NotebookLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: { notebookId: string }
}) {
  // Fetch data with server
  const notes = await getAllNotes(params.notebookId);
  const files = await getAllFiles(params.notebookId);
  const conversations = await getAllConversations(params.notebookId);

  return (
    <div className="h-screen">
      <div className="flex p-3 gap-4 bg-gray-100 h-full">
        {/* Sidebar */}
        <div className="w-1/4 flex flex-col gap-3 h-full">
          <div className="h-1/2 rounded-3xl bg-white">
            <SourceFileUpload initialFiles={files}/>
          </div>
          <div className="flex-1 overflow-y-auto h-1/2 rounded-3xl bg-white">
            <HistoryConversation initialConversations={conversations}/>
          </div>
        </div>

        {/* Main conversation box */}
        <div className="flex-1 w-1/2 bg-white p-1 rounded-3xl">{children}</div>

        {/* Note list (client component) */}
        <div className="w-1/4 rounded-3xl bg-white">
          <NoteContainer initialNotes={notes}/>
        </div>
      </div>
    </div>
  )
}
