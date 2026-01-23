import { Slide } from "@/schemas/slide.interface";
import { sendRequest } from "@/utils/api";
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getAllSlides(notebookId: string) {
    return sendRequest<Slide[]>({
        url: `${API_URL}/slides/getAll/${notebookId}`,
        method: "GET",
    });
}

export const getSlideById = async (id: string) => {
    const res = await axios.get(`${API_URL}/slides/${id}`);
    return res.data;
};

export const createSlide = async (slide: Partial<Slide>) => {
    const res = await axios.post(`${API_URL}/slides`, slide);
    return res.data;
};

export const updateSlide = async (id: string, data: Partial<Slide>) => {
    const res = await axios.patch(`${API_URL}/slides/${id}`, data);
    return res.data;
};

export const deleteSlide = async (id: string) => {
    await axios.delete(`${API_URL}/slides/delete/${id}`);
};
