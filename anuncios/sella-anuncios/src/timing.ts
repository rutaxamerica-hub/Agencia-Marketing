import type { Word } from "./Captions";

const norm = (s: string) => s.replace(/[¿?¡!.,:]/g, "");

/** Segundo en que empieza la palabra `text` (la n-ésima vez que aparece) en la locución. */
export const wordAt = (words: Word[], text: string, nth = 0): number => {
  let k = 0;
  for (const w of words) {
    if (norm(w.text) === text) {
      if (k === nth) return w.start;
      k++;
    }
  }
  throw new Error(`Palabra no encontrada en la locución: ${text} (#${nth})`);
};
