import React from "react";
import { AbsoluteFill, interpolate, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import voz from "./data/voz-F.json";
import { C, ease, fontFamily, pop, popStyle, ramp, useT } from "./theme";
import { Background, Card, Chip, countUp, FooterPill, Label, Logo, PanelHeader, Pill, Scene, Source } from "./ui";
import { Captions } from "./Captions";
import { wordAt } from "./timing";
import { CtaScene } from "./Cta";
import { Confetti, Particles, Stamp } from "./fx";
import { Owner } from "./Owner";
import { Browser, Check, Flag, Megaphone, Users, XMark } from "./icons";

// Momentos clave, leídos de las palabras de la locución (voz-F.json).
const at = (text: string, nth = 0) => wordAt(voz.words, text, nth);
const T = {
  vendes: at("VENDES"),
  ganas: at("GANAS"),
  falta: at("FALTA", 1),
  plan: at("PLAN"),
  pct84: at("84%"),
  pero: at("PERO", 1),
  planMk: at("PLAN", 1),
  tres: at("3"),
  funcione: at("FUNCIONE"),
  sella: at("SELLA"),
  armamos: at("ARMAMOS"),
  anuncios: at("ANUNCIOS"),
  web: at("WEB"),
  seguimiento: at("SEGUIMIENTO"),
  clientes: at("CLIENTES"),
  entra: at("ENTRA"),
  agenda: at("AGENDA"),
  llamada: at("LLAMADA"),
  revisamos: at("REVISAMOS"),
};

// Cambios de escena, un poco antes de la frase que abre cada una.
const S = {
  hook: at("NO") - 0.2,
  ganas: at("EL") - 0.15,
  pct: T.pero - 0.12,
  tres: at("EN") - 0.15,
  plan: T.entra - 0.4,
};

const MONTHS = ["ENE", "FEB", "MAR", "ABR"];

/** 1. ¿Quieres crecer… pero cada mes vendes lo mismo? */
const Hook: React.FC = () => {
  const t = useT();
  const flat = ramp(t, T.vendes, T.vendes + 0.5);
  return (
    <>
      <Pill at={-0.4} top={292}>
        SOLO PARA DUEÑOS DE PYMES
      </Pill>
      <Card at={-0.4} style={{ top: 392, height: 840 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "40px 46px 0" }}>
          <Label style={{ fontSize: 34 }}>TUS VENTAS</Label>
          <Chip color={C.green} style={{ fontSize: 28 }}>
            META: CRECER
          </Chip>
        </div>
        {/* Línea de meta */}
        <div style={{ position: "absolute", left: 46, right: 46, top: 196, height: 0, borderTop: `5px dashed ${C.green}`, opacity: 0.9 }} />
        <div style={{ position: "absolute", right: 60, top: 128, display: "flex", alignItems: "center", gap: 10 }}>
          <Flag size={58} color={C.green} stroke={2.6} />
          <span style={{ fontFamily, fontWeight: 800, fontSize: 40, color: C.green }}>META</span>
        </div>
        {/* Barras: mismo alto, mes tras mes */}
        {MONTHS.map((m, i) => {
          const wob = Math.sin(t * 3 + i * 1.3) * 5;
          const h = 330 + wob;
          return (
            <React.Fragment key={m}>
              <div
                style={{
                  position: "absolute",
                  left: 60 + i * 150,
                  bottom: 140,
                  width: 112,
                  height: h,
                  borderRadius: "20px 20px 6px 6px",
                  background: `linear-gradient(180deg, ${flat > 0.5 ? "#ff7a86" : "#7d8cd6"}, ${flat > 0.5 ? C.red : "#3e4f99"})`,
                }}
              />
              <div
                style={{
                  position: "absolute",
                  left: 40 + i * 150,
                  width: 152,
                  bottom: 140 + h + 14,
                  textAlign: "center",
                  fontFamily,
                  fontWeight: 800,
                  fontSize: 36,
                  color: C.white,
                }}
              >
                $3,2M
              </div>
              <div style={{ position: "absolute", left: 40 + i * 150, width: 152, bottom: 80, textAlign: "center", fontFamily, fontWeight: 700, fontSize: 32, color: C.muted }}>
                {m}
              </div>
            </React.Fragment>
          );
        })}
        {/* Línea plana roja */}
        <div
          style={{
            position: "absolute",
            left: 50,
            top: 840 - 140 - 330 - 6,
            height: 8,
            width: 600 * flat,
            borderRadius: 8,
            background: C.red,
            boxShadow: `0 0 24px ${C.red}`,
          }}
        />
        {/* Dueño mirando la meta */}
        <div style={{ position: "absolute", right: 34, bottom: 70 }}>
          <Owner width={220} armR={150 + Math.sin(t * 4) * 6} armL={10} headTilt={-12} />
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 300, display: "flex", justifyContent: "center" }}>
          <Stamp at={T.vendes + 0.15} size={58}>
            MISMAS VENTAS,
            <br />
            MES TRAS MES
          </Stamp>
        </div>
      </Card>
    </>
  );
};

