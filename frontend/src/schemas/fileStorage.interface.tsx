export interface SingleFile {
    public_id: string
    title: string
    url: string
    format: string
    content?: string
    embedding?: number[]
    checked: boolean
    created_at: Date | null
    updated_at: Date | null
}

export interface FileListStorage {
    notebookId: string
    file_list: SingleFile[]
    created_at: Date
    updated_at: Date
}