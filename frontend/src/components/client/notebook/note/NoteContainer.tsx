// NoteContainer.tsx

'use client'
import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/shadcn-io/spinner';
import ActionTrigger from '@/components/client/ActionTrigger';
import { useNotes } from '@/hooks/useNotes';
import { Note } from '@/schemas/note.interface';
import { Block, } from "@blocknote/core";
import { getNoteById } from '@/lib/api/noteApi';
import { Dialog, DialogClose, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Separator } from '@/components/ui/separator';
import { X } from 'lucide-react';
import { useCreateBlockNote } from '@blocknote/react';
import { BlockNoteView } from '@blocknote/mantine';
import Image from "next/image";
import "@blocknote/mantine/style.css";
import "@blocknote/core/fonts/inter.css";

interface NoteContainerProps {
  initialNotes: Note[];
}

export default function NoteContainer({ initialNotes }: NoteContainerProps) {
  const params = useParams<{ notebookId: string }>();

  const [loading, setLoading] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [noteTitle, setNoteTitle] = useState("New note");
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const { notes, create, update, remove } = useNotes(initialNotes, params.notebookId);

  const editor = useCreateBlockNote({});
  const reset = () => {
    const ids = editor.document.map(b => b.id);
    editor.removeBlocks(ids);
    setBlocks([]);
    setNoteTitle("New note");
  };

  const handleSubmit = async () => {
    if (editingNote) {
      await update(editingNote.id, noteTitle, blocks);
    } else {
      await create(noteTitle, blocks);
    }
    setEditingNote(null);
    reset()
    setIsDialogOpen(false);
  };

  const handleNewNote = () => {
    setEditingNote(null);
    setBlocks([]);
    setNoteTitle("New note");
    setIsDialogOpen(true);
  };

  const handleEdit = async (note: Note) => {
    setEditingNote(note);
    reset()
    const res = await getNoteById(note.id);

    editor.insertBlocks(
      res.blocks,
      editor.document[0],
      "before",
    );
    setNoteTitle(note.title ?? "New note");
    setBlocks(res.blocks);
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: string) => {
    await remove(id);
  };

  if (loading) return <Spinner variant="ring" className="w-4 h-4 animate-spin text-white" />;

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-center p-4 bg-white border-b border-gray-200 rounded-t-xl">
        <Button
          className="px-4 py-2 rounded-full bg-gray-700 text-white hover:bg-gray-500 transition cursor-pointer"
          onClick={handleNewNote}
        >
          + New Note
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1 p-3" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
        {notes.map(note => (
          <div
            key={note.id}
            className="flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer hover:bg-gray-100 transition"
            onClick={() => handleEdit(note)}
          >
            <Image src="/icon/format/note.png" 
              alt="file icon" 
              width={20} height={20}
              className="w-5 h-5"
            />
            <span className="text-gray-700 text-base font-medium">{note.title ?? "Note"}</span>
            <div onClick={(e) => e.stopPropagation()}>
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
                onClick={reset}
                className="opacity-70 w-7 h-7 cursor-pointer
                            rounded-full hover:bg-gray-200 focus:outline-none focus:ring-0"
              >
                <X className="h-4 w-4" />
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
            <BlockNoteView editor={editor} onChange={() => setBlocks(editor.document)} />
          </div>

          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline" onClick={reset} className="rounded-full cursor-pointer">Cancel</Button>
            </DialogClose>
            <Button
              onClick={handleSubmit}
              className="px-4 py-2 rounded-full bg-blue-500 text-white hover:bg-blue-300 cursor-pointer transition"
            >
              {editingNote ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
