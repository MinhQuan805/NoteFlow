"use client"

// React & Next.js
import * as React from "react"
import { useRouter } from "next/navigation"

// Icons
import { LockIcon, Plus } from "lucide-react"
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
  DialogContent,
  DialogDescription,
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

// Main component to center the drawer trigger
export default function CreateNote() {
  return (
    <div className="flex items-center justify-center w-full h-screen">
      <DrawerResponsive />
    </div>
  )
}


// Drawer component with trigger card and modal dialog
function DrawerResponsive() {
  const [open, setOpen] = React.useState(false) // state to control dialog open/close

  // Trigger card for creating a new note
  const triggerCard = (
    <div className="flex flex-col items-center justify-center w-60 h-48 p-8 border border-gray-200 rounded-xl cursor-pointer hover:shadow-md transition-shadow">
      <div className="flex items-center justify-center w-12 h-12 bg-indigo-50 rounded-full">
        <Plus className="w-6 h-6 text-indigo-500" strokeWidth={2.5} />
      </div>
      <p className="mt-3 font-medium text-gray-700">Create a new notebook</p>
    </div>
  )

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {/* Clicking the card opens the dialog */}
      <DialogTrigger asChild>{triggerCard}</DialogTrigger>

      {/* Dialog content */}
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create a New Notebook</DialogTitle>
          <DialogDescription>
            Enter the information for your notebook below.
          </DialogDescription>
        </DialogHeader>

        {/* Form for notebook creation */}
        <NoteForm />
      </DialogContent>
    </Dialog>
  )
}

// Zod schema for form validation
const FormSchema = z.object({
  title: z.string().min(1, { message: "Please enter a title" }),
  password: z.string().optional(),
  avatar: z.string().optional(),
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
      password: "",
      avatar: ""
    },
  })

  // Handle form submission
  const onSubmit = async (data: z.infer<typeof FormSchema>) => {
    setLoading(true)
    try {
      // Send POST request to create a new notebook
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

          {/* Password Field (optional) */}
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password (optional)</FormLabel>
                <FormControl>
                  <div className="relative">
                    <LockIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      type="password"
                      placeholder="Enter password"
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

          {/* SUBMIT BUTTON */}
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