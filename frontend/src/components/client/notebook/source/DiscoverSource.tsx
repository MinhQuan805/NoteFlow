// DiscoverSource.tsx

"use client";

// React & icon
import { Search, X } from "lucide-react";
import { IoIosArrowBack } from "react-icons/io";

// shadcn UI
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { FaSearchPlus } from "react-icons/fa";
import { useState } from "react";
import { SingleFile } from "@/schemas/fileStorage.interface";
import { useParams } from "next/navigation";
import axios from "axios";
import { toast } from "react-toastify";

interface SingleLink {
  public_id: string;
  title: string;
  url: string;
  format: string;
  checked: boolean;
  description: string;
  created_at: Date | null;
  updated_at: Date | null;
}

export default function DiscoverSource({
  onImportComplete,
}: {
  onImportComplete?: (files: SingleFile[]) => void;
}) {
  const [showResult, setShowResult] = useState(false);
  const [sources, setSources] = useState<SingleLink[]>([]);
  const params = useParams<{ notebookId: string; conversationId: string }>();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  const resetImport = () => {
    setShowResult(false);
    setSources([]);
    setQuery("");
    setOpen(false);
  };
  const handleDiscover = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await axios.post("/api/search", { query });
      setSources(res.data);
      setShowResult(true);
    } catch (error) {
      console.error("Discover failed:", error);
    } finally {
      setLoading(false);
    }
  };
  const handleToggleFile = (id: string) => {
    setSources((prev) =>
      prev.map((f) => (f.public_id === id ? { ...f, checked: !f.checked } : f)),
    );
  };

  const handleSelectAll = () => {
    const allChecked = sources.every((f) => f.checked);
    setSources((prev) => prev.map((f) => ({ ...f, checked: !allChecked })));
  };

  const handleImport = async () => {
    setLoading(true);
    const sourcesImport = sources
      .filter((f) => f.checked)
      .map(({ description, ...rest }) => rest); // Delete description before import to SingleFile
    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/files/upload_url/${params.notebookId}`,
        sourcesImport,
      );
      if (onImportComplete) onImportComplete(sourcesImport);
    } catch {
      toast.error("Import failed");
    } finally {
      resetImport();
      setLoading(false);
    }
  };
  const selectedCount = sources.filter((f) => f.checked).length;

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          onClick={() => setOpen(true)}
          className="flex h-10 w-full cursor-pointer items-center justify-center gap-1 rounded-3xl border border-gray-300 hover:bg-gray-100"
        >
          <Search size={16} /> Discover
        </Button>
      </DialogTrigger>

      <DialogContent
        className="rounded-2xl sm:max-w-[700px]"
        showCloseButton={false}
      >
        <div className="flex items-center justify-between">
          {showResult && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                setShowResult(false);
                setQuery("");
              }}
              className="flex h-7 w-7 cursor-pointer justify-center rounded-full opacity-70 hover:bg-gray-200 focus:outline-none focus:ring-0"
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
              className="h-7 w-7 cursor-pointer rounded-full opacity-70 hover:bg-gray-200 focus:outline-none focus:ring-0"
            >
              <X className="h-2 w-2" />
            </Button>
          </DialogClose>
        </div>

        {/* Step 1: Enter your topic */}
        {!showResult ? (
          <div className="mt-2 space-y-4">
            <div className="flex flex-col items-center">
              <div className="mb-2 mt-2 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                <FaSearchPlus className="h-5 w-5 text-sky-600" />
              </div>
              <Label className="mb-2 text-center text-lg font-medium">
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
                className="cursor-pointer rounded-full px-5"
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
            <div className="max-h-[400px] space-y-3 overflow-y-auto pr-2">
              <div className="mb-2 flex max-h-[400px] items-center justify-between px-3 py-2">
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
                  className="flex w-full items-center justify-between rounded-xl border px-3 py-2 transition hover:bg-gray-50"
                >
                  <div className="flex w-[80%] flex-col">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="line-clamp-1 max-w-full text-sm font-medium text-blue-600 hover:underline"
                    >
                      {item.title}
                    </a>
                    <p className="line-clamp-1 max-w-full text-xs text-gray-600">
                      {item.description}
                    </p>
                  </div>
                  <Checkbox
                    checked={item.checked}
                    onCheckedChange={() => handleToggleFile(item.public_id)}
                    className="cursor-pointer"
                  />
                </div>
              ))}
            </div>

            <div className="mt-4 flex items-center justify-between border-t pt-3">
              <p className="text-sm text-gray-600">
                Selected {selectedCount} sources
              </p>
              <Button
                className="cursor-pointer rounded-full px-5"
                onClick={handleImport}
                disabled={loading}
              >
                {loading ? "Importing..." : "Import"}
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
