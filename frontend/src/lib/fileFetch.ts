import { SingleFile } from "@/schemas/fileStorage.interface";
import { sendRequest } from "@/utils/api";

export async function getAllFiles(notebookId: string) {
  return sendRequest<SingleFile[]>({
    url: `${process.env.NEXT_PUBLIC_API_URL}/files/${notebookId}`,
    method: "GET",
  });
}
