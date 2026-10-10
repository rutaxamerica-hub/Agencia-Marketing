import React from "react";
import { AbsoluteFill } from "remotion";
import { C, fontFamily, pop, popStyle, useT } from "./theme";

/** Pseudo-aleatorio determinista (mismo resultado en cada fotograma). */
export const rand = (i: number, salt = 1) => {
  const x = Math.sin(i * 127.1 + salt * 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** Partículas suaves que suben lento, para dar profundidad al fondo. */
export const Particles: React.FC = () => {
  const t = useT();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {Array.from({ length: 22 }, (_, i) => {
        const size = 4 + rand(i, 2) * 8;
        const speed = 18 + rand(i, 3) * 30;
        const y = (((rand(i, 4) * 1920 - t * speed) % 1920) + 1920) % 1920;
        const x = rand(i, 5) * 1080 + Math.sin(t * 0.6 + i) * 14;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: size,
              background: i % 3 === 0 ? C.green : "#6f84ff",
              opacity: 0.12 + rand(i, 6) * 0.14,
              filter: "blur(1px)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** Lluvia de confeti que parte en `at`. */
export const Confetti: React.FC<{ at: number; x: number; y: number }> = ({ at, x, y }) => {
  const t = useT();
  const k = t - at;
  if (k < 0 || k > 2.2) return null;
  const colors = [C.green, C.yellow, "#ffffff", "#6f84ff"];
  return (
    <>
      {Array.from({ length: 34 }, (_, i) => {
        const ang = rand(i, 7) * Math.PI * 2;
        const v = 380 + rand(i, 8) * 520;
        const px = x + Math.cos(ang) * v * k;
        const py = y + Math.sin(ang) * v * k * 0.8 + 900 * k * k;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: px,
              top: py,
              width: 14,
              height: 24,
              borderRadius: 4,
              background: colors[i % colors.length],
              rotate: `${k * 720 * (rand(i, 9) - 0.5)}deg`,
              opacity: Math.max(0, 1 - k / 2.2),
            }}
          />
        );
      })}
    </>
  );
};

/** Sello rotado tipo "SIN PLAN" de los anuncios originales. */
export const Stamp: React.FC<{
  at: number;
  children: React.ReactNode;
  color?: string;
  size?: number;
  rotate?: number;
  style?: React.CSSProperties;
}> = ({ at, children, color = C.red, size = 64, rotate = -5, style }) => {
  const t = useT();
  const p = pop(t, at, 30, 9);
  if (p <= 0) return null;
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 18,
        background: color,
        color: C.white,
        fontFamily,
        fontWeight: 800,
        fontSize: size,
        lineHeight: 1.05,
        textAlign: "center",
        padding: `${size * 0.28}px ${size * 0.6}px`,
        borderRadius: 24,
        boxShadow: `0 24px 70px ${color}66`,
        rotate: `${rotate}deg`,
        opacity: Math.min(1, p * 2),
        scale: String(1.7 - 0.7 * p),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Notificación flotante (mensajes, tareas pendientes…). */
export const Bubble: React.FC<{
  at: number;
  icon: React.ReactNode;
  iconBg: string;
  text: string;
  badge?: string;
  style?: React.CSSProperties;
  float?: number;
}> = ({ at, icon, iconBg, text, badge, style, float = 0 }) => {
  const t = useT();
  const p = pop(t, at, 30, 11);
  return (
    <div
      style={{
        position: "absolute",
        display: "flex",
        alignItems: "center",
        gap: 18,
        padding: "16px 26px 16px 16px",
        borderRadius: 30,
        background: "rgba(22,32,74,0.96)",
        border: "2.5px solid #2f3d7a",
        boxShadow: "0 18px 50px rgba(0,0,0,0.45)",
        ...popStyle(p, 30),
        translate: `0px ${(1 - p) * 30 + Math.sin(t * 2.2 + float) * 7}px`,
        ...style,
      }}
    >
      <div
        style={{
          position: "relative",
          width: 78,
          height: 78,
          borderRadius: 22,
          background: iconBg,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
        }}
      >
        {icon}
        {badge && (
          <div
            style={{
              position: "absolute",
              right: -12,
              top: -12,
              minWidth: 40,
              height: 40,
              borderRadius: 20,
              background: C.red,
              color: C.white,
              fontFamily,
              fontWeight: 800,
              fontSize: 22,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              padding: "0 8px",
              border: "3px solid #16204a",
            }}
          >
            {badge}
          </div>
        )}
      </div>
      <span style={{ fontFamily, fontWeight: 700, fontSize: 37, color: C.white, whiteSpace: "nowrap" }}>{text}</span>
    </div>
  );
};
