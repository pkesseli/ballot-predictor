"use client"

import { ChangeEvent, useCallback, useEffect, useRef, useState } from 'react';
import { ModelEvent, ModelStatus } from './entity';
import Progress from './progress'

/**
 * Currently the sole default page on the website. Will eventually become the
 * German predictor page.
 * 
 * @returns Next.js home page.
 */
export default function Home(): JSX.Element {
  const [progress, setProgress] = useState(0);
  const [isModelReady, setModelReady] = useState(false);
  const model = useRef<Worker | null>(null);
  useEffect(() => {
    const shouldInitialiseModel: boolean = !model.current;
    if (shouldInitialiseModel)
      model.current = new Worker(new URL('./model.ts', import.meta.url), { type: 'module' });

    const onMessageReceived = (e: MessageEvent<ModelEvent>) => {
      switch (e.data.status) {
        case ModelStatus.LOADING:
          setProgress(_ => e.data.progressInPercent!);
          break;
        case ModelStatus.READY:
          setModelReady(_ => true);
      }
    };
    model.current!.addEventListener('message', onMessageReceived);

    if (shouldInitialiseModel)
      model.current?.postMessage("init")

    return () => model.current?.removeEventListener('message', onMessageReceived);
  }, [])

  const tokenize = useCallback((text: string) => model.current?.postMessage(text), []);

  return (
    <main>
      <Progress visible={!isModelReady} percentage={progress} />
      <input type="text" onInput={(e: ChangeEvent<HTMLInputElement>) => tokenize(e.target.value)} />
    </main>
  );
}
