// noteApi.ts

import { Note } from "@/schemas/note.interface";
import { sendRequest } from "@/utils/api";
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getAllNotes(notebookId: string) {
  return sendRequest<Note[]>({
    url: `${API_URL}/notes/getAll/${notebookId}`,
    method: "GET",
  });
}

export const getNoteById = async (id: string) => {
  const res = await axios.get(`${API_URL}/notes/${id}`);
  return res.data;
};

export const createNote = async (note: Partial<Note>) => {
  const res = await axios.post(`${API_URL}/notes`, note);
  return res.data;
};

export const updateNote = async (id: string, data: Partial<Note>) => {
  const res = await axios.patch(`${API_URL}/notes/${id}`, data);
  return res.data;
};

export const deleteNote = async (id: string) => {
  await axios.delete(`${API_URL}/notes/delete/${id}`);
};