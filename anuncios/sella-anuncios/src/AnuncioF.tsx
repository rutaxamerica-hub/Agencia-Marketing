import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import voz from "./data/voz-F.json";
import { C, fontFamily, pop, popStyle, ramp, useT } from "./theme";
import { Background, Bar, Card, Chip, countUp, FooterPill, Label, Logo, PanelHeader, Pill, Scene, Source } from "./ui";
import { Captions } from "./Captions";
import { CtaScene } from "./Cta";
import { Browser, Check, Flag, Megaphone, Store, Users, XMark } from "./icons";

// Momentos clave de la locución (segundos), tomados de voz-F.json.
const T = {
  crecer: 0.5,
  negocio: 1.04,
  ganas: 2.18,
  falta: 3.72,
  plan: 4.4,
  pct84: 5.5,
  pero: 9.88,
  planMk: 10.74,
  tres: 12.2,
  funcione: 14.98,
  sella: 16.25,
  arma: 16.79,
  anuncios: 19.25,
  web: 19.97,
  seguimiento: 20.45,
  paso: 21.95,
};

/** Escena 1: quieres crecer, pero falta el plan. */
const Hook: React.FC = () => {
  const t = useT();
  const big = ramp(t, -0.2, 0.8);
  const arc = ramp(t, 0.1, 1.0);
  const q = pop(t, T.negocio, 30, 8);
  const ganas = ramp(t, T.ganas, T.ganas + 0.7);
  const planRed = ramp(t, T.falta, T.falta + 0.25);
  const stamp = pop(t, T.plan, 30, 9);
  return (
    <>
      <Pill at={-0.4} top={292}>
        SOLO PARA DUEÑOS DE PYMES
      </Pill>
      <Card at={-0.4} style={{ top: 400, height: 470 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "34px 40px 0" }}>
          <Label>TU NEGOCIO</Label>
          <Chip color={C.green} p={pop(t, T.crecer)}>
            META: CRECER
          </Chip>
        </div>
        {/* Hoy */}
        <div style={{ position: "absolute", left: 70, top: 200, width: 200, textAlign: "center" }}>
          <Store size={170} color={C.slate} stroke={1.6} />
          <Label style={{ marginTop: 6 }}>HOY</Label>
        </div>
        {/* Camino punteado */}
        <svg width={420} height={220} style={{ position: "absolute", left: 250, top: 150 }}>
          <defs>
            <clipPath id="arcClip">
              <rect x={0} y={0} width={420 * arc} height={220} />
            </clipPath>
          </defs>
          <path
            d="M 20 190 C 140 40, 280 20, 380 70"
            stroke={C.muted}
            strokeWidth={6}
            strokeDasharray="2 18"
            strokeLinecap="round"
            fill="none"
            clipPath="url(#arcClip)"
          />
          <path d="M 362 46 L 392 74 L 354 86" stroke={C.muted} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" opacity={arc > 0.95 ? 1 : 0} />
        </svg>
        <div
          style={{
            position: "absolute",
            left: 390,
            top: 120,
            fontFamily,
            fontWeight: 800,
            fontSize: 130,
            color: C.red,
            textShadow: "0 0 40px rgba(251,76,92,0.5)",
            ...popStyle(q, 30),
            rotate: `${Math.sin(t * 6) * 6 * q}deg`,
          }}
        >
          ?
        </div>
        {/* Meta */}
        <div
          style={{
            position: "absolute",
            right: 50,
            top: 104,
            width: 320,
            height: 336,
            borderRadius: 30,
            border: `4px dashed ${C.green}`,
            background: "rgba(25,226,165,0.06)",
            boxShadow: `0 0 ${50 * big}px rgba(25,226,165,0.25)`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            ...popStyle(big),
          }}
        >
          <Store size={228} color={C.green} stroke={1.3} />
          <Label style={{ color: C.green, marginTop: 4 }}>TU META</Label>
        </div>
        {/* Sello rojo */}
        {stamp > 0 && (
          <div
            style={{
              position: "absolute",
              left: 0,
              right: 0,
              top: 175,
              display: "flex",
              justifyContent: "center",
            }}
          >
            <div
              style={{
                background: C.red,
                color: C.white,
                fontFamily,
                fontWeight: 800,
                fontSize: 60,
                lineHeight: 1.08,
                textAlign: "center",
                padding: "20px 40px",
                borderRadius: 22,
                boxShadow: "0 20px 60px rgba(251,76,92,0.45)",
                rotate: "-5deg",
                opacity: Math.min(1, stamp * 2),
                scale: String(1.6 - 0.6 * stamp),
              }}
            >
              SIN PLAN NO HAY
              <br />
              CRECIMIENTO.
            </div>
          </div>
        )}
      </Card>

      <Card at={1.9} style={{ top: 910, height: 330, padding: "44px 46px", boxSizing: "border-box" }}>
        <Row label="GANAS" value={`${countUp(t, T.ganas, T.ganas + 0.7, 100)}%`} color={C.green}>
          <Bar value={ganas} color={C.green} height={30} glow />
        </Row>
        <div style={{ height: 52 }} />
        <Row label="PLAN" value="0%" color={planRed > 0.5 ? C.red : C.muted}>
          <div
            style={{
              height: 30,
              borderRadius: 30,
              background: "#1a2448",
              border: `3px solid rgba(251,76,92,${planRed})`,
              boxSizing: "border-box",
            }}
          />
        </Row>
        <div style={{ position: "absolute", right: 46, top: 46 }}>
          <Chip color={C.green} solid p={pop(t, T.ganas + 0.6)}>
            <Check size={26} color={C.ink} stroke={3.4} /> DE SOBRA
          </Chip>
        </div>
        <div style={{ position: "absolute", right: 46, bottom: 46 }}>
          <Chip color={C.red} p={pop(t, T.falta + 0.2)}>
            <XMark size={26} color={C.red} stroke={3.4} /> SIN PLAN
          </Chip>
        </div>
      </Card>
    </>
  );
};

