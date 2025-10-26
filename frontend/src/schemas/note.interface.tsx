export interface Styles {
  [key: string]: boolean;
}

export interface StyledText {
  type: "text";
  text: string;
  styles?: Styles;
}

export interface Link {
  type: "link";
  content: StyledText[];
  href: string;
}

export interface CustomInlineContent {
  type: string;
  content?: StyledText[];
  props?: {
    [key: string]: boolean | number | string;
  };
}

export type InlineContent = Link | StyledText | CustomInlineContent;

export interface TableContent {
  rows?: StyledText[][];
}

export interface Note {
  id: string;
  type: string;
  props?: {
    [key: string]: boolean | number | string;
  };
  content?: InlineContent[] | TableContent;
  children: Note[];
}

export interface NoteContainer {
  title: string;
  notebookId: string;
  blocks: Note[];
  created_at: Date
  updated_at: Date;
}
