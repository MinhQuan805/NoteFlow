export interface Slide {
    id: string;
    title: string;
    notebookId: string;
    html_content: string;
    created_at: Date;
    updated_at: Date;
}

export interface SlideListItem {
    id: string;
    title: string;
}
