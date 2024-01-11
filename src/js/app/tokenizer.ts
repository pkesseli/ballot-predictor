import { BertTokenizer, PreTrainedTokenizer, Tensor } from '@xenova/transformers';

/** Single tokenizer instance, reused as long as the module exists. */
let tokenizer: PreTrainedTokenizer

/**
 * Default event listener. Currently initalises a tokenizer if missing. This
 * should be done on startup in the future.
 */
self.addEventListener("message", async (e: MessageEvent<string>) => {
  if (tokenizer === undefined)
    tokenizer = await BertTokenizer.from_pretrained("Xenova/bert-base-multilingual-cased");

  self.postMessage("pong: " + e.data);
});