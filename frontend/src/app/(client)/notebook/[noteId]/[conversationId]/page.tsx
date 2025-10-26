'use client'
import ConversationBox from '@/components/client/notebook/ConversationBox'
import dynamic from "next/dynamic";

const NoteComponent = dynamic(
  () => import("@/components/client/notebook/note/NoteComponent"),
  { ssr: false }
);

export default function ConversationPage() {
  return <ConversationBox />
}