'use client'

// React hooks
import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import axios from 'axios'
import ActionTrigger from "@/components/client/ActionTrigger"
import { toast } from 'react-toastify'
import { Spinner } from '@/components/ui/shadcn-io/spinner'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog"
import { Separator } from "@/components/ui/separator"

import { Button } from '@/components/ui/button'
import { X } from 'lucide-react'
import { Block } from "@blocknote/core";
import "@blocknote/core/fonts/inter.css";
import { BlockNoteView } from "@blocknote/mantine";
import "@blocknote/mantine/style.css";
import { useCreateBlockNote } from "@blocknote/react";
import { Note } from '@/schemas/note.interface'

export default function NoteContainer({ initialNotes}: { initialNotes: Note[] }) {
  const [notes, setNotes] = useState(initialNotes)
  const params = useParams<{ notebookId: string }>()

  const [editingNoteId, setEditingNoteId] = useState<string>("")
  const [noteTitle, setNoteTitle] = useState<string>("New note")

  const [loading, setLoading] = useState(true)

  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const [blocks, setBlocks] = useState<Block[]>([]);

  const resetImport = () => {
    const currentBlockIds = editor.document.map(b => b.id);
    editor.removeBlocks(currentBlockIds);
    setBlocks([]);
    setEditingNoteId("");
  }


  // Creates a new editor instance.
  const editor = useCreateBlockNote({});

  const handleEdit = async (noteId: string) => {
    setEditingNoteId(noteId);

    const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/notes/${noteId}`);
    const loadedBlocks = res.data.blocks as Block[];

    // Remove all existing blocks
    const currentBlockIds = editor.document.map(b => b.id);
    editor.removeBlocks(currentBlockIds);
    
    // Insert before first block
    editor.insertBlocks(
      loadedBlocks,
      editor.document[0],
      "before",
    );

    setBlocks(loadedBlocks);
    setNoteTitle(res.data.title);
  };


  const handleCreate = async () => {
    const newNote = {
      "notebookId": params.notebookId,
      "title": noteTitle,
      "blocks": blocks,
      "updated_at": new Date().toISOString(),
    }
    setIsDialogOpen(false);
    const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/notes`, newNote);
    setNotes([res.data, ...notes])
    resetImport();
  };

  const handleUpdate = async () => {
    const data = {
      "title": noteTitle,
      "blocks": blocks,
    }
    setIsDialogOpen(false);
    const res = await axios.patch(`${process.env.NEXT_PUBLIC_API_URL}/notes/${editingNoteId}`, data);
    setNotes(prevNotes => {
      const updated = prevNotes.filter(c => c.id !== editingNoteId);
      return [res.data, ...updated];
    });
    resetImport();
  };

  const handleDelete = async (noteId: string) => {
    try {
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/notes/delete/${noteId}`);
      
      // Filter remained notes
      const updatedNotes = notes.filter(c => c.id !== noteId);
      setNotes(updatedNotes);
    } catch {
      toast.error("Failed to delete note");
    }
  };

  return (
    loading ? (
      <div className="flex items-center justify-center gap-2 p-3">
        <Spinner variant="ring" className="w-4 h-4 animate-spin text-white" />
      </div>
    ) : (
        <div className="flex flex-col h-full">
          <div className="flex justify-center p-4 bg-white border-b border-gray-200">
            <Button
              className="px-4 py-2 rounded-full bg-gray-700 text-white hover:bg-gray-500 cursor-pointer transition"
              onClick={() => {
                setNoteTitle("New note");
                setIsDialogOpen(true);
              }}
            >
              + New Note
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto space-y-1 p-3" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
            {notes.map(note => (
              <div
                className="flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer transition hover:bg-gray-100"
                onClick={() => {
                  handleEdit(note.id)
                  setIsDialogOpen(true);
                }}
              >
              <img src='/icon/format/note.png' alt="file icon" className="w-5 h-5"/>
              <span className="text-gray-700 text-base font-medium">{note.title ?? "Note"}</span>
              <div
                onClick={(e) => e.stopPropagation()}
              >
                <ActionTrigger
                  className="text-gray-500"
                  apiLink={`notes`}
                  onDelete={() => handleDelete(note.id)}
                  id={note.id}
                />
              </div>
          </div>
          ))}
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="sm:max-w-[60vw] max-h-[80vh] overflow-auto break-words" showCloseButton={false}>
            <div className="flex items-center justify-between">
              <DialogHeader>
                <DialogTitle>Note Details</DialogTitle>
              </DialogHeader>
              <DialogClose asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => {
                    resetImport();
                    setIsDialogOpen(false);
                  }}
                  className="opacity-70 w-7 h-7 cursor-pointer
                            rounded-full hover:bg-gray-200 focus:outline-none focus:ring-0"
                >
                  <X className="h-2 w-2" />
                </Button>
              </DialogClose>
            </div>
            <div className="h-[400px] max-h-[65vh] overflow-y-auto">
              <div className="max-w-full flex flex-col items-center">
                <input
                  placeholder="Enter note title..."
                  className="w-full focus:outline-none max-w-[70%] text-lg font-medium"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                />
                <Separator className="my-2 max-w-[70%]" />
              </div>
              <BlockNoteView
                editor={editor}
                onChange={() => {
                  // Sets the document JSON whenever the editor content changes.
                  setBlocks(editor.document);
                }}
              />
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" onClick={resetImport} className="rounded-full cursor-pointer">Cancel</Button>
              </DialogClose>
              <Button
                onClick={() => editingNoteId ? handleUpdate() : handleCreate()}
                className="px-4 py-2 rounded-full bg-blue-500 text-white hover:bg-blue-300 cursor-pointer transition"
              >
                {editingNoteId ? "Update" : "Create"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    )
  )
}
