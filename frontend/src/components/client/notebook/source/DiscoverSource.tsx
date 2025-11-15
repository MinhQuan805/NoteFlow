// DiscoverSource.tsx

'use client'

// React & icon
import { Search, X } from "lucide-react"
import { IoIosArrowBack } from "react-icons/io";

// shadcn UI
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { FaSearchPlus } from "react-icons/fa"
import { useState } from "react"
import { SingleFile } from "@/schemas/fileStorage.interface"
import { useParams } from "next/navigation"
import axios from "axios"
import { toast } from "react-toastify";

interface SingleLink {
    public_id: string
    title: string
    url: string
    format: string
    checked: boolean
    description: string
    created_at: Date | null
    updated_at: Date | null
}

export default function DiscoverSource(
                          { onImportComplete }: { onImportComplete?: (files: SingleFile[]) => void }) {
  const [showResult, setShowResult] = useState(false);
  const [sources, setSources] = useState<SingleLink[]>([])
  const params = useParams<{ notebookId: string, conversationId: string }>()
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)

  const resetImport = () => {
    setShowResult(false)
    setSources([])
    setQuery("")
    setOpen(false)
  }
  const handleDiscover = async () => {
    if (!query.trim()) return
    setLoading(true)
    try {
      const res = await axios.post("/api/search", { query })
      setSources(res.data)
      setShowResult(true)
    } catch (error) {
      console.error("Discover failed:", error)
    } finally {
      setLoading(false)
    }
  }
  const handleToggleFile = (id: string) => {
    setSources((prev) =>
      prev.map((f) => (f.public_id === id ? { ...f, checked: !f.checked } : f))
    )
  }

  const handleSelectAll = () => {
    const allChecked = sources.every((f) => f.checked)
    setSources((prev) => prev.map((f) => ({ ...f, checked: !allChecked })))
  }

  const handleImport = async () => {
    const sourcesImport = sources.filter(f => f.checked)
                                  .map(({ description, ...rest }) => rest); // Delete description before import to SingleFile
    try {
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/files/upload_url/${params.notebookId}`, sourcesImport)
      if (onImportComplete) onImportComplete(sourcesImport)
    } catch (err) {
      toast.error("Import failed")
    } finally {
      resetImport()
    }
  }
  const selectedCount = sources.filter((f) => f.checked).length

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          onClick={() => setOpen(true)}
          className="w-full h-10 flex items-center justify-center gap-1 rounded-3xl cursor-pointer border border-gray-300 hover:bg-gray-100"
        >
          <Search size={16} /> Discover
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-[700px] rounded-2xl" showCloseButton={false}>
        <div className="flex items-center justify-between">
          {showResult && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => { setShowResult(false); setQuery("") }}
              className="flex justify-center opacity-70 w-7 h-7 cursor-pointer
                        rounded-full hover:bg-gray-200 focus:outline-none focus:ring-0"
            >
              <IoIosArrowBack className="h-2 w-2" />
            </Button>
          )}
          <DialogHeader className="p-0">
            <DialogTitle>Discover New Sources</DialogTitle>
          </DialogHeader>
          <DialogClose asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={resetImport}
              className="opacity-70 w-7 h-7 cursor-pointer
                        rounded-full hover:bg-gray-200 focus:outline-none focus:ring-0"
            >
              <X className="h-2 w-2" />
            </Button>
          </DialogClose>
        </div>

        {/* Step 1: Enter your topic */}
        {!showResult ? (
          <div className="space-y-4 mt-2">
            <div className="flex flex-col items-center">
              <div className="flex justify-center items-center bg-blue-100 mt-2 mb-2 w-12 h-12 rounded-full">
                <FaSearchPlus className="text-sky-600 w-5 h-5" />
              </div>
              <Label className="font-medium text-center text-lg mb-2">
                What are you interested in?
              </Label>
            </div>

            <Textarea
              className="mt-2 h-28"
              placeholder="Enter the topics you’d like to explore..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />

            <div className="flex justify-end">
              <Button
                className="rounded-full cursor-pointer px-5"
                onClick={handleDiscover}
                disabled={loading}
              >
                {loading ? "Discovering..." : "Discover"}
              </Button>
            </div>
          </div>
        ) : (
          /* Step 2: Display result */
          <div className="mt-3">

            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
              <div className="flex justify-between items-center mb-2 max-h-[400px] px-3 py-2">
                <Label className="font-medium">Select all sources</Label>
                <Checkbox
                  checked={sources.every((f) => f.checked)}
                  onCheckedChange={handleSelectAll}
                  className="cursor-pointer"
                />
              </div>
              {sources.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between border 
                            rounded-xl px-3 py-2 hover:bg-gray-50 transition w-full"
                >
                  <div className="flex flex-col w-[80%]">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm font-medium text-blue-600 hover:underline max-w-full line-clamp-1"
                    >
                      {item.title}
                    </a>
                    <p className="text-xs text-gray-600 max-w-full line-clamp-1">{item.description}</p>
                  </div>
                  <Checkbox
                    checked={item.checked}
                    onCheckedChange={() => handleToggleFile(item.public_id)}
                    className="cursor-pointer"
                  />
                </div>
              ))}
            </div>

            <div className="flex justify-between items-center mt-4 border-t pt-3">
              <p className="text-sm text-gray-600">
                Selected {selectedCount} sources
              </p>
              <Button className="rounded-full px-5 cursor-pointer" onClick={handleImport}>Import</Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
