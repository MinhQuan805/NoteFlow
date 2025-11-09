import { redirect } from "next/navigation"

export default function NoteBookPage({ params }: { params: { notebookId: string } }) {
  redirect(`/notebook/${params.notebookId}/1`)
}