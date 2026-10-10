import React from "react";
import { C } from "./theme";

const BODY = "#3e4f99";
const SKIN = "#5869b8";
const LEGS = "#2c3a7a";
const APRON = "#c8d2f3";

/**
 * Dueño de pyme en estilo plano (como el personaje del anuncio E).
 * Ángulos de brazo en grados: 0 = colgando, positivo = hacia afuera / arriba.
 */
export const Owner: React.FC<{
  width?: number;
  armL?: number;
  armR?: number;
  headTilt?: number;
  item?: "phone" | "none";
  sweat?: number; // 0–1
  style?: React.CSSProperties;
}> = ({ width = 240, armL = 8, armR = 8, headTilt = 0, item = "none", sweat = 0, style }) => {
  const h = (width * 440) / 240;
  return (
    <svg width={width} height={h} viewBox="0 0 240 440" style={{ overflow: "visible", ...style }}>
      <ellipse cx={120} cy={430} rx={84} ry={10} fill="rgba(0,0,0,0.35)" />
      {/* piernas */}
      <rect x={88} y={288} width={27} height={136} rx={13} fill={LEGS} />
      <rect x={125} y={288} width={27} height={136} rx={13} fill={LEGS} />
      <ellipse cx={99} cy={424} rx={24} ry={10} fill="#1b2452" />
      <ellipse cx={142} cy={424} rx={24} ry={10} fill="#1b2452" />
      {/* brazo izquierdo (detrás del delantal) */}
      <g transform={`rotate(${armL} 72 172)`}>
        <line x1={72} y1={172} x2={72} y2={282} stroke={BODY} strokeWidth={28} strokeLinecap="round" />
        <circle cx={72} cy={290} r={16} fill={SKIN} />
      </g>
      {/* torso */}
      <rect x={60} y={146} width={120} height={166} rx={50} fill={BODY} />
      {/* delantal */}
      <path d="M84 150 L94 174 M156 150 L146 174" stroke={APRON} strokeWidth={6} strokeLinecap="round" />
      <rect x={93} y={172} width={54} height={40} rx={8} fill={APRON} />
      <path d="M78 206 H162 L168 314 Q120 326 72 314 Z" fill={APRON} />
      <rect x={100} y={238} width={40} height={26} rx={6} fill="none" stroke="#8f9bd0" strokeWidth={3.5} />
      {/* cuello y cabeza */}
      <rect x={108} y={126} width={24} height={30} rx={8} fill={SKIN} />
      <g transform={`rotate(${headTilt} 120 130)`}>
        <circle cx={120} cy={96} r={42} fill={SKIN} />
        <path d="M78 98 A42 42 0 0 1 162 98 Q152 70 120 68 Q88 70 78 98 Z" fill="#26326c" />
      </g>
      {/* brazo derecho */}
      <g transform={`rotate(${-armR} 168 172)`}>
        <line x1={168} y1={172} x2={168} y2={282} stroke={BODY} strokeWidth={28} strokeLinecap="round" />
        <circle cx={168} cy={290} r={16} fill={SKIN} />
        {item === "phone" && (
          <g transform="translate(150 262) rotate(8)">
            <rect x={0} y={0} width={38} height={64} rx={8} fill="#0d142c" stroke="#9aa6d6" strokeWidth={3} />
            <rect x={6} y={10} width={26} height={40} rx={3} fill={C.green} opacity={0.85} />
          </g>
        )}
      </g>
      {/* gotas de sudor */}
      {sweat > 0 && (
        <g opacity={sweat}>
          <path d="M60 70 q-7 12 0 16 q7 -4 0 -16 Z" fill="#8fd3ff" />
          <path d="M178 58 q-6 10 0 13 q6 -3 0 -13 Z" fill="#8fd3ff" />
        </g>
      )}
    </svg>
  );
};
