import React from "react";
import { interpolate } from "remotion";
import { C, ease, fontFamily, pop, popStyle, ramp, useT } from "./theme";
import { ArrowRight, Check, Cursor } from "./icons";

const DAYS = ["L", "M", "M", "J", "V", "S", "D"];

/** Calendario + botón "Agendar llamada", igual que el cierre de los anuncios A–E. */
export const CtaScene: React.FC<{ from: number; entra: number; agenda: number; llamada: number; revisamos: number }> = ({
  from,
  entra,
  agenda,
  llamada,
  revisamos,
}) => {
  const t = useT();
  const card = pop(t, from);
  const btn = pop(t, llamada - 0.15);
  const press = interpolate(t, [revisamos - 0.05, revisamos + 0.05, revisamos + 0.25], [1, 0.95, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cursorP = ramp(t, revisamos - 0.9, revisamos - 0.08);
  const ripple = ramp(t, revisamos, revisamos + 0.6);
  const shine = ((t - (llamada + 0.2)) % 2.2) / 2.2;

  return (
    <>
      <div
        style={{
          position: "absolute",
          left: 92,
          top: 380,
          width: 896,
          height: 740,
          background: C.card,
          border: `2.5px solid ${C.border}`,
          borderRadius: 44,
          boxShadow: "0 30px 90px rgba(0,0,0,0.4)",
          padding: "52px 60px",
          boxSizing: "border-box",
          ...popStyle(card),
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 34 }}>
          <div style={{ width: 16, height: 16, borderRadius: 8, background: C.green }} />
          <span style={{ fontFamily, fontWeight: 700, fontSize: 34, letterSpacing: 5, color: C.muted }}>LLAMADA</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 104px)", columnGap: 8, rowGap: 10 }}>
          {DAYS.map((d, i) => (
            <div key={`d${i}`} style={{ textAlign: "center", fontFamily, fontWeight: 700, fontSize: 30, color: C.muted, height: 50 }}>
              {d}
            </div>
          ))}
          {Array.from({ length: 28 }, (_, i) => {
            const n = i + 1;
            const p = pop(t, from + 0.15 + i * 0.022, 30, 16);
            const sel = n === 17 ? pop(t, entra, 30, 11) : 0;
            return (
              <div
                key={n}
                style={{
                  height: 76,
                  borderRadius: 16,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily,
                  fontWeight: 700,
                  fontSize: 38,
                  color: sel > 0.5 ? C.ink : C.white,
                  background: sel > 0.02 ? `rgba(25,226,165,${sel})` : "#16204a",
                  border: `2px solid ${sel > 0.02 ? C.green : "#212c5c"}`,
                  boxShadow: sel > 0.02 ? `0 0 ${36 * sel}px rgba(25,226,165,0.55)` : undefined,
                  scale: String((0.8 + 0.2 * p) * (1 + 0.12 * sel)),
                  opacity: p,
                }}
              >
                {n}
              </div>
            );
          })}
        </div>
        <div style={{ display: "flex", gap: 22, marginTop: 34 }}>
          {["09:30", "11:00", "15:30"].map((s, i) => {
            const p = pop(t, entra + 0.35 + i * 0.08, 30, 15);
            const sel = s === "11:00" ? pop(t, agenda, 30, 12) : 0;
            return (
              <div
                key={s}
                style={{
                  flex: 1,
                  height: 84,
                  borderRadius: 18,
                  border: `2.5px solid ${sel > 0.05 ? C.green : "#24305f"}`,
                  background: sel > 0.05 ? C.green : "transparent",
                  color: sel > 0.5 ? C.ink : C.white,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 10,
                  fontFamily,
                  fontWeight: 700,
                  fontSize: 40,
                  ...popStyle(p, 16),
                }}
              >
                {sel > 0.05 && <Check size={34} color={C.ink} stroke={3} />}
                {s}
              </div>
            );
          })}
        </div>
      </div>

      {/* Botón */}
      <div
        style={{
          position: "absolute",
          left: 88,
          top: 1160,
          width: 904,
          height: 140,
          borderRadius: 54,
          background: C.green,
          boxShadow: `0 0 ${60 + 30 * ripple}px rgba(25,226,165,0.45)`,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 26,
          ...popStyle(btn, 30),
          scale: String((0.86 + 0.14 * btn) * press),
        }}
      >
        <span style={{ fontFamily, fontWeight: 800, fontSize: 60, color: C.ink, letterSpacing: -1 }}>AGENDAR LLAMADA</span>
        <ArrowRight size={60} color={C.ink} stroke={3} />
        {t > llamada + 0.2 && (
          <div
            style={{
              position: "absolute",
              top: -40,
              bottom: -40,
              width: 130,
              left: interpolate(shine, [0, 0.6, 1], [-200, 1100, 1100]),
              background: "rgba(255,255,255,0.35)",
              rotate: "18deg",
            }}
          />
        )}
        {ripple > 0 && ripple < 1 && (
          <div
            style={{
              position: "absolute",
              left: 640 - 400 * ripple,
              top: 70 - 400 * ripple,
              width: 800 * ripple,
              height: 800 * ripple,
              borderRadius: "50%",
              background: `rgba(255,255,255,${0.35 * (1 - ripple)})`,
            }}
          />
        )}
      </div>

      {cursorP > 0 && (
        <div
          style={{
            position: "absolute",
            left: interpolate(ease(cursorP), [0, 1], [880, 712]),
            top: interpolate(ease(cursorP), [0, 1], [1560, 1238]),
            opacity: Math.min(1, cursorP * 4),
            scale: String(press),
          }}
        >
          <Cursor size={72} />
        </div>
      )}
    </>
  );
};
