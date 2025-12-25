"use client";
import 'katex/dist/katex.min.css';
import katex from 'katex';
import { useEffect, useRef } from 'react';

export default function MathRenderer({ expression }: { expression: string }) {
  const containerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      try {
        katex.render(expression, containerRef.current, {
          throwOnError: false,
          displayMode: true, // Centers the equation and makes it big
          output: 'html', // Render as HTML for speed
        });
      } catch (error) {
        console.error("KaTeX Render Error:", error);
        containerRef.current.innerText = expression;
      }
    }
  }, [expression]);

  return <span ref={containerRef} className="text-cyan-300 text-lg" />;
}