const Row: React.FC<{ label: string; value: string; color: string; children: React.ReactNode }> = ({
  label,
  value,
  color,
  children,
}) => (
  <div>
    <div style={{ display: "flex", alignItems: "baseline", gap: 20, marginBottom: 18 }}>
      <span style={{ fontFamily, fontWeight: 800, fontSize: 44, color: C.white }}>{label}</span>
      <span style={{ fontFamily, fontWeight: 800, fontSize: 44, color }}>{value}</span>
    </div>
    {children}
  </div>
);

/** Escena 2: 84% quiere crecer. */
const Ring84: React.FC = () => {
  const t = useT();
  const v = ramp(t, T.pct84 - 0.05, T.pct84 + 0.95);
  const r = 230;
  const len = 2 * Math.PI * r;
  return (
    <>
      <div style={{ position: "absolute", left: 540 - 290, top: 330, width: 580, height: 580, ...popStyle(pop(t, 5.2)) }}>
        <svg width={580} height={580} style={{ position: "absolute", rotate: "-90deg" }}>
          <circle cx={290} cy={290} r={r} stroke="#1c2750" strokeWidth={40} fill="none" />
          <circle
            cx={290}
            cy={290}
            r={r}
            stroke={C.green}
            strokeWidth={40}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={`${len * 0.84 * v} ${len}`}
            style={{ filter: "drop-shadow(0 0 18px rgba(25,226,165,0.55))" }}
          />
        </svg>
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily,
            fontWeight: 800,
            color: C.white,
          }}
        >
          <span style={{ fontSize: 200, letterSpacing: -6 }}>{countUp(t, T.pct84 - 0.05, T.pct84 + 0.95, 84)}</span>
          <span style={{ fontSize: 100, color: C.green, marginTop: 70 }}>%</span>
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          top: 965,
          left: 60,
          right: 60,
          textAlign: "center",
          fontFamily,
          fontWeight: 800,
          fontSize: 50,
          lineHeight: 1.18,
          color: C.white,
          ...popStyle(pop(t, 6.5), 24),
        }}
      >
        DE LAS PYMES PARTE EL AÑO
        <br />
        <span style={{ color: C.green }}>CON PLANES PARA CRECER</span>
      </div>
      <Source top={1120} at={7.0}>
        Fuente: Novuna Business Finance, 2026
      </Source>
    </>
  );
};

