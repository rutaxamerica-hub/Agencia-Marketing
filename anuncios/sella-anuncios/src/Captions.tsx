import React, { useMemo } from "react";
import { C, fontFamily, pop, ramp, useT } from "./theme";

export type Word = { text: string; start: number; end: number };
type Page = { words: Word[]; start: number; end: number };

const MAX_CHARS = 16;
const chars = (ws: Word[]) => ws.reduce((n, x) => n + x.text.length, 0);

/**
 * Parte una frase en grupos de hasta 3 palabras que quepan en una línea:
 * la menor cantidad de grupos y, entre esas, la de largos más parejos.
 */
const chunk = (phrase: Word[]): Word[][] => {
  const fits = (g: Word[]) => g.length === 1 || chars(g) <= MAX_CHARS;
  const memo = new Map<number, { groups: Word[][]; cost: number } | null>();
  const best = (i: number): { groups: Word[][]; cost: number } | null => {
    if (i === phrase.length) return { groups: [], cost: 0 };
    if (memo.has(i)) return memo.get(i)!;
    let res: { groups: Word[][]; cost: number } | null = null;
    for (let size = 1; size <= 3 && i + size <= phrase.length; size++) {
      const g = phrase.slice(i, i + size);
      const rest = fits(g) ? best(i + size) : null;
      if (!rest) continue;
      // Cada grupo extra pesa mucho; luego se castigan grupos muy cortos o muy largos.
      const cost = rest.cost + 1000 + (MAX_CHARS - chars(g)) ** 2;
      if (!res || cost < res.cost) res = { groups: [g, ...rest.groups], cost };
    }
    memo.set(i, res);
    return res;
  };
  return best(0)?.groups ?? phrase.map((w) => [w]);
};

/** Páginas de hasta 3 palabras, cortando en puntuación o pausas, como en los anuncios A–E. */
const toPages = (words: Word[]): Page[] => {
  const phrases: Word[][] = [];
  let cur: Word[] = [];
  words.forEach((w, i) => {
    cur.push(w);
    const next = words[i + 1];
    const punct = /[.?!,:]$/.test(w.text);
    const pause = next ? next.start - w.end > 0.45 : true;
    if (punct || pause) {
      phrases.push(cur);
      cur = [];
    }
  });
  if (cur.length) phrases.push(cur);
  return phrases
    .flatMap(chunk)
    .map((ws) => ({ words: ws, start: ws[0].start, end: ws[ws.length - 1].end }));
};

export const Captions: React.FC<{ words: Word[]; top?: number }> = ({ words, top = 1395 }) => {
  const t = useT();
  const pages = useMemo(() => toPages(words), [words]);
  const idx = pages.findIndex((p, i) => t >= p.start - 0.04 && (i === pages.length - 1 || t < pages[i + 1].start - 0.04));
  if (idx < 0) return null;
  const page = pages[idx];
  if (t > page.end + 1.1) return null;
  // La primera página ya está visible en el fotograma 0 (miniatura del anuncio).
  const enter = page.start < 0.1 ? 1 : pop(t, page.start - 0.04, 30, 16);
  const dim = ramp(t, page.end + 0.15, page.end + 0.45);

  return (
    <div
      style={{
        position: "absolute",
        top,
        left: 40,
        right: 40,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        alignItems: "center",
        columnGap: 12,
        rowGap: 4,
        scale: String(0.9 + 0.1 * enter),
        opacity: Math.min(1, enter * 2),
      }}
    >
      {page.words.map((w, i) => {
        const nextStart = page.words[i + 1]?.start ?? w.end + 0.2;
        const active = t >= w.start - 0.03 && t < nextStart - 0.03 && t < page.end + 0.15;
        const p = active ? pop(t, w.start - 0.03, 30, 12) : 0;
        return (
          <span
            key={i}
            style={{
              fontFamily,
              fontWeight: 800,
              fontSize: 80,
              lineHeight: 1.15,
              letterSpacing: -1.5,
              textTransform: "uppercase",
              color: active ? C.ink : `rgba(255,255,255,${1 - 0.38 * dim})`,
              background: active ? C.green : "transparent",
              borderRadius: 16,
              padding: "0 16px",
              rotate: active ? `${-2.5 * p}deg` : "0deg",
              scale: active ? String(1 + 0.06 * p) : "1",
              textShadow: active ? "none" : "0 6px 18px rgba(0,0,0,0.45)",
              display: "inline-block",
            }}
          >
            {w.text}
          </span>
        );
      })}
    </div>
  );
};
