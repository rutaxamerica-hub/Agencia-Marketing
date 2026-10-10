import React from "react";
import { AbsoluteFill, Easing } from "remotion";
import { C, fontFamily, pop, popStyle, ramp, useT } from "./theme";
import { House, PlusCircle, Seal, Store } from "./icons";

export const Background: React.FC = () => (
  <AbsoluteFill
    style={{
      backgroundColor: C.bg,
      backgroundImage: [
        "radial-gradient(ellipse 820px 760px at 50% 33%, rgba(30,44,110,0.55) 0%, rgba(22,32,79,0.25) 45%, rgba(9,14,29,0) 75%)",
        "repeating-linear-gradient(0deg, rgba(255,255,255,0.022) 0 2px, transparent 2px 120px)",
        "repeating-linear-gradient(90deg, rgba(255,255,255,0.022) 0 2px, transparent 2px 120px)",
      ].join(","),
      fontFamily,
    }}
  />
);

export const Logo: React.FC = () => (
  <div style={{ position: "absolute", left: 64, top: 182, display: "flex", alignItems: "center", gap: 16 }}>
    <Seal size={58} />
    <span style={{ fontFamily, fontWeight: 700, fontSize: 46, color: C.white, letterSpacing: -0.5 }}>Sella</span>
  </div>
);

/** Ventana de escena: aparece y desaparece con un fundido corto. Los hijos usan el tiempo global. */
export const Scene: React.FC<{ from: number; to: number; children: React.ReactNode }> = ({
  from,
  to,
  children,
}) => {
  const t = useT();
  if (t < from || t > to + 0.3) return null;
  const inP = from <= 0 ? 1 : ramp(t, from, from + 0.22);
  const outP = ramp(t, to, to + 0.25, Easing.in(Easing.quad));
  return (
    <AbsoluteFill style={{ opacity: inP * (1 - outP), scale: String(1 - 0.03 * outP) }}>{children}</AbsoluteFill>
  );
};

export const Pill: React.FC<{ children: React.ReactNode; at: number; top: number; color?: string }> = ({
  children,
  at,
  top,
  color = C.green,
}) => {
  const t = useT();
  const p = pop(t, at);
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          ...popStyle(p, 20),
          padding: "14px 34px",
          borderRadius: 60,
          border: `3px solid ${color}`,
          background: "rgba(25,226,165,0.07)",
          color,
          fontFamily,
          fontWeight: 700,
          fontSize: 30,
          letterSpacing: 4,
        }}
      >
        {children}
      </div>
    </div>
  );
};

export const Card: React.FC<{
  style?: React.CSSProperties;
  at: number;
  children?: React.ReactNode;
  glow?: boolean;
}> = ({ style, at, children, glow }) => {
  const t = useT();
  const p = pop(t, at);
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        background: C.card,
        border: `2.5px solid ${glow ? C.green : C.border}`,
        borderRadius: 40,
        boxShadow: glow
          ? "0 0 60px rgba(25,226,165,0.18), 0 30px 80px rgba(0,0,0,0.35)"
          : "0 30px 80px rgba(0,0,0,0.35)",
        overflow: "hidden",
        ...popStyle(p),
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const Label: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div
    style={{
      fontFamily,
      fontWeight: 700,
      fontSize: 25,
      letterSpacing: 3.5,
      color: C.muted,
      textTransform: "uppercase",
      ...style,
    }}
  >
    {children}
  </div>
);

export const Chip: React.FC<{
  children: React.ReactNode;
  color: string;
  solid?: boolean;
  style?: React.CSSProperties;
  p?: number;
}> = ({ children, color, solid, style, p = 1 }) => (
  <div
    style={{
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      padding: "8px 20px",
      borderRadius: 40,
      border: `2.5px solid ${color}`,
      background: solid ? color : "transparent",
      color: solid ? C.ink : color,
      fontFamily,
      fontWeight: 700,
      fontSize: 24,
      letterSpacing: 2,
      whiteSpace: "nowrap",
      ...popStyle(p, 12),
      ...style,
    }}
  >
    {children}
  </div>
);

export const PanelHeader: React.FC<{ title?: string }> = ({ title = "Panel Sella" }) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "30px 40px 26px",
      borderBottom: `2px solid ${C.border}`,
    }}
  >
    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
      <Seal size={50} />
      <span style={{ fontFamily, fontWeight: 700, fontSize: 40, color: C.white }}>{title}</span>
    </div>
    <div
      style={{
        border: `2.5px solid ${C.yellowText}`,
        color: C.yellowText,
        borderRadius: 40,
        padding: "8px 22px",
        fontFamily,
        fontWeight: 700,
        fontSize: 21,
        letterSpacing: 2.5,
      }}
    >
      EJEMPLO ILUSTRATIVO
    </div>
  </div>
);

/** Barra de progreso horizontal. */
export const Bar: React.FC<{ value: number; color: string; height?: number; glow?: boolean }> = ({
  value,
  color,
  height = 18,
  glow,
}) => (
  <div style={{ height, borderRadius: height, background: "#1a2448", overflow: "hidden" }}>
    <div
      style={{
        width: `${Math.max(0, Math.min(1, value)) * 100}%`,
        height: "100%",
        borderRadius: height,
        background: color,
        boxShadow: glow ? `0 0 24px ${color}` : undefined,
      }}
    />
  </div>
);

export const FooterPill: React.FC<{ at: number; top: number }> = ({ at, top }) => {
  const t = useT();
  const p = pop(t, at);
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        top,
        height: 106,
        borderRadius: 60,
        border: `2.5px solid ${C.green}`,
        background: "linear-gradient(90deg, rgba(25,226,165,0.10), rgba(25,226,165,0.03))",
        display: "flex",
        alignItems: "center",
        gap: 22,
        padding: "0 40px",
        ...popStyle(p, 20),
      }}
    >
      <div style={{ display: "flex", gap: 14 }}>
        <Store size={44} color={C.green} />
        <PlusCircle size={44} color={C.green} />
        <House size={44} color={C.green} />
      </div>
      <div style={{ fontFamily, fontWeight: 700, fontSize: 29, lineHeight: 1.2, color: C.white }}>
        HECHO PARA PYMES CHILENAS
        <br />
        QUE YA INVIERTEN EN PUBLICIDAD
      </div>
    </div>
  );
};

export const Source: React.FC<{ children: React.ReactNode; top: number; at: number }> = ({ children, top, at }) => {
  const t = useT();
  return (
    <div
      style={{
        position: "absolute",
        top,
        left: 0,
        right: 0,
        textAlign: "center",
        fontFamily,
        fontWeight: 400,
        fontSize: 26,
        color: C.muted,
        opacity: ramp(t, at, at + 0.4),
      }}
    >
      {children}
    </div>
  );
};

/** Número que cuenta hasta `to`. */
export const countUp = (t: number, a: number, b: number, to: number) => Math.round(ramp(t, a, b) * to);
