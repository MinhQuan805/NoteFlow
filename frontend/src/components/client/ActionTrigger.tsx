"use client"
import { useState } from "react"
import { MoreVertical } from "lucide-react"
import { FaPen, FaTrash } from "react-icons/fa"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { updateTitle } from "@/lib/actionApi"
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import axios from "axios";

interface ActionProps {
  className?: string
  apiLink?: string
  onDelete: () => Promise<void>
  id?: string
}

interface RenameDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  apiLink?: string
  id?: string
}

const renameSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }).max(35, { message: "Title cannot exceed 35 characters" })
})

function RenameDialog({ open, onOpenChange, apiLink, id}: RenameDialogProps) {

  const { register, handleSubmit, formState: { errors }, reset } = useForm<z.infer<typeof renameSchema>>({
    resolver: zodResolver(renameSchema),
    defaultValues: { title: "" }
  });


  return (
    
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="w-100">
        <DialogHeader>
          <DialogTitle>Rename Item</DialogTitle>
          <DialogDescription>Enter a new name for this item.</DialogDescription>
        </DialogHeader>
        <form
          onSubmit={handleSubmit(async (data) => {
            await updateTitle(`${apiLink}/update_title/${id}?title=${data.title}`);
            reset();
            onOpenChange(false);
            window.location.reload();
          })}
        >
          <Input {...register("title")} placeholder="New name" className="mt-2" />
          {errors.title && <p className="text-red-500 mt-1">{errors.title.message}</p>}
          <DialogFooter className="mt-4 flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                reset();
                onOpenChange(false);
              }}
            >
              Cancel
            </Button>
            <Button type="submit">Rename</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>

  )
}

// Component chính
export default function ActionTrigger({ className, apiLink, onDelete, id}: ActionProps) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <div className="w-6 h-6 flex items-center justify-center rounded-full hover:bg-gray-200 transition-colors">
            <MoreVertical className={className} size={20} />
          </div>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-30">
          {
            apiLink !== "notes" && (
              <DropdownMenuItem
                onClick={() => setOpen(true)}
                className="cursor-pointer flex items-center gap-2"
              >
                <FaPen /> <p>Rename</p>
              </DropdownMenuItem>
            )
          }
          <DropdownMenuItem
            onClick={onDelete}
            className="cursor-pointer flex items-center gap-2"
          >
            <FaTrash /> <p>Delete</p>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <RenameDialog
        open={open}
        onOpenChange={setOpen}
        apiLink={apiLink}
        id={id}
      />
    </>
  )
}
