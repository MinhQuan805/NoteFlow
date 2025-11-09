import axios from "axios";
import { SingleFile } from "@/schemas/fileStorage.interface";

export function useFileSelect(notebookId: string, files: SingleFile[], setFiles: React.Dispatch<React.SetStateAction<SingleFile[]>>) {

  const toggleSelectFile = async (fileId: string, currentChecked: boolean) => {
    try {
      await axios.patch(
        `${process.env.NEXT_PUBLIC_API_URL}/files/update_checked/${notebookId}/${fileId}?checked=${!currentChecked}`
      );

      setFiles(prev =>
        prev.map(file =>
          file.public_id === fileId
            ? { ...file, checked: !currentChecked }
            : file
        )
      );
    } catch (error) {
      console.error("Failed to update checked:", error);
    }
  };

  const toggleSelectAll = async () => {
    const allSelected = files.every(f => f.checked);
    const updatedFiles = await Promise.all(
      files.map(async (f) => {
        try {
          await axios.patch(
            `${process.env.NEXT_PUBLIC_API_URL}/files/update_checked/${notebookId}/${f.public_id}?checked=${!allSelected}`
          );
          return { ...f, checked: !allSelected };
        } catch {
          return f;
        }
      })
    );
    setFiles(updatedFiles);
  };

  return { toggleSelectFile, toggleSelectAll };
}
