'use client'


import SourceFileUpload from '@/components/client/notebook/source/SourceFileUpload'
import HistoryConversation from '@/components/client/notebook/HistoryConversation'

import dynamic from "next/dynamic";

const NoteComponent = dynamic(
  () => import("@/components/client/notebook/note/NoteComponent"),
  { ssr: false }
);

export default function NotebookLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen p-3 gap-4 bg-gray-100">
      {/* Sidebar */}
      <div className="w-1/4 flex flex-col gap-3">
        <div className="h-1/2 rounded-3xl bg-white">
          <SourceFileUpload />
        </div>
        <div className="flex-1 overflow-y-auto h-1/2 rounded-3xl bg-white">
          <HistoryConversation/>
        </div>
      </div>

      {/* Main conversation box */}
      <div className="flex-1 w-1/2 bg-white p-1 rounded-3xl">{children}</div>

      <div className="w-1/4 rounded-3xl bg-white">
        <NoteComponent />
      </div>
    </div>
  )
}
