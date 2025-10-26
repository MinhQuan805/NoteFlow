'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import ActionTrigger from '../../ActionTrigger'
import { Checkbox } from "@/components/ui/checkbox"
import { Download, ExternalLink, Plus} from 'lucide-react'
import { Input } from '@/components/ui/input'
import axios from 'axios'
import { SingleFile } from '@/schemas/fileStorage.interface'
import { Spinner } from '@/components/ui/shadcn-io/spinner/index';
import DiscoverSources from './DiscoverSources'
import { useFileSelect } from '@/hooks/useFileSelect'

const icons = [
  { format: 'pdf', source: '/icon/format/pdf.png'},
  { format: 'docx', source: '/icon/format/docx.png'},
  { format: 'pptx', source: '/icon/format/pptx.png'},
  { format: 'txt', source: '/icon/format/txt.png'},
  { format: 'md', source: '/icon/format/md.png'},
  { format: 'csv', source: '/icon/format/csv.png'},
  { format: 'json', source: '/icon/format/json.png'},
  { format: 'url', source: '/icon/format/url.png'},
]

export default function SourceFileUpload() {
  const [actionOpen, setActionOpen] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  
  const [files, setFiles] = useState<SingleFile[]>([])
  
  const [loadingAdd, setLoadingAdd] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState<string | null>(null)

  const params = useParams<{ noteId: string, conversationId: string }>()
  const { toggleSelectFile, toggleSelectAll } = useFileSelect(params.noteId, files, setFiles)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/files/${params.noteId}`)
        setFiles(res.data)
      } catch (error) {
        console.error("Failed to fetch files:", error);
      }
      
    }
    fetchData()
  }, [params.noteId])
  
  const handleAddFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const formData = new FormData();
    Array.from(e.target.files).forEach(file => formData.append("files", file))


    try {
      setLoadingAdd(true)
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/files/upload_files/${params.noteId}`,
        formData)
      setFiles([...res.data, ...files])
    } catch (err) {
      console.log(err)
    } finally {
      setLoadingAdd(false)
    }
  }

  // Download File
  const handleDownloadFile = async (public_id: string) => {
    setLoadingDownload(public_id);
    const link = document.createElement('a');
    link.href = `${process.env.NEXT_PUBLIC_API_URL}/files/download_file/${params.noteId}/${public_id}`;
    link.setAttribute('download', '');
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    link.remove();

    // Simulator "Loading"
    setTimeout(() => setLoadingDownload(null), 1000);
  };

  const handleDeleteFile = async (public_id: string, format: string) => {
    try {
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/files/delete/${params.noteId}/${public_id}/${format}`);
      
      // Filter remained files
      const updatedFiles = files.filter(c => c.public_id !== public_id);
      setFiles(updatedFiles);

    } catch (error) {
      console.error("Failed to delete file:", error);
    }
  }


  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center p-3 mb-1 sticky top-0 z-10 border-b">
        <p className="text-lg font-semibold text-gray-800">Source</p>
      </div>

      <div className="flex flex-row space-x-2 p-2">
        <label className="w-1/2 h-10 flex font-semibold justify-center items-center gap-1 px-3 py-1.5 text-sm rounded-3xl cursor-pointer border border-gray-300 hover:bg-gray-100">
          <Input type="file" className="hidden" multiple onChange={handleAddFile}/>
          {loadingAdd ? (
            <Spinner variant="ring" className="w-4 h-4" />
          ) : (
            <>
              <Plus size={16} />Add
            </>
          )}
        </label>
        <div className="w-1/2">
          <DiscoverSources onImportComplete={(newFiles) => setFiles(prev => [...newFiles, ...prev])} />
        </div>
      </div>

      <div className="flex justify-between items-center px-4 py-1 bg-white z-10">
        <span className="text-sm text-gray-700">Select all sources</span>
        <Checkbox className="cursor-pointer" checked={files.length > 0 && files.every(f => f.checked)} onCheckedChange={toggleSelectAll}/>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1 p-1" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
        {files.map(file => (
          <div
            key={file.public_id}
            onClick={() => { setActionOpen(true); setSelectedId(file.public_id) }}
            className={`flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer transition ${
              selectedId === file.public_id ? 'bg-gray-100' : 'hover:bg-gray-50'
            }`}
          >
            <div className="flex items-center space-x-2 w-3/4 overflow-hidden">
              <div className="w-5 h-5 flex-shrink-0">
                {(actionOpen && file.public_id === selectedId)
                  ? <ActionTrigger className="text-gray-500 hover:bg-gray-200 rounded-full" 
                                  apiLink={`files`} 
                                  onDelete={() => handleDeleteFile(file.public_id, file.format)}
                                  id={`${params.noteId}/${file.public_id}/${file.format}`}
                    />
                  : <img src={icons.find(icon => icon.format === file.format)?.source || '/icon/format/other.png'} 
                          alt="file icon" className="w-5 h-5"/>}
              </div>
              <span className="text-gray-700 text-sm truncate w-full">{file.title}</span>
            </div>
            <div className="flex items-center gap-3">
                <div className="flex items-center justify-center hover:bg-gray-200 rounded-full w-7 h-7">
                  {file.format !== "url" ? (
                    // Display Download Button For File
                    loadingDownload === file.public_id ? (
                      <Spinner variant="ring" className="w-4 h-4" />
                    ) : (
                      <Download
                        className="text-gray-500 w-5 h-5"
                        onClick={() => handleDownloadFile(file.public_id)}
                      />
                    )
                  ) : (
                    // Display Open Link Button For File
                    <ExternalLink
                      className="text-gray-500 w-5 h-5"
                      onClick={() => window.open(file.url, "_blank")}
                    />
                  )}
                </div>

              <Checkbox
                className="cursor-pointer"
                checked={file.checked}
                onCheckedChange={() => toggleSelectFile(file.public_id, file.checked)}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
