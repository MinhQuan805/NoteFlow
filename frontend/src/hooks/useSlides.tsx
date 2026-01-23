import { useState } from 'react';
import { Slide } from '@/schemas/slide.interface';
import * as slideApi from '@/lib/api/slideApi';
import { toast } from 'react-toastify';

export function useSlides(initialSlides: Slide[], notebookId: string) {
    const [slides, setSlides] = useState(initialSlides);

    const create = async (title: string, html_content: string) => {
        const newSlide = {
            notebookId: notebookId,
            title: title,
            html_content: html_content,
        };

        try {
            const newRes = await slideApi.createSlide(newSlide);
            setSlides([newRes, ...slides]);
            return newRes;
        } catch {
            toast.error("Failed to create presentation");
            return null;
        }
    };

    const update = async (id: string, title: string, html_content: string) => {
        try {
            const data = { title, html_content };
            const updatedSlide = await slideApi.updateSlide(id, data);
            setSlides(prev => [updatedSlide, ...prev.filter(s => s.id !== id)]);
            return updatedSlide;
        } catch {
            toast.error("Failed to update slide");
            return null;
        }
    };

    const remove = async (id: string) => {
        try {
            await slideApi.deleteSlide(id);
            setSlides(prev => prev.filter(s => s.id !== id));
        } catch {
            toast.error("Failed to delete slide");
        }
    };

    return { slides, create, update, remove, setSlides };
}
