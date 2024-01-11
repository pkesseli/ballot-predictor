"use client"

import { ChangeEvent, useCallback, useEffect, useRef } from 'react';

/**
 * Currently the sole default page on the website. Will eventually become the
 * German predictor page.
 * 
 * @returns Next.js home page.
 */
export default function Home(): JSX.Element {
  const tokenizer = useRef<Worker | null>(null);
  useEffect(() => {
    if (!tokenizer.current)
      tokenizer.current = new Worker(new URL('./tokenizer.ts', import.meta.url), {
        type: 'module'
      });
    tokenizer.current.addEventListener('message', (e: MessageEvent<string>) => {
      console.log("e: " + e.data);
    });
  }, [])

  const tokenize = useCallback((text: string) => {
    tokenizer.current?.postMessage(text);
  }, []);

  return (
    <main>
      <input type="text" onInput={(e: ChangeEvent<HTMLInputElement>) => tokenize(e.target.value)} />
    </main>
  );
}
