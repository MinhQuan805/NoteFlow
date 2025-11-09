// lib/noteApi.ts
import { Note } from "@/schemas/note.interface";
import { sendRequest } from "@/utils/api";

export async function getAllNotes(notebookId: string) {
  return sendRequest<Note[]>({
    url: `${process.env.NEXT_PUBLIC_API_URL}/notes/getAll/${notebookId}`,
    method: "GET",
  });
}

export async function getNoteById(noteId: string) {
  return sendRequest({
    url: `${process.env.NEXT_PUBLIC_API_URL}/notes/${noteId}`,
    method: "GET",
  });
}

export async function createNote(data: any) {
  return sendRequest({
    url: `${process.env.NEXT_PUBLIC_API_URL}/notes`,
    method: "POST",
    body: data,
  });
}

export async function updateNote(noteId: string, data: any) {
  return sendRequest({
    url: `${process.env.NEXT_PUBLIC_API_URL}/notes/${noteId}`,
    method: "PATCH",
    body: data,
  });
}

export async function deleteNote(noteId: string) {
  return sendRequest({
    url: `${process.env.NEXT_PUBLIC_API_URL}/notes/delete/${noteId}`,
    method: "DELETE",
  });
}
