"use client"

// React & Next.js
import * as React from "react"
import { useRouter } from "next/navigation"

// Icons
import { Plus, X } from "lucide-react"
import { CiStickyNote } from "react-icons/ci"

// HTTP & Validation
import axios from "axios"
import * as z from "zod"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

// UI Components
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Spinner } from '@/components/ui/shadcn-io/spinner/index';
import { toast } from "react-toastify"


// Drawer component with trigger card and modal dialog
export default function CreateNote() {
  const [open, setOpen] = React.useState(false) // state to control dialog open/close

  // Trigger card for creating a new note
  const triggerCard = (
    <div className="flex flex-col items-center justify-center w-70 h-52 p-8 border border-gray-200 rounded-xl cursor-pointer hover:shadow-md transition-shadow">
      <div className="flex items-center justify-center w-14 h-14 bg-indigo-50 rounded-full">
        <Plus className="w-7 h-7 text-indigo-500" strokeWidth={2.5} />
      </div>
      <p className="mt-3 font-medium text-gray-700 text-lg">Create a new notebook</p>
    </div>
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {/* Clicking the card opens the dialog */}
      <DialogTrigger asChild>{triggerCard}</DialogTrigger>

      {/* Dialog content */}
      <DialogContent className="sm:max-w-[425px]" showCloseButton={false}>
        <div className="flex items-center justify-between">
          <DialogHeader>
            <DialogTitle>Create a New Notebook</DialogTitle>
          </DialogHeader>
          <DialogClose asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                setOpen(false);
              }}
              className="opacity-70 w-7 h-7 cursor-pointer
                        rounded-full hover:bg-gray-200 focus:outline-none focus:ring-0"
            >
              <X className="h-2 w-2" />
            </Button>
          </DialogClose>
        </div>
        {/* Form for notebook creation */}
        <NoteForm />
      </DialogContent>
    </Dialog>
  )
}

// Zod schema for form validation
const FormSchema = z.object({
  title: z.string().min(1, { message: "Please enter a title" }),
  avatar: z.string().optional(),
  bgcolor: z.string().optional()
})

// Notebook creation form component
function NoteForm() {
  const router = useRouter()
  const [loading, setLoading] = React.useState(false)


  // React Hook Form with Zod validation
  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      title: "",
      avatar: "",
      bgcolor: ""
    },
  })

  // Handle form submission
  const randomColor = ["#fecaca", "#fed7aa", "#fde68a", "#dbeafe", 
                      "#fef08a", "#d9f99d", "#86efac", "#6ee7b7", 
                      "#5eead4", "#7dd3fc", "#82f967"
                    ];


  const onSubmit = async (data: z.infer<typeof FormSchema>) => {
    setLoading(true)
    try {
      // Send POST request to create a new notebook

      // Create random background color if it doesn't have avatar
      if (data.avatar === "") {
        const random = Math.floor(Math.random() * randomColor.length);
        data.bgcolor = randomColor[random];
        console.log(data);
      }
      const resNote  = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/notebooks/create`, data)
      toast.success("Notebook created successfully!")
      router.push(`/notebook/${resNote.data.notebookId}/${resNote.data.conversationId}`)
    } catch (err: any) {
      console.error(err)
      toast.error("Cannot create notebook. Please try again later.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="grid items-start gap-6 w-full max-w-sm"
        >
          {/* Title Field */}
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Title</FormLabel>
                <FormControl>
                  <div className="relative">
                    {/* Icon inside input */}
                    <CiStickyNote className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Enter title"
                      className="pl-10"
                      {...field}
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Avatar Field (optional) */}
          <FormField
            control={form.control}
            name="avatar"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Avatar</FormLabel>
                <FormControl>
                  <Input
                    type="text"
                    placeholder="Paste image URL or leave empty"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Submit Button */}
          <Button type="submit" disabled={loading} className="flex items-center justify-center gap-2 cursor-pointer">
            {loading ? (
              <>
                <Spinner variant="ring" className="w-4 h-4 animate-spin text-white" />
                Creating...
              </>
            ) : (
              "Create"
            )}
          </Button>
        </form>
      </Form>
    </>
  )
}