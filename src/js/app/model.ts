import { BertTokenizer, PreTrainedTokenizer, env } from '@xenova/transformers';
import { FetchProgressEvent, trackResponseProgress } from 'fetch-api-progress';
import { ModelEvent, ModelStatus } from './entity';

/** Single tokenizer instance, reused as long as the module exists. */
let getTokenizer: Promise<PreTrainedTokenizer> = BertTokenizer.from_pretrained("Xenova/bert-base-multilingual-cased");;

/** Single vote prediction model instance, currently just a raw byte array. */
let getModel: Promise<ArrayBuffer> = createModel();

/**
 * Downloads the vote prediction model and creates a tensorflow.js model
 * instance from it.
 * 
 * @returns Async promise initialising the model.
 */
async function createModel(): Promise<ArrayBuffer> {
  const modelDownload: Response = await fetch('/vote-prediction.lzma');
  const modelDownloadWithProgress: Response = trackResponseProgress(
    modelDownload,
    (progress: FetchProgressEvent) => {
      if (progress.total) {
        const modelEvent: ModelEvent = {
          status: ModelStatus.LOADING,
          progressInPercent: Math.round(100.0 * progress.loaded / progress.total)
        };
        self.postMessage(modelEvent);
      }
    }
  );
  const modelContent: ArrayBuffer = await modelDownloadWithProgress.arrayBuffer();
  self.postMessage({ status: ModelStatus.READY });
  return modelContent;
}

/** Default event listener. Starts a vote prediction based on a user input. */
self.addEventListener("message", async (e: MessageEvent<string>) => {
  const tokenizer: PreTrainedTokenizer = await getTokenizer;
  const model: ArrayBuffer = await getModel;
  console.log("Do the work here...");
});
