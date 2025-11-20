import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import axios from "axios";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const updateTitle = async (apiLink: string) => {
  try {
    await axios.patch(
      `${process.env.NEXT_PUBLIC_API_URL}/${apiLink}`
    );
  } catch (err) {
    console.error('Failed to update title', err);
  }
};


