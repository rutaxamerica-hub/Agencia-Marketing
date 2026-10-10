import React from "react";
import { AbsoluteFill, interpolate, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import voz from "./data/voz-G.json";
import { C, ease, fontFamily, pop, popStyle, ramp, useT } from "./theme";
import { Background, Bar, Card, Chip, countUp, FooterPill, Label, Logo, PanelHeader, Pill, Scene } from "./ui";
import { Captions } from "./Captions";
import { CtaScene } from "./Cta";
import { Chat, Check, Clock, Hand, ImagePost, Loop, Megaphone, Moon, Sheet, Spark, Users } from "./icons";

// Momentos clave de la locución (segundos), tomados de voz-G.json.
const T = {
  mano: 2.14,
  publicar: 2.9,
  responder: 3.8,
  ajustar: 5.12,
  anotar: 6.28,
  manana: 8.14,
  otraVez: 8.84,
  pct81: 9.86,
  agotado: 12.7,
  pct70: 13.72,
  horas: 15.92,
  sella: 18.69,
  encarga: 19.25,
  publicaciones: 20.81,
  anuncios: 21.77,
  seguimiento: 22.53,
  panel: 24.03,
  tu: 24.89,
};

const TASKS = [
  { Icon: ImagePost, title: "Publicar en Instagram", sub: "Diseñar, escribir y subir", at: T.publicar },
  { Icon: Chat, title: "Responder mensajes", sub: "37 sin leer", at: T.responder, badge: "37" },
  { Icon: Megaphone, title: "Ajustar anuncios", sub: "Presupuesto, público, texto", at: T.ajustar },
  { Icon: Sheet, title: "Anotar clientes en Excel", sub: "Copiar y pegar, uno por uno", at: T.anotar },
];

const ROW_TOP = 548; // y absoluto de la primera fila
const ROW_STEP = 154;
const BOX_X = 924; // x absoluto del checkbox

const CLOCK = ["23:41", "23:58", "00:26", "00:49", "01:15"];

/** Escena 1: todo el marketing a mano, y mañana otra vez. */
const Manual: React.FC = () => {
  const t = useT();
  const reset = t >= T.manana + 0.15;
  const doneCount = reset ? 0 : TASKS.filter((x) => t >= x.at + 0.12).length;
  const clock = reset ? CLOCK[0] : CLOCK[doneCount];
  const stamp = pop(t, T.otraVez, 30, 9);

  // Recorrido de la mano: de checkbox en checkbox.
  const stops = TASKS.map((x, i) => ({ at: x.at, y: ROW_TOP + 68 + i * ROW_STEP }));
  let hy = stops[0].y + 260;
  let hx = BOX_X + 120;
  for (let i = 0; i < stops.length; i++) {
    const s = stops[i];
    const prevY = i === 0 ? s.y + 260 : stops[i - 1].y;
    const prevX = i === 0 ? BOX_X + 120 : BOX_X;
    if (t >= s.at - 0.4) {
      const k = ease(ramp(t, s.at - 0.4, s.at - 0.05));
      hy = interpolate(k, [0, 1], [prevY, s.y]);
      hx = interpolate(k, [0, 1], [prevX, BOX_X]);
    }
  }
  const away = ramp(t, T.manana - 0.2, T.manana + 0.3);
  const tap = TASKS.some((x) => t > x.at - 0.06 && t < x.at + 0.12) ? 0.86 : 1;
  const handIn = ramp(t, T.publicar - 0.6, T.publicar - 0.3);

  return (
    <>
      <Pill at={-0.4} top={292}>
        SOLO PARA DUEÑOS DE PYMES
      </Pill>
      <Card at={-0.4} style={{ top: 400, height: 830 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", padding: "36px 40px 0" }}>
          <div>
            <Label style={{ color: reset ? C.red : C.muted }}>{reset ? "TU MARKETING · MAÑANA" : "TU MARKETING · HOY"}</Label>
            <div style={{ marginTop: 14 }}>
              <Chip color={C.red} p={pop(t, T.mano - 0.5)}>
                <Hand size={30} color={C.red} stroke={2.4} /> TODO A MANO
              </Chip>
            </div>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "12px 22px",
              borderRadius: 22,
              background: C.redSoft,
              border: `2.5px solid ${C.red}`,
            }}
          >
            <Clock size={40} color={C.red} stroke={2.4} />
            <span style={{ fontFamily, fontWeight: 800, fontSize: 46, color: C.white, letterSpacing: 1 }}>{clock}</span>
          </div>
        </div>
        <div style={{ position: "absolute", left: 40, right: 40, top: ROW_TOP - 400, display: "flex", flexDirection: "column", gap: 18 }}>
          {TASKS.map(({ Icon, title, sub, at, badge }, i) => {
            const p = pop(t, -0.3 + i * 0.1);
            const done = !reset && t >= at + 0.12;
            const ck = done ? pop(t, at + 0.12, 30, 12) : 0;
            const unread = badge && !done;
            return (
              <div
                key={title}
                style={{
                  height: 136,
                  borderRadius: 26,
                  background: C.cardHi,
                  border: `2.5px solid #222d5e`,
                  display: "flex",
                  alignItems: "center",
                  gap: 24,
                  padding: "0 28px",
                  opacity: done ? 0.62 : 1,
                  ...popStyle(p, 30),
                }}
              >
                <div style={{ position: "relative" }}>
                  <Icon size={58} color={C.slate} stroke={1.8} />
                  {unread && (
                    <div
                      style={{
                        position: "absolute",
                        right: -16,
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
                        padding: "0 6px",
                      }}
                    >
                      {badge}
                    </div>
                  )}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily, fontWeight: 700, fontSize: 36, color: C.white, textDecoration: done ? "line-through" : "none" }}>
                    {title}
                  </div>
                  <div style={{ fontFamily, fontWeight: 500, fontSize: 26, color: C.muted }}>{sub}</div>
                </div>
                <div
                  style={{
                    width: 58,
                    height: 58,
                    borderRadius: 14,
                    border: `3.5px solid ${done ? C.slate : C.muted2}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {done && <Check size={44} color={C.white} stroke={3.4} style={{ scale: String(ck) }} />}
                </div>
              </div>
            );
          })}
        </div>
        <div style={{ position: "absolute", left: 40, bottom: 34, display: "flex", alignItems: "center", gap: 18 }}>
          <Chip color={C.red}>PENDIENTES: {4 - doneCount}</Chip>
          {reset && (
            <span style={{ fontFamily, fontWeight: 700, fontSize: 26, color: C.muted, opacity: ramp(t, T.manana + 0.15, T.manana + 0.4) }}>
              Y vuelta a empezar…
            </span>
          )}
        </div>
        {stamp > 0 && (
          <div style={{ position: "absolute", left: 0, right: 0, top: 300, display: "flex", justifyContent: "center" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                background: C.red,
                color: C.white,
                fontFamily,
                fontWeight: 800,
                fontSize: 76,
                padding: "18px 44px",
                borderRadius: 24,
                boxShadow: "0 20px 60px rgba(251,76,92,0.45)",
                rotate: "-5deg",
                opacity: Math.min(1, stamp * 2),
                scale: String(1.6 - 0.6 * stamp),
              }}
            >
              <Loop size={70} color={C.white} stroke={3} style={{ rotate: `${t * 240}deg` }} />
              OTRA VEZ.
            </div>
          </div>
        )}
      </Card>
      {handIn > 0 && away < 1 && (
        <div
          style={{
            position: "absolute",
            left: hx - 10 + 260 * away,
            top: hy - 18 + 120 * away,
            opacity: handIn * (1 - away),
            scale: String(tap),
            filter: "drop-shadow(0 10px 20px rgba(0,0,0,0.5))",
          }}
        >
          <div style={{ background: C.white, borderRadius: 40, padding: 10, display: "flex" }}>
            <Hand size={62} color={C.ink} stroke={2.2} />
          </div>
        </div>
      )}
    </>
  );
};

/** Batería que se descarga. */
const Battery: React.FC<{ level: number }> = ({ level }) => {
  const color = level > 0.5 ? C.green : level > 0.25 ? C.yellow : C.red;
  return (
    <div style={{ display: "flex", alignItems: "center" }}>
      <div style={{ width: 300, height: 130, borderRadius: 26, border: `7px solid ${C.white}`, padding: 10, boxSizing: "border-box" }}>
        <div style={{ width: `${level * 100}%`, height: "100%", borderRadius: 14, background: color, boxShadow: `0 0 26px ${color}` }} />
      </div>
      <div style={{ width: 20, height: 52, borderRadius: "0 10px 10px 0", background: C.white, marginLeft: 6 }} />
    </div>
  );
};

const StatCard: React.FC<{
  at: number;
  top: number;
  value: string;
  color: string;
  bar: number;
  source: string;
  children: React.ReactNode;
}> = ({ at, top, value, color, bar, source, children }) => (
  <Card at={at} style={{ top, height: 290, padding: "34px 44px 0", boxSizing: "border-box" }}>
    <div style={{ display: "flex", alignItems: "center", gap: 34 }}>
      <span style={{ fontFamily, fontWeight: 800, fontSize: 150, color, letterSpacing: -6, lineHeight: 1, textShadow: `0 0 40px ${color}55`, minWidth: 330 }}>
        {value}
      </span>
      <div style={{ fontFamily, fontWeight: 800, fontSize: 36, lineHeight: 1.18, color: C.white }}>{children}</div>
    </div>
    <div style={{ marginTop: 26 }}>
      <Bar value={bar} color={color} height={16} />
    </div>
    <div style={{ position: "absolute", right: 44, bottom: 18, fontFamily, fontSize: 22, color: C.muted }}>{source}</div>
  </Card>
);

/** Escena 2: agotados y sin tiempo. */
const Stats: React.FC = () => {
  const t = useT();
  const level = interpolate(t, [9.8, T.agotado], [0.68, 0.1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const blink = t > T.agotado ? 0.55 + 0.45 * Math.abs(Math.cos((t - T.agotado) * 5)) : 1;
  return (
    <>
      <Card at={9.6} style={{ top: 290, height: 250, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 54px", boxSizing: "border-box" }}>
        <div>
          <Label>TU ENERGÍA</Label>
          <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 14 }}>
            <Moon size={46} color={C.yellow} stroke={2.2} />
            <span style={{ fontFamily, fontWeight: 800, fontSize: 52, color: C.white }}>01:15</span>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 26, opacity: blink }}>
          <Battery level={level} />
          <span style={{ fontFamily, fontWeight: 800, fontSize: 54, color: level < 0.25 ? C.red : C.white, minWidth: 120 }}>
            {Math.round(level * 100)}%
          </span>
        </div>
      </Card>
      <StatCard at={9.78} top={580} value={`${countUp(t, T.pct81, T.pct81 + 0.8, 81)}%`} color={C.red} bar={ramp(t, T.pct81, T.pct81 + 0.8) * 0.81} source="Fuente: Enji, 2025">
        DE LOS DUEÑOS DE PYME
        <br />
        DICE ESTAR <span style={{ color: C.red }}>AGOTADO</span>
      </StatCard>
      <StatCard at={13.56} top={910} value={`${countUp(t, T.pct70, T.pct70 + 0.8, 70)}%`} color={C.yellow} bar={ramp(t, T.pct70, T.pct70 + 0.8) * 0.7} source="Fuente: Fiverr, 2025">
        LE DEDICA <span style={{ color: C.yellow }}>MENOS DE</span>
        <br />
        <span style={{ color: C.yellow }}>5 HORAS</span> A LA SEMANA
        <br />A SU MARKETING
      </StatCard>
    </>
  );
};

const AUTO = [
  { Icon: ImagePost, title: "Publicaciones", sub: "12 programadas este mes", at: T.publicaciones },
  { Icon: Megaphone, title: "Anuncios", sub: "3 activos, ajustados cada semana", at: T.anuncios },
  { Icon: Users, title: "Seguimiento de clientes", sub: "Mensajes y contactos al día", at: T.seguimiento + 0.3 },
];

/** Escena 3: Sella se encarga, tú revisas resultados. */
const Panel: React.FC = () => {
  const t = useT();
  const glow = ramp(t, T.panel, T.panel + 0.3) * (1 - 0.5 * ramp(t, T.panel + 0.6, T.panel + 1.2));
  const res = pop(t, T.tu);
  const line = ramp(t, T.tu + 0.1, T.tu + 1.1);
  return (
    <>
      <Card at={18.45} glow style={{ top: 290, height: 830, boxShadow: `0 0 ${60 + 80 * glow}px rgba(25,226,165,${0.18 + 0.3 * glow})` }}>
        <PanelHeader />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "28px 40px 18px" }}>
          <Label>TU MARKETING · HOY</Label>
          <Chip color={C.green} solid p={pop(t, T.panel + 0.2)}>
            PENDIENTES: 0
          </Chip>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 16, padding: "0 40px" }}>
          {AUTO.map(({ Icon, title, sub, at }, i) => {
            const p = pop(t, T.encarga + i * 0.14);
            const done = pop(t, at, 30, 12);
            const on = done > 0.3;
            return (
              <div
                key={title}
                style={{
                  height: 118,
                  borderRadius: 26,
                  background: C.cardHi,
                  border: `2.5px solid ${on ? C.green : "#222d5e"}`,
                  display: "flex",
                  alignItems: "center",
                  gap: 24,
                  padding: "0 28px",
                  ...popStyle(p, 24),
                }}
              >
                <Icon size={56} color={on ? C.green : C.slate} stroke={1.8} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily, fontWeight: 800, fontSize: 34, color: C.white }}>{title}</div>
                  <div style={{ fontFamily, fontWeight: 500, fontSize: 25, color: C.muted }}>{sub}</div>
                </div>
                {on ? (
                  <div style={{ display: "flex", alignItems: "center", gap: 14, ...popStyle(done, 0) }}>
                    <span style={{ fontFamily, fontWeight: 700, fontSize: 20, letterSpacing: 2, color: C.green }}>SELLA</span>
                    <div style={{ width: 58, height: 58, borderRadius: 29, background: C.green, display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <Check size={38} color={C.ink} stroke={3.6} />
                    </div>
                  </div>
                ) : (
                  <div
                    style={{
                      width: 52,
                      height: 52,
                      borderRadius: 26,
                      border: `5px solid ${C.muted2}`,
                      borderTopColor: C.green,
                      rotate: `${t * 400}deg`,
                    }}
                  />
                )}
              </div>
            );
          })}
        </div>
        {/* Resultados */}
        <div
          style={{
            position: "absolute",
            left: 40,
            right: 40,
            bottom: 36,
            height: 172,
            borderRadius: 26,
            background: "linear-gradient(90deg, rgba(25,226,165,0.12), rgba(25,226,165,0.03))",
            border: `2.5px solid ${C.green}`,
            display: "flex",
            alignItems: "center",
            gap: 26,
            padding: "0 30px",
            ...popStyle(res, 24),
          }}
        >
          <div style={{ flex: 1 }}>
            <Label style={{ color: C.green }}>RESULTADOS DE LA SEMANA</Label>
            <svg width={420} height={90} style={{ marginTop: 6 }}>
              <defs>
                <clipPath id="resLine">
                  <rect x={0} y={0} width={420 * line} height={90} />
                </clipPath>
              </defs>
              <path
                d="M 6 78 C 70 70, 110 64, 160 52 S 260 40, 300 28 S 380 12, 414 8"
                stroke={C.green}
                strokeWidth={7}
                fill="none"
                strokeLinecap="round"
                clipPath="url(#resLine)"
                style={{ filter: "drop-shadow(0 0 10px rgba(25,226,165,0.6))" }}
              />
            </svg>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              background: C.green,
              color: C.ink,
              borderRadius: 40,
              padding: "16px 26px",
              fontFamily,
              fontWeight: 800,
              fontSize: 30,
              ...popStyle(pop(t, T.tu + 0.45), 10),
            }}
          >
            <Spark size={34} color={C.ink} stroke={3} /> TÚ: REVISAR
          </div>
        </div>
      </Card>
      <FooterPill at={25.6} top={1162} />
    </>
  );
};

export const AnuncioG: React.FC = () => {
  return (
    <AbsoluteFill>
      <Background />
      <Scene from={0} to={9.6}>
        <Manual />
      </Scene>
      <Scene from={9.6} to={18.45}>
        <Stats />
      </Scene>
      <Scene from={18.45} to={27.35}>
        <Panel />
      </Scene>
      <Scene from={27.35} to={voz.duration + 1}>
        <CtaScene from={27.35} cta={voz.ctaStart} />
      </Scene>
      <Logo />
      <Captions words={voz.words} />
      <Audio src={staticFile("audio/anuncio-G.wav")} />
    </AbsoluteFill>
  );
};

export const durationG = voz.duration;