/** Escena 3: con un plan, 3 veces más probabilidades. */
const ThreeX: React.FC = () => {
  const t = useT();
  const left = ramp(t, T.pero + 0.1, T.pero + 0.7);
  const right1 = ramp(t, T.planMk, T.planMk + 0.5);
  const right3 = pop(t, T.tres, 30, 11);
  const rightH = 110 * right1 + 220 * right3;
  const badge = pop(t, T.funcione, 30, 10);
  return (
    <>
      <Card at={9.72} style={{ top: 290, height: 200, display: "flex", alignItems: "center", gap: 36, padding: "0 48px", boxSizing: "border-box" }}>
        <span style={{ fontFamily, fontWeight: 800, fontSize: 120, color: C.green, letterSpacing: -4 }}>84%</span>
        <span style={{ fontFamily, fontWeight: 700, fontSize: 38, color: C.white, lineHeight: 1.2 }}>
          QUIERE CRECER
          <br />
          <span style={{ color: C.muted }}>ESTE AÑO</span>
        </span>
      </Card>
      <Card at={T.pero} style={{ top: 530, height: 740 }}>
        <div style={{ padding: "40px 46px 0" }}>
          <Label>PROBABILIDAD DE QUE TU MARKETING FUNCIONE</Label>
        </div>
        {/* Columnas */}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 150, height: 470 }}>
          <div style={{ position: "absolute", left: 60, right: 60, bottom: 0, height: 3, background: C.border }} />
          {/* Sin plan */}
          <div style={{ position: "absolute", left: 150, bottom: 0, width: 230, height: 110 * left, borderRadius: "22px 22px 0 0", background: "#3a4677" }} />
          <div
            style={{
              position: "absolute",
              left: 150,
              width: 230,
              bottom: 110 * left + 16,
              textAlign: "center",
              fontFamily,
              fontWeight: 800,
              fontSize: 70,
              color: C.slate,
              opacity: left,
            }}
          >
            1X
          </div>
          {/* Con plan */}
          <div
            style={{
              position: "absolute",
              right: 150,
              bottom: 0,
              width: 230,
              height: rightH,
              borderRadius: "22px 22px 0 0",
              background: C.green,
              boxShadow: "0 0 50px rgba(25,226,165,0.35)",
            }}
          />
          <div
            style={{
              position: "absolute",
              right: 150,
              width: 230,
              bottom: rightH + 12,
              textAlign: "center",
              fontFamily,
              fontWeight: 800,
              fontSize: 70 + 46 * right3,
              color: C.green,
              opacity: right1,
            }}
          >
            {right3 > 0.05 ? "3X" : "1X"}
          </div>
          {badge > 0 && (
            <div
              style={{
                position: "absolute",
                right: 112,
                bottom: rightH - 40,
                width: 76,
                height: 76,
                borderRadius: 38,
                background: C.white,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                ...popStyle(badge, 0),
              }}
            >
              <Check size={50} color={C.ink} stroke={3.4} />
            </div>
          )}
        </div>
        <div style={{ position: "absolute", left: 150, width: 230, bottom: 92, textAlign: "center", fontFamily, fontWeight: 800, fontSize: 32, color: C.muted }}>
          SIN PLAN
        </div>
        <div style={{ position: "absolute", right: 150, width: 230, bottom: 92, textAlign: "center", fontFamily, fontWeight: 800, fontSize: 32, color: C.green }}>
          CON PLAN
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 30, textAlign: "center", fontFamily, fontSize: 24, color: C.muted }}>
          Fuente: Enji, State of Small Business 2025
        </div>
      </Card>
    </>
  );
};

const STEPS = [
  { n: 1, Icon: Megaphone, title: "ANUNCIOS", sub: "Atraer clientes nuevos", at: T.anuncios },
  { n: 2, Icon: Browser, title: "WEB", sub: "Convertir visitas en ventas", at: T.web },
  { n: 3, Icon: Users, title: "SEGUIMIENTO", sub: "Que vuelvan a comprar", at: T.seguimiento + 0.25 },
];

