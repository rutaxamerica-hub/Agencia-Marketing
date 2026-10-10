import { Easing, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { loadFont } from "@remotion/fonts";

// Poppins local (public/fonts), así el render no depende de Google Fonts.
export const fontFamily = "Poppins";
for (const weight of ["400", "500", "600", "700", "800"]) {
  loadFont({ family: fontFamily, url: staticFile(`fonts/Poppins-${weight}.woff2`), weight });
}

// Paleta tomada de los anuncios A–E.
export const C = {
  bg: "#090e1d",
  glow: "#16204f",
  card: "#101932",
  cardHi: "#16204a",
  border: "#1c2750",
  borderHi: "#2a3772",
  green: "#19e2a5",
  greenSoft: "rgba(25,226,165,0.12)",
  red: "#fb4c5c",
  redSoft: "rgba(251,76,92,0.14)",
  yellow: "#ffc542",
  yellowText: "#eab645",
  white: "#ffffff",
  muted: "#8a93b8",
  muted2: "#5b6590",
  ink: "#06101d",
  slate: "#a7b2e0",
  figure: "#3e4f99",
};

export const W = 1080;
export const H = 1920;

export const ease = Easing.bezier(0.16, 1, 0.3, 1);

/** Segundos actuales de la composición. */
export const useT = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return frame / fps;
};

/** 0→1 entre a y b (segundos). */
export const ramp = (t: number, a: number, b: number, easing = ease) =>
  interpolate(t, [a, b], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

/** Resorte que arranca en `at` segundos. */
export const pop = (t: number, at: number, fps = 30, damping = 13) =>
  t < at
    ? 0
    : spring({
        frame: (t - at) * fps,
        fps,
        config: { damping, stiffness: 170, mass: 0.8 },
      });

/** Estilo de aparición estándar: sube, escala y aparece. */
export const popStyle = (p: number, dy = 40): React.CSSProperties => ({
  opacity: Math.min(1, p * 1.6),
  translate: `0px ${(1 - p) * dy}px`,
  scale: String(0.86 + 0.14 * p),
});