/** 2. No es falta de ganas: es falta de un plan. */
const Badge: React.FC<{ ok: boolean; at: number; label: string; value: string; x: number }> = ({ ok, at, label, value, x }) => {
  const t = useT();
  const p = pop(t, at, 30, 10);
  const color = ok ? C.green : C.red;
  const shake = !ok && t > T.plan ? Math.sin((t - T.plan) * 50) * 10 * Math.max(0, 1 - (t - T.plan) * 3) : 0;
  return (
    <div style={{ position: "absolute", left: x - 210, top: 470, width: 420, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div
        style={{
          width: 380,
          height: 380,
          borderRadius: 190,
          border: `10px ${ok ? "solid" : "dashed"} ${color}`,
          background: ok ? `radial-gradient(circle, ${color}55, ${color}18)` : "rgba(251,76,92,0.06)",
          boxShadow: ok ? `0 0 ${80 * p}px ${color}66` : "none",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          translate: `${shake}px 0px`,
        }}
      >
        <div style={{ ...popStyle(p, 0) }}>{ok ? <Check size={230} color={C.white} stroke={3} /> : <XMark size={210} color={C.red} stroke={3} />}</div>
      </div>
      <div style={{ fontFamily, fontWeight: 800, fontSize: 76, color: C.white, marginTop: 34 }}>{label}</div>
      <div style={{ fontFamily, fontWeight: 800, fontSize: 56, color, opacity: p }}>{value}</div>
    </div>
  );
};

const Ganas: React.FC = () => (
  <>
    <Badge ok at={T.ganas - 0.1} label="GANAS" value="100%" x={290} />
    <Badge ok={false} at={T.falta} label="PLAN" value="0%" x={790} />
  </>
);

/** 3. 84% parte el año queriendo crecer. */
const Ring84: React.FC = () => {
  const t = useT();
  const v = ramp(t, T.pct84 - 0.1, T.pct84 + 0.9);
  const r = 250;
  const len = 2 * Math.PI * r;
  return (
    <>
      <div style={{ position: "absolute", left: 540 - 310, top: 330, width: 620, height: 620 }}>
        <svg width={620} height={620} style={{ position: "absolute", rotate: "-90deg" }}>
          <circle cx={310} cy={310} r={r} stroke="#1c2750" strokeWidth={44} fill="none" />
          <circle
            cx={310}
            cy={310}
            r={r}
            stroke={C.green}
            strokeWidth={44}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${len * 0.84 * v} ${len}`}
            style={{ filter: "drop-shadow(0 0 22px rgba(25,226,165,0.6))" }}
          />
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily, fontWeight: 800, color: C.white }}>
          <span style={{ fontSize: 230, letterSpacing: -8 }}>{countUp(t, T.pct84 - 0.1, T.pct84 + 0.9, 84)}</span>
          <span style={{ fontSize: 110, color: C.green, marginTop: 80 }}>%</span>
        </div>
      </div>
      <div style={{ position: "absolute", top: 1000, left: 40, right: 40, textAlign: "center", fontFamily, fontWeight: 800, fontSize: 58, lineHeight: 1.15, color: C.white, ...popStyle(pop(t, T.pct84 + 0.7), 24) }}>
        DE LAS PYMES PARTE EL AÑO
        <br />
        <span style={{ color: C.green }}>QUERIENDO CRECER</span>
      </div>
      <Source top={1170} at={T.pct84 + 1.1}>
        Fuente: Novuna Business Finance, 2026
      </Source>
    </>
  );
};

/** 4. Con un plan, 3 veces más probabilidades. */
const ThreeX: React.FC = () => {
  const t = useT();
  const left = ramp(t, T.pero, T.pero + 0.5);
  const one = ramp(t, T.planMk, T.planMk + 0.4);
  const three = pop(t, T.tres, 30, 11);
  const rightH = 150 * one + 320 * three;
  const party = pop(t, T.tres + 0.25, 30, 12);
  return (
    <Card at={S.pct - 0.05} style={{ top: 330, height: 930 }}>
      <div style={{ padding: "44px 50px 0" }}>
        <Label style={{ fontSize: 32, lineHeight: 1.35 }}>
          PROBABILIDAD DE QUE
          <br />
          TU MARKETING FUNCIONE
        </Label>
      </div>
      <div style={{ position: "absolute", left: 60, right: 60, bottom: 190, height: 4, background: C.border }} />
      {/* Sin plan */}
      <div style={{ position: "absolute", left: 120, bottom: 194, width: 280, height: 150 * left, borderRadius: "26px 26px 0 0", background: "#3a4677", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontFamily, fontWeight: 800, fontSize: 84, color: C.slate, opacity: left }}>1X</span>
      </div>
      {/* Con plan */}
      <div
        style={{
          position: "absolute",
          right: 120,
          bottom: 194,
          width: 280,
          height: rightH,
          borderRadius: "26px 26px 0 0",
          background: `linear-gradient(180deg, #4dffc6, ${C.green})`,
          boxShadow: "0 0 70px rgba(25,226,165,0.4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <span style={{ fontFamily, fontWeight: 800, fontSize: 84 + 70 * three, color: C.ink, letterSpacing: -4, opacity: one }}>
          {three > 0.05 ? "3X" : "1X"}
        </span>
      </div>
      {party > 0 && (
        <div style={{ position: "absolute", right: 120 + 140 - 70, bottom: 194 + rightH - 6, ...popStyle(party, 30) }}>
          <Owner width={140} armL={150 + Math.sin(t * 9) * 12} armR={150 - Math.sin(t * 9) * 12} />
        </div>
      )}
      <div style={{ position: "absolute", left: 120, width: 280, bottom: 120, textAlign: "center", fontFamily, fontWeight: 800, fontSize: 40, color: C.muted }}>SIN PLAN</div>
      <div style={{ position: "absolute", right: 120, width: 280, bottom: 120, textAlign: "center", fontFamily, fontWeight: 800, fontSize: 40, color: C.green }}>CON PLAN</div>
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 40, textAlign: "center", fontFamily, fontSize: 25, color: C.muted }}>
        Fuente: Enji, State of Small Business 2025
      </div>
      <Confetti at={T.funcione} x={540 + 160} y={360} />
    </Card>
  );
};

/** 5. Sella arma el plan y lo ejecuta: el dueño sube la escalera. */
const STEPS = [
  { Icon: Megaphone, label: "ANUNCIOS", at: T.anuncios },
  { Icon: Browser, label: "WEB", at: T.web },
  { Icon: Users, label: "SEGUIMIENTO", at: T.seguimiento },
];
const STEP_W = 262;
const STEP_X = [150, 412, 674];
const STEP_TOP = [480, 320, 160]; // y (relativo al área de la escalera) del borde superior de cada escalón
const GROUND = 720;

const Stairs: React.FC = () => {
  const t = useT();
  const build = ramp(t, T.armamos - 0.1, T.armamos + 0.6);
  // Posición del dueño: salta de escalón en escalón.
  const spots = [
    { x: 14, y: GROUND },
    ...STEPS.map((s, i) => ({ x: STEP_X[i] + STEP_W / 2 - 90, y: STEP_TOP[i] })),
  ];
  let ox = spots[0].x;
  let oy = spots[0].y;
  STEPS.forEach((s, i) => {
    const k = ramp(t, s.at - 0.05, s.at + 0.3, ease);
    if (k > 0) {
      ox = interpolate(k, [0, 1], [spots[i].x, spots[i + 1].x]);
      oy = interpolate(k, [0, 1], [spots[i].y, spots[i + 1].y]) - Math.sin(Math.PI * k) * 80;
    }
  });
  const win = t > T.clientes;
  return (
    <>
      <Card at={S.tres} glow style={{ top: 300, height: 930 }}>
        <PanelHeader />
        <div style={{ padding: "30px 44px 0" }}>
          <Label style={{ fontSize: 32 }}>TU PLAN DE CRECIMIENTO</Label>
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 170, height: 760 }}>
          {STEPS.map(({ Icon, label, at }, i) => {
            const on = pop(t, at, 30, 12);
            const h = (GROUND - STEP_TOP[i]) * build;
            return (
              <div
                key={label}
                style={{
                  position: "absolute",
                  left: STEP_X[i],
                  width: STEP_W - 10,
                  top: GROUND - h,
                  height: h,
                  borderRadius: "24px 24px 0 0",
                  background: on > 0.3 ? `linear-gradient(180deg, #4dffc6, ${C.green})` : C.cardHi,
                  border: `3px solid ${on > 0.3 ? C.green : "#2a3670"}`,
                  boxShadow: on > 0.3 ? "0 0 50px rgba(25,226,165,0.35)" : "none",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  paddingTop: 34,
                  gap: 10,
                  overflow: "hidden",
                }}
              >
                <Icon size={76} color={on > 0.3 ? C.ink : C.slate} stroke={2} />
                <span style={{ fontFamily, fontWeight: 800, fontSize: label.length > 8 ? 30 : 38, color: on > 0.3 ? C.ink : C.white }}>{label}</span>
              </div>
            );
          })}
          <div style={{ position: "absolute", right: 6, top: 30, ...popStyle(pop(t, T.armamos + 0.3), 10), rotate: `${Math.sin(t * 5) * 4}deg` }}>
            <Flag size={110} color={C.green} stroke={2.4} />
          </div>
          <div style={{ position: "absolute", left: ox, top: oy - 238 }}>
            <Owner width={130} armL={win ? 150 + Math.sin(t * 9) * 12 : 20} armR={win ? 150 - Math.sin(t * 9) * 12 : 20} />
          </div>
        </div>
        <Confetti at={T.clientes} x={800} y={300} />
      </Card>
      <FooterPill at={T.clientes + 0.1} top={1250} />
    </>
  );
};

export const AnuncioF: React.FC = () => {
  return (
    <AbsoluteFill>
      <Background />
      <Particles />
      <Scene from={0} to={S.hook}>
        <Hook />
      </Scene>
      <Scene from={S.hook} to={S.ganas}>
        <Ganas />
      </Scene>
      <Scene from={S.ganas} to={S.pct}>
        <Ring84 />
      </Scene>
      <Scene from={S.pct} to={S.tres}>
        <ThreeX />
      </Scene>
      <Scene from={S.tres} to={S.plan}>
        <Stairs />
      </Scene>
      <Scene from={S.plan} to={voz.duration + 1}>
        <CtaScene from={S.plan} entra={T.entra} agenda={T.agenda} llamada={T.llamada} revisamos={T.revisamos} />
      </Scene>
      <Logo />
      <Captions words={voz.words} />
      <Audio src={staticFile("audio/anuncio-F.wav")} />
    </AbsoluteFill>
  );
};

export const durationF = voz.duration;
