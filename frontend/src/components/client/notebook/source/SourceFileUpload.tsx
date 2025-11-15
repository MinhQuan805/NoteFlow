// // SourceFileUpload.tsx

'use client'
import { useState } from 'react'
import { useParams } from 'next/navigation'
import { Checkbox } from '@/components/ui/checkbox'
import { Download, ExternalLink, Plus } from 'lucide-react'
import { Spinner } from '@/components/ui/shadcn-io/spinner'
import DiscoverSource from './DiscoverSource'
import ActionTrigger from '@/components/client/ActionTrigger'
import { useSource } from '@/hooks/useSource'
import { useFileSelect } from '@/hooks/useFileSelect'
import { SingleFile } from '@/schemas/fileStorage.interface'
import AddSource from './AddSource'

const icons = [
  { format: 'pdf', source: '/icon/format/pdf.png' },
  { format: 'docx', source: '/icon/format/docx.png' },
  { format: 'pptx', source: '/icon/format/pptx.png' },
  { format: 'txt', source: '/icon/format/txt.png' },
  { format: 'md', source: '/icon/format/md.png' },
  { format: 'csv', source: '/icon/format/csv.png' },
  { format: 'json', source: '/icon/format/json.png' },
  { format: 'url', source: '/icon/format/url.png' },
]

export default function SourceFileUpload({ initialFiles }: { initialFiles: SingleFile[] }) {
  const params = useParams<{ notebookId: string }>()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [actionOpen, setActionOpen] = useState(false)

  const { files, addFile, deleteFile, 
          downloadFile, setFiles, loadingAdd, loadingDownload 
        } = useSource(initialFiles, params.notebookId)
        
  const { toggleSelectFile, toggleSelectAll } = useFileSelect(params.notebookId, files, setFiles)

  return (
    <div className="flex flex-col h-full">
      <div className="flex justify-between items-center p-3 mb-1 sticky top-0 z-10 border-b">
        <p className="text-lg font-semibold text-gray-800">Source</p>
      </div>

      <div className="flex flex-row space-x-2 p-2">
        <div className="w-1/2">
          <AddSource onAdd={addFile} loading={loadingAdd} />
        </div>
        <div className="w-1/2">
          <DiscoverSource onImportComplete={(newFiles) => setFiles(prev => [...newFiles, ...prev])} />
        </div>
      </div>

      <div className="flex justify-between items-center px-4 py-1 bg-white z-10">
        <span className="text-sm text-gray-700">Select all sources</span>
        <Checkbox checked={files.length > 0 && files.every(f => f.checked)} onCheckedChange={toggleSelectAll} />
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
              <div className="flex items-center flex-shrink-0">
                {(actionOpen && file.public_id === selectedId)
                  ? <ActionTrigger
                      className="text-gray-500 hover:bg-gray-200 rounded-full"
                      apiLink={`files`}
                      onDelete={() => deleteFile(file.public_id, file.format)}
                      id={`${params.notebookId}/${file.public_id}/${file.format}`}
                    />
                  : <img src={icons.find(i => i.format === file.format)?.source || '/icon/format/other.png'} alt="file icon" className="w-5 h-5" />}
              </div>
              <span className="text-gray-700 text-sm truncate w-full">{file.title}</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center hover:bg-gray-200 rounded-full w-7 h-7">
                {file.format !== "url" ? (
                  loadingDownload === file.public_id ? (
                    <Spinner variant="ring" className="w-4 h-4" />
                  ) : (
                    <Download className="text-gray-500 w-5 h-5" onClick={() => downloadFile(file.public_id)} />
                  )
                ) : (
                  <ExternalLink className="text-gray-500 w-5 h-5" onClick={() => window.open(file.url, "_blank")} />
                )}
              </div>
              <Checkbox checked={file.checked} onCheckedChange={() => toggleSelectFile(file.public_id, file.checked)} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}