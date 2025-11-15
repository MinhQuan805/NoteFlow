import { useState } from 'react'
import * as fileApi from '@/lib/fileApi'
import { SingleFile } from '@/schemas/fileStorage.interface'

export function useSource(initialFiles: SingleFile[], notebookId: string) {
  const [files, setFiles] = useState(initialFiles)
  const [loadingAdd, setLoadingAdd] = useState(false)
  const [loadingDownload, setLoadingDownload] = useState<string | null>(null)

  const addFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return
    const formData = new FormData()
    Array.from(e.target.files).forEach(file => formData.append("files", file))

    try {
      setLoadingAdd(true)
      const res = await fileApi.uploadFiles(notebookId, formData)
      setFiles([...res, ...files])
    } finally {
      setLoadingAdd(false)
    }
  }

  const deleteFile = async (public_id: string, format: string) => {
    try {
      await fileApi.deleteFile(notebookId, public_id, format)
      setFiles(prev => prev.filter(f => f.public_id !== public_id))
    } catch (err) {
      console.error("Failed to delete file:", err)
    }
  }

  const downloadFile = async (public_id: string) => {
    setLoadingDownload(public_id)
    await fileApi.downloadFile(notebookId, public_id)
    setTimeout(() => setLoadingDownload(null), 1000)
  }

  
  return { files, addFile, deleteFile, downloadFile, setFiles, loadingAdd, loadingDownload }
}
