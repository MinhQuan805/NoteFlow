import { redirect } from "next/navigation"

export default function NoteBookPage({ params }: { params: { noteId: string } }) {
  redirect(`/notebook/${params.noteId}/1`)
}