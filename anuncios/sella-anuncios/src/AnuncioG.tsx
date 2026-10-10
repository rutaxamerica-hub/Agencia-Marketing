import React from "react";
import { AbsoluteFill, interpolate, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import voz from "./data/voz-G.json";
import { C, ease, fontFamily, pop, popStyle, ramp, useT } from "./theme";
import { Background, Card, Chip, countUp, FooterPill, Label, Logo, PanelHeader, Scene } from "./ui";
import { Captions } from "./Captions";
import { CtaScene } from "./Cta";
import { Bubble, Particles, Stamp } from "./fx";
import { Owner } from "./Owner";
import { Chat, Check, Clock, Hand, ImagePost, Loop, Megaphone, Sheet, Spark } from "./icons";

// Momentos clave de la locución (segundos), de voz-G.json.
const T = {
  mano: 1.48,
  publicar: 2.11,
  responder: 2.55,
  ajustar: 3.37,
  anotar: 4.17,
  manana: 5.55,
  todo: 5.79,
  pct81: 7.1,
  agotado: 9.52,
  pct70: 10.22,
  horas: 11.82,
  sella: 13.84,
  encarga: 14.2,
  panel: 15.86,
  tu: 16.47,
  revisas: 16.71,
  resultados: 17.19,
  entra: 18.73,
  agenda: 19.73,
  llamada: 20.19,
  revisamos: 21.59,
};

const S = { hook: 2.0, tareas: 6.9, datos: 13.7, sella: 18.35 };

/** 1. ¿Sigues haciendo todo tu marketing a mano? — el dueño tapado de pendientes. */
const Hook: React.FC = () => {
  const t = useT();
  const pending = Math.round(interpolate(t, [0, 1.9], [14, 37], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
  const jitter = Math.sin(t * 22) * 7;
  return (
    <>
      <div style={{ position: "absolute", top: 300, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 26,
            padding: "18px 44px",
            borderRadius: 40,
            background: C.redSoft,
            border: `3px solid ${C.red}`,
          }}
        >
          <span style={{ fontFamily, fontWeight: 800, fontSize: 40, letterSpacing: 3, color: C.white }}>PENDIENTES</span>
          <span style={{ fontFamily, fontWeight: 800, fontSize: 92, lineHeight: 1, color: C.red, minWidth: 110, textAlign: "center" }}>{pending}</span>
        </div>
      </div>
      {/* Dueño al centro */}
      <div style={{ position: "absolute", left: 540 - 170, top: 700 }}>
        <Owner width={340} armR={62 + jitter} armL={28 - jitter} headTilt={8} item="phone" sweat={0.6 + 0.4 * Math.sin(t * 6)} />
      </div>
      {/* Notificaciones que no paran */}
      <Bubble at={-0.6} float={0} style={{ left: 40, top: 470 }} iconBg="#2b6cff" icon={<Chat size={42} color={C.white} stroke={2.2} />} badge="37" text="Mensajes sin leer" />
      <Bubble at={-0.45} float={1} style={{ right: 40, top: 600 }} iconBg="#d6339a" icon={<ImagePost size={42} color={C.white} stroke={2.2} />} text="Publicar post de hoy" />
      <Bubble at={-0.3} float={2} style={{ left: 40, top: 740 }} iconBg={C.red} icon={<Megaphone size={42} color={C.white} stroke={2.2} />} text="Ajustar anuncio" />
      <Bubble at={0.25} float={3} style={{ right: 40, top: 880 }} iconBg="#1f9d55" icon={<Sheet size={42} color={C.white} stroke={2.2} />} text="Pasar clientes a Excel" />
      <Bubble at={0.6} float={4} style={{ left: 40, top: 1020 }} iconBg="#2b6cff" icon={<Chat size={42} color={C.white} stroke={2.2} />} badge="12" text="Responder comentarios" />
      <Bubble at={0.95} float={5} style={{ right: 40, top: 1160 }} iconBg="#d6339a" icon={<ImagePost size={42} color={C.white} stroke={2.2} />} text="Subir historia" />
      <div style={{ position: "absolute", left: 0, right: 0, top: 1240, display: "flex", justifyContent: "center" }}>
        <Stamp at={T.mano - 0.1} size={60}>
          <Hand size={62} color={C.white} stroke={2.4} /> TODO A MANO
        </Stamp>
      </div>
    </>
  );
};

const TASKS = [
  { Icon: ImagePost, label: "PUBLICAR", at: T.publicar, bg: "#d6339a" },
  { Icon: Chat, label: "RESPONDER", at: T.responder, bg: "#2b6cff" },
  { Icon: Megaphone, label: "AJUSTAR ANUNCIOS", at: T.ajustar, bg: C.red },
  { Icon: Sheet, label: "ANOTAR EN EXCEL", at: T.anotar, bg: "#1f9d55" },
];
const TILE = { w: 440, h: 330, gap: 40, x0: 80, y0: 470 };
const tilePos = (i: number) => ({ x: TILE.x0 + (i % 2) * (TILE.w + TILE.gap), y: TILE.y0 + Math.floor(i / 2) * (TILE.h + TILE.gap) });

/** 2. Publicar, responder, ajustar, anotar… y mañana, todo de nuevo. */
const Tareas: React.FC = () => {
  const t = useT();
  const reset = t >= T.todo + 0.1;
  const spin = ramp(t, T.manana, T.manana + 0.9);
  // Mano que marca cada tarea.
  let hx = 900;
  let hy = 1300;
  TASKS.forEach((task, i) => {
    const k = ease(ramp(t, task.at - 0.35, task.at - 0.02));
    const prev = i === 0 ? { x: 900, y: 1300 } : { x: tilePos(i - 1).x + TILE.w - 120, y: tilePos(i - 1).y + TILE.h - 120 };
    const cur = { x: tilePos(i).x + TILE.w - 120, y: tilePos(i).y + TILE.h - 120 };
    if (k > 0) {
      hx = interpolate(k, [0, 1], [prev.x, cur.x]);
      hy = interpolate(k, [0, 1], [prev.y, cur.y]);
    }
  });
  const handOut = ramp(t, T.manana - 0.2, T.manana + 0.2);
  const tap = TASKS.some((x) => t > x.at - 0.05 && t < x.at + 0.1) ? 0.85 : 1;
  return (
    <>
      <div style={{ position: "absolute", top: 320, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <Chip color={reset ? C.red : C.slate} style={{ fontSize: 34, padding: "12px 30px" }}>
          <Clock size={36} color={reset ? C.red : C.slate} stroke={2.4} /> {t >= T.manana ? "MAÑANA" : "HOY"}
        </Chip>
      </div>
      {TASKS.map(({ Icon, label, at, bg }, i) => {
        const { x, y } = tilePos(i);
        const p = pop(t, 1.95 + i * 0.07);
        const done = !reset && t >= at;
        const ck = done ? pop(t, at, 30, 11) : 0;
        return (
          <div
            key={label}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: TILE.w,
              height: TILE.h,
              borderRadius: 36,
              background: C.card,
              border: `3px solid ${done ? C.white : C.border}`,
              boxShadow: done ? "0 0 50px rgba(255,255,255,0.18)" : "0 24px 60px rgba(0,0,0,0.35)",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 22,
              ...popStyle(p),
              scale: String((0.86 + 0.14 * p) * (1 + 0.05 * Math.sin(Math.PI * Math.min(1, ck)))),
            }}
          >
            <div style={{ width: 130, height: 130, borderRadius: 34, background: bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Icon size={80} color={C.white} stroke={2} />
            </div>
            <div style={{ fontFamily, fontWeight: 800, fontSize: 42, color: C.white, textAlign: "center", lineHeight: 1.05, padding: "0 20px" }}>{label}</div>
            {done && (
              <div style={{ position: "absolute", right: 22, top: 22, width: 66, height: 66, borderRadius: 33, background: C.white, display: "flex", alignItems: "center", justifyContent: "center", scale: String(ck) }}>
                <Check size={46} color={C.ink} stroke={3.6} />
              </div>
            )}
          </div>
        );
      })}
      {/* Flecha circular de "otra vez" */}
      {spin > 0 && (
        <div style={{ position: "absolute", left: 540 - 520, top: 835 - 520, width: 1040, height: 1040, opacity: Math.min(1, spin * 3) * 0.9, rotate: `${spin * 360}deg` }}>
          <Loop size={1040} color={C.red} stroke={0.7} />
        </div>
      )}
      {handOut < 1 && t > 1.9 && (
        <div style={{ position: "absolute", left: hx + 200 * handOut, top: hy + 300 * handOut, opacity: 1 - handOut, scale: String(tap), filter: "drop-shadow(0 12px 24px rgba(0,0,0,0.5))" }}>
          <div style={{ background: C.white, borderRadius: 60, padding: 16, display: "flex" }}>
            <Hand size={84} color={C.ink} stroke={2.2} />
          </div>
        </div>
      )}
      <div style={{ position: "absolute", left: 0, right: 0, top: 735, display: "flex", justifyContent: "center" }}>
        <Stamp at={T.todo} size={72}>
          <Loop size={72} color={C.white} stroke={3} /> TODO DE NUEVO
        </Stamp>
      </div>
    </>
  );
};

/** 3. 81% agotado, 70% menos de 5 horas. */
const StatCard: React.FC<{ at: number; top: number; value: string; color: string; children: React.ReactNode; footer: React.ReactNode; source: string }> = ({
  at,
  top,
  value,
  color,
  children,
  footer,
  source,
}) => (
  <Card at={at} style={{ top, height: 430, padding: "44px 50px 0", boxSizing: "border-box" }}>
    <div style={{ display: "flex", alignItems: "center", gap: 36 }}>
      <span style={{ fontFamily, fontWeight: 800, fontSize: 190, color, letterSpacing: -8, lineHeight: 0.95, textShadow: `0 0 50px ${color}55`, minWidth: 390 }}>{value}</span>
      <div style={{ fontFamily, fontWeight: 800, fontSize: 44, lineHeight: 1.15, color: C.white }}>{children}</div>
    </div>
    <div style={{ marginTop: 34 }}>{footer}</div>
    <div style={{ position: "absolute", right: 50, bottom: 22, fontFamily, fontSize: 24, color: C.muted }}>{source}</div>
  </Card>
);

const Datos: React.FC = () => {
  const t = useT();
  const level = interpolate(t, [T.pct81, T.agotado + 0.2], [0.7, 0.08], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const batColor = level > 0.45 ? C.green : level > 0.2 ? C.yellow : C.red;
  const blink = t > T.agotado ? 0.55 + 0.45 * Math.abs(Math.cos((t - T.agotado) * 6)) : 1;
  return (
    <>
      <StatCard
        at={6.85}
        top={330}
        value={`${countUp(t, T.pct81, T.pct81 + 0.8, 81)}%`}
        color={C.red}
        source="Fuente: Enji, 2025"
        footer={
          <div style={{ display: "flex", alignItems: "center", gap: 20, opacity: blink }}>
            <div style={{ flex: 1, height: 74, borderRadius: 22, border: `6px solid ${C.white}`, padding: 8, boxSizing: "border-box" }}>
              <div style={{ width: `${level * 100}%`, height: "100%", borderRadius: 12, background: batColor, boxShadow: `0 0 24px ${batColor}` }} />
            </div>
            <div style={{ width: 16, height: 34, borderRadius: "0 8px 8px 0", background: C.white }} />
            <span style={{ fontFamily, fontWeight: 800, fontSize: 48, color: batColor, minWidth: 110, textAlign: "right" }}>{Math.round(level * 100)}%</span>
          </div>
        }
      >
        DE LOS DUEÑOS
        <br />
        DE PYME DICE
        <br />
        ESTAR <span style={{ color: C.red }}>AGOTADO</span>
      </StatCard>
      <StatCard
        at={T.pct70 - 0.15}
        top={800}
        value={`${countUp(t, T.pct70, T.pct70 + 0.8, 70)}%`}
        color={C.yellow}
        source="Fuente: Fiverr, 2025"
        footer={
          <div style={{ display: "flex", alignItems: "center", gap: 22, ...popStyle(pop(t, T.horas), 12) }}>
            <Clock size={70} color={C.yellow} stroke={2.2} />
            <span style={{ fontFamily, fontWeight: 800, fontSize: 56, color: C.yellow }}>{"< 5 H"}</span>
            <span style={{ fontFamily, fontWeight: 700, fontSize: 40, color: C.muted }}>POR SEMANA</span>
          </div>
        }
      >
        LE DEDICA
        <br />
        <span style={{ color: C.yellow }}>MENOS DE 5 HORAS</span>
        <br />A LA SEMANA
      </StatCard>
    </>
  );
};

/** 4. Sella se encarga de todo, tú solo revisas resultados. */
const Sella: React.FC = () => {
  const t = useT();
  const auto = ramp(t, T.encarga, T.encarga + 0.35);
  const zero = pop(t, T.panel, 30, 10);
  const res = pop(t, T.tu);
  const line = ramp(t, T.tu + 0.1, T.resultados + 0.6);
  return (
    <>
      <Card at={13.65} glow style={{ top: 300, height: 700 }}>
        <PanelHeader />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "26px 44px 6px" }}>
          <Label style={{ fontSize: 32 }}>MODO</Label>
          <div
            style={{
              width: 330,
              height: 76,
              borderRadius: 40,
              background: auto > 0.5 ? C.green : "#2a3466",
              display: "flex",
              alignItems: "center",
              justifyContent: auto > 0.5 ? "flex-start" : "flex-end",
              padding: "0 10px",
              boxShadow: auto > 0.5 ? "0 0 40px rgba(25,226,165,0.5)" : "none",
              position: "relative",
            }}
          >
            <span style={{ position: "absolute", left: auto > 0.5 ? 26 : 120, fontFamily, fontWeight: 800, fontSize: 28, color: auto > 0.5 ? C.ink : C.muted }}>
              {auto > 0.5 ? "AUTOMÁTICO" : "MANUAL"}
            </span>
            <div style={{ position: "absolute", left: interpolate(auto, [0, 1], [10, 330 - 66]), width: 56, height: 56, borderRadius: 28, background: C.white }} />
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18, padding: "18px 44px 0" }}>
          {TASKS.map(({ Icon, label, bg }, i) => {
            const done = pop(t, T.encarga + 0.25 + i * 0.13, 30, 12);
            return (
              <div
                key={label}
                style={{
                  height: 128,
                  borderRadius: 26,
                  background: C.cardHi,
                  border: `3px solid ${done > 0.3 ? C.green : "#2a3670"}`,
                  display: "flex",
                  alignItems: "center",
                  gap: 18,
                  padding: "0 20px",
                }}
              >
                <div style={{ width: 74, height: 74, borderRadius: 20, background: bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <Icon size={46} color={C.white} stroke={2} />
                </div>
                <span style={{ flex: 1, fontFamily, fontWeight: 800, fontSize: 27, color: C.white, lineHeight: 1.1 }}>{label}</span>
                <div style={{ width: 52, height: 52, borderRadius: 26, background: done > 0.02 ? C.green : "transparent", border: `3px solid ${done > 0.02 ? C.green : C.muted2}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  {done > 0.02 && <Check size={34} color={C.ink} stroke={3.6} style={{ scale: String(done) }} />}
                </div>
              </div>
            );
          })}
        </div>
        <div
          style={{
            margin: "22px 44px 0",
            height: 96,
            borderRadius: 26,
            background: "linear-gradient(90deg, rgba(25,226,165,0.22), rgba(25,226,165,0.06))",
            border: `3px solid ${C.green}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 22,
            ...popStyle(zero, 16),
          }}
        >
          <span style={{ fontFamily, fontWeight: 800, fontSize: 40, letterSpacing: 2, color: C.white }}>PENDIENTES:</span>
          <span style={{ fontFamily, fontWeight: 800, fontSize: 72, color: C.green, lineHeight: 1 }}>0</span>
        </div>
      </Card>
      {/* Tú: solo revisas resultados */}
      <div style={{ position: "absolute", left: 70, top: 1018, ...popStyle(res, 30) }}>
        <Owner width={130} armR={70} armL={14} item="phone" headTilt={-6} />
      </div>
      <Card at={T.tu + 0.05} style={{ left: 240, top: 1030, height: 200, display: "flex", alignItems: "center", gap: 20, padding: "0 30px", boxSizing: "border-box" }}>
        <div style={{ flex: 1 }}>
          <Label style={{ color: C.green, fontSize: 26 }}>TUS RESULTADOS</Label>
          <svg width={360} height={100} style={{ marginTop: 6 }}>
            <defs>
              <clipPath id="resG">
                <rect x={0} y={0} width={360 * line} height={100} />
              </clipPath>
            </defs>
            <path d="M 6 88 C 70 80, 110 72, 160 58 S 250 42, 290 26 S 340 10, 354 6" stroke={C.green} strokeWidth={8} fill="none" strokeLinecap="round" clipPath="url(#resG)" style={{ filter: "drop-shadow(0 0 10px rgba(25,226,165,0.6))" }} />
          </svg>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, background: C.green, color: C.ink, borderRadius: 40, padding: "14px 22px", fontFamily, fontWeight: 800, fontSize: 28, ...popStyle(pop(t, T.revisas), 10) }}>
          <Spark size={32} color={C.ink} stroke={3} /> TÚ: REVISAS
        </div>
      </Card>
      <FooterPill at={T.resultados + 0.2} top={1262} />
    </>
  );
};

export const AnuncioG: React.FC = () => {
  return (
    <AbsoluteFill>
      <Background />
      <Particles />
      <Scene from={0} to={S.hook}>
        <Hook />
      </Scene>
      <Scene from={S.hook} to={S.tareas}>
        <Tareas />
      </Scene>
      <Scene from={S.tareas} to={S.datos}>
        <Datos />
      </Scene>
      <Scene from={S.datos} to={S.sella}>
        <Sella />
      </Scene>
      <Scene from={S.sella} to={voz.duration + 1}>
        <CtaScene from={S.sella} entra={T.entra} agenda={T.agenda} llamada={T.llamada} revisamos={T.revisamos} />
      </Scene>
      <Logo />
      <Captions words={voz.words} />
      <Audio src={staticFile("audio/anuncio-G.wav")} />
    </AbsoluteFill>
  );
};

export const durationG = voz.duration;

