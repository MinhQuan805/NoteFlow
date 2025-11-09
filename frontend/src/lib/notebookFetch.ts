// lib/noteApi.ts
import { Note } from "@/schemas/note.interface";
import { sendRequest } from "@/utils/api";

export async function getAllNotes(notebookId: string) {
  return sendRequest<Note[]>({
    url: `${process.env.NEXT_PUBLIC_API_URL}/notes/getAll/${notebookId}`,
    method: "GET",
  });
}
