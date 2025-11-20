// useNotes.tsx
import { useState } from 'react';
import { Note } from '@/schemas/note.interface';
import * as noteApi from '@/lib/api/noteApi';
import { toast } from 'react-toastify';
import { Block } from "@blocknote/core";

export function useNotes(initialNotes: Note[], notebookId: string) {
  const [notes, setNotes] = useState(initialNotes);

  const create = async (title: string, blocks: Block[]) => {
    const newNote = {
      "notebookId": notebookId,
      "title": title,
      "blocks": blocks,
      "updated_at": new Date().toISOString(),
    }
    try {
      const newRes = await noteApi.createNote(newNote);
      setNotes([newRes, ...notes]);
      return newRes;
    } catch {
      toast.error("Failed to create note");
      return null;
    }
  };

  const update = async (id: string, title: string, blocks: Block[]) => {
    try {
      const data = {
        title,
        blocks,
      }
      const updatedNote = await noteApi.updateNote(id, data);
      setNotes(prev => [updatedNote, ...prev.filter(n => n.id !== id)]);
      return updatedNote;
    } catch {
      toast.error("Failed to update note");
      return null;
    }
  };

  const remove = async (id: string) => {
    try {
      await noteApi.deleteNote(id);
      setNotes(prev => prev.filter(n => n.id !== id));
    } catch {
      toast.error("Failed to delete note");
    }
  };

  return { notes, create, update, remove, setNotes };
}
