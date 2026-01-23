// NoteContainer.tsx

'use client'
import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/shadcn-io/spinner';
import ActionTrigger from '@/components/client/ActionTrigger';
import { useNotes } from '@/hooks/useNotes';
import { useSlides } from '@/hooks/useSlides';
import { Note } from '@/schemas/note.interface';
import { Slide } from '@/schemas/slide.interface';
import { Block, } from "@blocknote/core";
import { getNoteById } from '@/lib/api/noteApi';
import { getSlideById } from '@/lib/api/slideApi';
import { Dialog, DialogClose, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { X, Presentation, StickyNote,  } from 'lucide-react';
import { useCreateBlockNote } from '@blocknote/react';
import { BlockNoteView } from '@blocknote/mantine';
import Image from "next/image";
import SlidesViewer from './SlidesViewer';
import axios from 'axios';
import { toast } from 'react-toastify';
import "@blocknote/mantine/style.css";
import "@blocknote/core/fonts/inter.css";

interface NoteContainerProps {
  initialNotes: Note[];
  initialSlides: Slide[];
}

export default function NoteContainer({ initialNotes, initialSlides }: NoteContainerProps) {
  const params = useParams<{ notebookId: string; conversationId: string }>();

  // Notes state
  const [loading, setLoading] = useState(false);
  const [editingNote, setEditingNote] = useState<Note | null>(null);
  const [noteTitle, setNoteTitle] = useState("New note");
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Slides state
  const [isSlideDialogOpen, setIsSlideDialogOpen] = useState(false);
  const [slideQuery, setSlideQuery] = useState("");
  const [generatingSlide, setGeneratingSlide] = useState(false);
  const [viewingSlide, setViewingSlide] = useState<Slide | null>(null);
  const [isViewerOpen, setIsViewerOpen] = useState(false);

  const { notes, create, update, remove } = useNotes(initialNotes, params.notebookId);
  const { slides, create: createSlide, remove: removeSlide } = useSlides(initialSlides, params.notebookId);

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

  // Slides handlers
  const handleCreateSlide = () => {
    setSlideQuery("");
    setIsSlideDialogOpen(true);
  };

  const handleGenerateSlide = async () => {
    if (!slideQuery.trim()) {
      toast.error("Please enter a topic");
      return;
    }

    setGeneratingSlide(true);
    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/conversations/generate_slides/${params.notebookId}/${params.conversationId}`,
        {
          message_item: {
            id: crypto.randomUUID(),
            role: "user",
            parts: [{ type: "text", text: slideQuery }],
          },
          query: slideQuery,
          file_filters: [],
        },
        { headers: { "Content-Type": "application/json" } }
      );

      const htmlContent = res.data.response_message.parts[0].text;
      const newSlide = await createSlide(slideQuery.slice(0, 50) + "...", htmlContent);
      
      if (newSlide) {
        toast.success("Slides generated successfully!");
        setIsSlideDialogOpen(false);
        setSlideQuery("");
      }
    } catch (error) {
      console.error("Error generating presentation:", error);
      toast.error("Failed to generate presentation");
    } finally {
      setGeneratingSlide(false);
    }
  };

  const handleViewSlide = async (slide: Slide) => {
    const fullSlide = await getSlideById(slide.id);
    setViewingSlide(fullSlide);
    setIsViewerOpen(true);
  };

  const handleDeleteSlide = async (id: string) => {
    await removeSlide(id);
  };

  if (loading) return <Spinner variant="ring" className="w-4 h-4 animate-spin text-white" />;

  return (
    <div className="flex flex-col h-full">
      {/* Header with buttons */}
      <div className="flex justify-center items-center p-3 mb-2 sticky top-0 bg-white z-10 border-b rounded-t-xl">
        <div className="flex gap-2">
          <Button
            onClick={handleCreateSlide}
            className="flex items-center gap-2 px-3 py-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition"
          >
            <Presentation className="h-4 w-4" />
            <span className="text-sm">Presentation</span>
          </Button>
          <Button
            onClick={handleNewNote}
            className="flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition"
          >
            <StickyNote className="h-4 w-4"/>
            <span className="text-sm">Note</span>
          </Button>
        </div>
      </div>

      {/* Slides list */}
      {slides.length > 0 && (
        <>
          <div className="px-3 py-2">
            <h3 className="text-sm font-semibold text-gray-600 mb-2">Slides</h3>
          </div>
          <div className="flex-shrink-0 max-h-[30%] overflow-y-auto space-y-1 px-3">
            {slides.map((slide) => (
              <div
                key={slide.id}
                onClick={() => handleViewSlide(slide)}
                className="flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer transition hover:bg-red-50 border border-red-100"
              >
                <div className="flex items-center gap-2">
                  <Presentation className="h-4 w-4 text-red-500" />
                  <span className="text-gray-700 text-base font-medium">{slide.title ?? "Untitled Slides"}</span>
                </div>
                <div onClick={(e) => e.stopPropagation()}>
                  <ActionTrigger
                    className="text-gray-500"
                    apiLink="slides"
                    onDelete={() => handleDeleteSlide(slide.id)}
                    id={slide.id}
                  />
                </div>
              </div>
            ))}
          </div>
          <Separator className="my-2" />
        </>
      )}

      {/* Notes list */}
      <div className="px-3 py-2">
        <h3 className="text-sm font-semibold text-gray-600 mb-2">Notes</h3>
      </div>
      <div className="flex-1 overflow-y-auto space-y-1 px-3" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
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

      {/* Slide Generation Dialog */}
      <Dialog open={isSlideDialogOpen} onOpenChange={setIsSlideDialogOpen}>
        <DialogContent className="sm:max-w-[500px]" showCloseButton={false}>
          <div className="flex items-center justify-between">
            <DialogHeader>
              <DialogTitle>Generate Presentation</DialogTitle>
            </DialogHeader>
            <DialogClose asChild>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSlideDialogOpen(false)}
                className="opacity-70 w-7 h-7 cursor-pointer rounded-full hover:bg-gray-200 focus:outline-none focus:ring-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </DialogClose>
          </div>

          <div className="space-y-4 mt-4">
            <div>
              <label className="text-sm font-medium text-gray-700 mb-2 block">
                What topic would you like to create presentation about?
              </label>
              <Textarea
                placeholder="e.g., Introduction to Machine Learning, Python Basics, etc."
                value={slideQuery}
                onChange={(e) => setSlideQuery(e.target.value)}
                className="h-32"
              />
            </div>
          </div>

          <DialogFooter className="mt-6">
            <DialogClose asChild>
              <Button variant="outline" className="rounded-full cursor-pointer">
                Cancel
              </Button>
            </DialogClose>
            <Button
              onClick={handleGenerateSlide}
              disabled={generatingSlide}
              className="px-4 py-2 rounded-full bg-red-500 text-white hover:bg-red-600 cursor-pointer transition"
            >
              {generatingSlide ? (
                <>
                  <Spinner variant="ring" className="w-4 h-4 mr-2" />
                  Generating...
                </>
              ) : (
                "Generate Presentation"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Slides Viewer Dialog */}
      <Dialog open={isViewerOpen} onOpenChange={setIsViewerOpen}>
        <DialogContent className="max-w-[95vw] max-h-[95vh] p-0" showCloseButton={false}>
          {viewingSlide && (
            <SlidesViewer
              htmlContent={viewingSlide.html_content}
              onClose={() => setIsViewerOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
