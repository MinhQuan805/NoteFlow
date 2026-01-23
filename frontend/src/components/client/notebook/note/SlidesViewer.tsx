"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, X } from "lucide-react";

interface SlidesViewerProps {
    htmlContent: string;
    onClose?: () => void;
}

export default function SlidesViewer({ htmlContent, onClose }: SlidesViewerProps) {
    const [currentSlide, setCurrentSlide] = useState(0);
    const [totalSlides, setTotalSlides] = useState(0);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Extract and count slides from HTML
    useEffect(() => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, "text/html");
        const slides = doc.querySelectorAll(".slide");
        setTotalSlides(slides.length);
    }, [htmlContent]);

    // Update iframe content to show current slide
    useEffect(() => {
        if (!iframeRef.current) return;

        const iframe = iframeRef.current;
        const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;

        if (iframeDoc) {
            iframeDoc.open();

            // Inject KaTeX for math rendering
            const katexCSS = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css" crossorigin="anonymous">';
            const katexJS = '<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js" crossorigin="anonymous"></script>';
            const katexAutoRender = '<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>';

            // Insert KaTeX into HTML before writing
            let enhancedHTML = htmlContent;

            // Ensure all slides start hidden (prevents flash)
            const slideHiddenCSS = '<style>.slide { display: none !important; } .slide.active { display: flex !important; }</style>';

            if (enhancedHTML.includes('<head>')) {
                enhancedHTML = enhancedHTML.replace('</head>', `${katexCSS}${katexJS}${katexAutoRender}${slideHiddenCSS}</head>`);
            } else if (enhancedHTML.includes('<html>')) {
                enhancedHTML = enhancedHTML.replace('<html>', `<html><head>${katexCSS}${katexJS}${katexAutoRender}${slideHiddenCSS}</head>`);
            } else {
                enhancedHTML = `<html><head>${katexCSS}${katexJS}${katexAutoRender}${slideHiddenCSS}</head><body>${enhancedHTML}</body></html>`;
            }

            iframeDoc.write(enhancedHTML);
            iframeDoc.close();

            // Show only current slide and trigger KaTeX
            setTimeout(() => {
                const slides = iframeDoc.querySelectorAll(".slide");
                slides.forEach((slide, index) => {
                    (slide as HTMLElement).classList.toggle("active", index === currentSlide);
                });

                // Manually trigger KaTeX rendering
                const iframeWindow = iframe.contentWindow as any;
                if (iframeWindow?.renderMathInElement) {
                    try {
                        iframeWindow.renderMathInElement(iframeDoc.body, {
                            delimiters: [
                                { left: '$$', right: '$$', display: true },
                                { left: '$', right: '$', display: false }
                            ],
                            throwOnError: false
                        });
                    } catch (e) {
                        console.error('KaTeX render error:', e);
                    }
                }
            }, 150);
        }
    }, [htmlContent, currentSlide]);

    const nextSlide = useCallback(() => {
        if (currentSlide < totalSlides - 1) {
            setCurrentSlide(prev => prev + 1);
        }
    }, [currentSlide, totalSlides]);

    const prevSlide = useCallback(() => {
        if (currentSlide > 0) {
            setCurrentSlide(prev => prev - 1);
        }
    }, [currentSlide]);

    const enterFullscreen = useCallback(async () => {
        if (!containerRef.current || isFullscreen) return;

        try {
            await containerRef.current.requestFullscreen();
            setIsFullscreen(true);
        } catch (error) {
            console.error("Fullscreen error:", error);
        }
    }, [isFullscreen]);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            switch (e.key) {
                case "ArrowRight":
                    nextSlide();
                    break;
                case "ArrowLeft":
                    prevSlide();
                    break;
                case "F":
                    enterFullscreen();
                    break;
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [nextSlide, prevSlide, enterFullscreen, isFullscreen]);

    // Handle fullscreen change events
    useEffect(() => {
        const handleFullscreenChange = () => {
            setIsFullscreen(!!document.fullscreenElement);
        };

        document.addEventListener("fullscreenchange", handleFullscreenChange);
        return () => document.removeEventListener("fullscreenchange", handleFullscreenChange);
    }, []);

    // Auto enter fullscreen on mount
    useEffect(() => {
        const autoEnterFullscreen = async () => {
            if (containerRef.current && !isFullscreen) {
                try {
                    await containerRef.current.requestFullscreen();
                    setIsFullscreen(true);
                } catch (error) {
                    console.error("Auto fullscreen error:", error);
                }
            }
        };

        // Small delay to ensure DOM is ready
        const timer = setTimeout(() => {
            autoEnterFullscreen();
        }, 100);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div
            ref={containerRef}
            className={`relative w-full h-full bg-gray-900 ${isFullscreen ? "fixed inset-0 z-50" : ""}`}
        >
            {/* Close button */}
            {onClose && (
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={onClose}
                    className="absolute top-4 right-4 z-10 text-white hover:bg-white/20"
                >
                    <X className="h-4 w-4" />
                </Button>
            )}

            {/* Slides iframe - allow-scripts needed for KaTeX */}
            <iframe
                ref={iframeRef}
                className="w-full h-full border-0"
                title="Slides Presentation"
                sandbox="allow-same-origin allow-scripts"
            />

            {/* Navigation controls */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-black/70 px-6 py-3 rounded-full">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={prevSlide}
                    disabled={currentSlide === 0}
                    className="text-white hover:bg-white/20 disabled:opacity-30"
                >
                    <ChevronLeft className="h-5 w-5" />
                </Button>

                <span className="text-white font-medium min-w-[80px] text-center">
                    {currentSlide + 1} / {totalSlides}
                </span>

                <Button
                    variant="ghost"
                    size="icon"
                    onClick={nextSlide}
                    disabled={currentSlide === totalSlides - 1}
                    className="text-white hover:bg-white/20 disabled:opacity-30"
                >
                    <ChevronRight className="h-5 w-5" />
                </Button>
            </div>
        </div>
    );
}