/** Escena 4: Sella arma el plan y lo ejecuta. */
const Panel: React.FC = () => {
  const t = useT();
  const prog =
    ramp(t, T.anuncios, T.anuncios + 0.5) * 0.28 +
    ramp(t, T.web, T.web + 0.45) * 0.26 +
    ramp(t, T.seguimiento + 0.25, T.seguimiento + 0.7) * 0.26 +
    ramp(t, T.paso, T.paso + 0.5) * 0.2;
  return (
    <>
      <Card at={15.95} glow style={{ top: 290, height: 905 }}>
        <PanelHeader />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "30px 40px 20px" }}>
          <Label>TU PLAN DE CRECIMIENTO</Label>
          <Chip color={C.green} solid p={pop(t, T.paso)}>
            PASO A PASO
          </Chip>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 18, padding: "0 40px" }}>
          {STEPS.map(({ n, Icon, title, sub, at }, i) => {
            const p = pop(t, T.arma + i * 0.14);
            const done = pop(t, at, 30, 12);
            return (
              <div
                key={n}
                style={{
                  height: 124,
                  borderRadius: 26,
                  background: C.cardHi,
                  border: `2.5px solid ${done > 0.3 ? C.green : "#222d5e"}`,
                  display: "flex",
                  alignItems: "center",
                  gap: 26,
                  padding: "0 28px",
                  ...popStyle(p, 24),
                }}
              >
                <div
                  style={{
                    width: 68,
                    height: 68,
                    borderRadius: 34,
                    border: `3px solid ${done > 0.3 ? C.green : C.muted2}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily,
                    fontWeight: 800,
                    fontSize: 34,
                    color: done > 0.3 ? C.green : C.muted,
                  }}
                >
                  {n}
                </div>
                <Icon size={54} color={done > 0.3 ? C.green : C.slate} stroke={1.8} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontFamily, fontWeight: 800, fontSize: 36, color: C.white }}>{title}</div>
                  <div style={{ fontFamily, fontWeight: 500, fontSize: 26, color: C.muted }}>{sub}</div>
                </div>
                <div
                  style={{
                    width: 62,
                    height: 62,
                    borderRadius: 31,
                    background: done > 0.02 ? C.green : "transparent",
                    border: `3px solid ${done > 0.02 ? C.green : C.muted2}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    scale: String(1 + 0.25 * Math.sin(Math.PI * Math.min(1, done))),
                  }}
                >
                  {done > 0.02 && <Check size={40} color={C.ink} stroke={3.6} />}
                </div>
              </div>
            );
          })}
        </div>
        {/* Escalera de crecimiento */}
        <svg width={880} height={210} style={{ position: "absolute", left: 40, top: 665 }}>
          <defs>
            <clipPath id="stairs">
              <rect x={0} y={0} width={880 * prog} height={210} />
            </clipPath>
          </defs>
          <line x1={20} y1={180} x2={860} y2={180} stroke={C.muted2} strokeWidth={4} strokeDasharray="3 14" strokeLinecap="round" />
          <path
            d="M 20 180 L 230 180 L 230 132 L 450 132 L 450 84 L 670 84 L 670 36 L 800 36"
            stroke={C.green}
            strokeWidth={9}
            fill="none"
            strokeLinejoin="round"
            clipPath="url(#stairs)"
            style={{ filter: "drop-shadow(0 0 12px rgba(25,226,165,0.6))" }}
          />
          {[230, 450, 670].map((x, i) => (
            <circle key={x} cx={x} cy={180 - 48 * (i + 1)} r={11} fill={C.white} opacity={prog * 880 > x ? 1 : 0} />
          ))}
        </svg>
        <div style={{ position: "absolute", left: 818, top: 640, ...popStyle(pop(t, T.paso + 0.35), 10) }}>
          <Flag size={74} color={C.green} stroke={2.4} />
        </div>
        <div style={{ position: "absolute", left: 60, top: 860, fontFamily, fontWeight: 700, fontSize: 22, letterSpacing: 3, color: C.muted2 }}>
          SIN PLAN
        </div>
        <div style={{ position: "absolute", right: 46, top: 860, fontFamily, fontWeight: 700, fontSize: 22, letterSpacing: 3, color: C.green, opacity: ramp(t, T.paso + 0.3, T.paso + 0.6) }}>
          META
        </div>
      </Card>
      <FooterPill at={T.paso - 0.1} top={1232} />
    </>
  );
};

export const AnuncioF: React.FC = () => {
  return (
    <AbsoluteFill>
      <Background />
      <Scene from={0} to={5.15}>
        <Hook />
      </Scene>
      <Scene from={5.15} to={9.7}>
        <Ring84 />
      </Scene>
      <Scene from={9.7} to={15.95}>
        <ThreeX />
      </Scene>
      <Scene from={15.95} to={23.25}>
        <Panel />
      </Scene>
      <Scene from={23.25} to={voz.duration + 1}>
        <CtaScene from={23.25} cta={voz.ctaStart} />
      </Scene>
      <Logo />
      <Captions words={voz.words} />
      <Audio src={staticFile("audio/anuncio-F.wav")} />
    </AbsoluteFill>
  );
};

export const durationF = voz.duration;
