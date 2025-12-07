'use client'

import { createContext, useContext, useState, ReactNode } from 'react'
import { SingleFile } from '@/schemas/fileStorage.interface'

interface FileContextType {
    files: SingleFile[]
    setFiles: React.Dispatch<React.SetStateAction<SingleFile[]>>
    getCheckedFileFilters: () => string[]
}

const FileContext = createContext<FileContextType | undefined>(undefined)

export function FileProvider({
    children,
    initialFiles
}: {
    children: ReactNode
    initialFiles: SingleFile[]
}) {
    const [files, setFiles] = useState<SingleFile[]>(initialFiles)

    // Returns an array of file titles for checked files
    // The backend uses partial filename matching
    const getCheckedFileFilters = (): string[] => {
        const checked = files.filter(f => f.checked).map(f => f.title)
        console.log('[FileContext] getCheckedFileFilters:', checked)
        return checked
    }

    return (
        <FileContext.Provider value={{ files, setFiles, getCheckedFileFilters }}>
            {children}
        </FileContext.Provider>
    )
}

export function useFileContext() {
    const context = useContext(FileContext)
    if (!context) {
        throw new Error('useFileContext must be used within a FileProvider')
    }
    return context
}
