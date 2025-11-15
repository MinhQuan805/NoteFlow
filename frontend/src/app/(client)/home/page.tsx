"use client"

import * as React from "react"
import CreateNote from "./CreateNote"
import { useState, useEffect } from 'react'
import axios from 'axios'
import ActionTrigger from "@/components/client/ActionTrigger"
import { Notebook } from "@/schemas/notebook.interface"
import { toast } from "react-toastify"
import { useRouter } from "next/navigation"

export default function Home() {
  
  const router = useRouter()
  const [notebooks, setNotebooks] = useState<Notebook[]>([])
  const [loading, setLoading] = useState(true)


  useEffect(() => {
      const fetchData = async () => {
        try {
          setLoading(true)
          const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/notebooks`)
          setNotebooks(res.data)
        } catch (err) {
          toast.error("Failed to load notes")
        } finally {
          setLoading(false)
        }
      }
      fetchData()
    }, [])
  
  const handleDelete = async (id: string, idAvatar: string) => {
    try {
      if (!idAvatar) {
        idAvatar = "noAvatar"
      }
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL}/notebooks/delete/${id}/${idAvatar}`);
      
      // Filter remained notebook
      const updatedNotebooks = notebooks.filter(c => c.id !== id);
      setNotebooks(updatedNotebooks);

    } catch (error) {
      toast.error("Failed to delete conversation");
    }
  };
  const handleLearn = async (notebookId: string) => {
    setLoading(true)
    try {
      const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/notebooks/${notebookId}`)
      router.push(`/notebook/${notebookId}/${res.data.conversationId}`)
    } catch (err: any) {
      console.error(err)
      toast.error("Cannot open notebook. Please try again later.")
    } finally {
      setLoading(false)
    }
  }

  if (notebooks.length === 0) {
    return (
      <div className="flex items-center justify-center w-full h-screen">
        <CreateNote/>
      </div>
    )
  }

  return (
    <div className="p-8 w-full">
      <h1 className="text-3xl font-bold mb-6">Your Notebooks 📔</h1>
      
      <div className="flex flex-wrap gap-6 justify-center"> 
        <CreateNote/>
        
        {notebooks.map((notebook) => (
            <div
              className="relative overflow-hidden flex flex-col items-center justify-center 
                        w-70 h-52 p-8 rounded-xl cursor-pointer 
                        transition-shadow bg-cover bg-center"
              style={
                notebook.avatar
                  ? { backgroundImage: `url(${notebook.avatar})` }
                  : { backgroundColor: notebook.bgcolor }
              }
              onClick={() => handleLearn(notebook.id)}
            >
              {/* Dark gradient overlay at the bottom half */}
              {notebook.avatar && (
                <div className="absolute bottom-0 left-0 w-full h-1/2 bg-gradient-to-t from-black/100 to-transparent" />
              )}
              <div
                onClick={
                  (e) => e.stopPropagation()
                }
              >
                <ActionTrigger
                  className="text-gray-500"
                  apiLink={`notebooks`}
                  onDelete={() => handleDelete(notebook.id, notebook.idAvatar)}
                  id={notebook.id}
                />
              </div>
              <div className={notebook.avatar ? "text-white" : "text-gray-700"}>
              <h3 className="text-2xl font-bold mt-4 
                            ">
                {notebook.title}
              </h3>
              
              <p className="text-sm mt-1">
                {new Date(notebook.updated_at).toLocaleDateString()}
              </p>
              </div>
            </div>
          ))}
      </div>
    </div>
  )
}

