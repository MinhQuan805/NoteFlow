// fileApi.ts

import { SingleFile } from "@/schemas/fileStorage.interface";
import { sendRequest } from "@/utils/api";
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL

export async function getAllFiles(notebookId: string) {
  return sendRequest<SingleFile[]>({
    url: `${API_URL}/files/${notebookId}`,
    method: "GET",
  });
}

export const uploadFiles = async (notebookId: string, formData: FormData) => {
  const res = await axios.post(`${API_URL}/files/upload_files/${notebookId}`, formData)
  return res.data.uploaded_files as SingleFile[]
}

export const downloadFile = async (notebookId: string, public_id: string) => {
  const link = document.createElement('a')
  link.href = `${API_URL}/files/download_file/${notebookId}/${public_id}`
  link.setAttribute('download', '')
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  link.remove()
}

export const deleteFile = async (notebookId: string, public_id: string, format: string) => {
  await axios.delete(`${API_URL}/files/delete/${notebookId}/${public_id}/${format}`)
}
