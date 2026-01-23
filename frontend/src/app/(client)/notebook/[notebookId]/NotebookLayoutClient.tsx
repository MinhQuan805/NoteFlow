'use client'

import { FileProvider } from '@/contexts/FileContext'
import { SingleFile } from '@/schemas/fileStorage.interface'

export default function NotebookLayoutClient({
    children,
    initialFiles,
}: {
    children: React.ReactNode
    initialFiles: SingleFile[]
}) {
    return (
        <FileProvider initialFiles={initialFiles}>
            {children}
        </FileProvider>
    )
}
