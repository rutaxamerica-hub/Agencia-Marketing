import React from "react";
import { C } from "./theme";

type P = { size?: number; color?: string; stroke?: number; style?: React.CSSProperties };

const Svg: React.FC<P & { children: React.ReactNode; vb?: string }> = ({
  size = 48,
  color = C.white,
  stroke = 2,
  style,
  vb = "0 0 24 24",
  children,
}) => (
  <svg
    width={size}
    height={size}
    viewBox={vb}
    fill="none"
    stroke={color}
    strokeWidth={stroke}
    strokeLinecap="round"
    strokeLinejoin="round"
    style={style}
  >
    {children}
  </svg>
);

/** Sello verde del logo Sella. */
export const Seal: React.FC<{ size?: number }> = ({ size = 56 }) => {
  const n = 16;
  const pts: string[] = [];
  for (let i = 0; i <= 360; i += 3) {
    const a = (i * Math.PI) / 180;
    const r = 46 + 4 * Math.cos(n * a);
    pts.push(`${50 + r * Math.cos(a)},${50 + r * Math.sin(a)}`);
  }
  return (
    <svg width={size} height={size} viewBox="0 0 100 100">
      <polygon points={pts.join(" ")} fill={C.green} />
      <circle cx="50" cy="50" r="33" fill={C.green} stroke="#0b3b31" strokeWidth="4" />
      <text
        x="50"
        y="51"
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="Poppins"
        fontWeight={700}
        fontSize="40"
        fill="#0a1a3a"
      >
        S
      </text>
    </svg>
  );
};

export const Store: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M3 9.5 4.6 4h14.8L21 9.5" />
    <path d="M3 9.5c0 1.4 1.1 2.5 2.5 2.5S8 10.9 8 9.5c0 1.4 1.1 2.5 2.5 2.5S13 10.9 13 9.5c0 1.4 1.1 2.5 2.5 2.5S18 10.9 18 9.5c0 1.4 1.1 2.5 2.5 2.5" />
    <path d="M4.5 12v8h15v-8" />
    <path d="M10 20v-5h4v5" />
  </Svg>
);

export const PlusCircle: React.FC<P> = (p) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 8v8M8 12h8" />
  </Svg>
);

export const House: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M3 11 12 4l9 7" />
    <path d="M5.5 9.5V20h13V9.5" />
    <path d="M10 20v-5h4v5" />
  </Svg>
);

export const Megaphone: React.FC<P & { fill?: string }> = ({ fill, ...p }) => (
  <Svg {...p}>
    <path d="M3 10v4a1 1 0 0 0 1 1h3l8 5V4L7 9H4a1 1 0 0 0-1 1Z" fill={fill ?? "none"} />
    <path d="M7 15v4.5a1.5 1.5 0 0 0 3 0V16.5" />
    <path d="M18.5 9a4 4 0 0 1 0 6" />
  </Svg>
);

export const Chat: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M4 5h16v11H9l-5 4V5Z" />
    <path d="M8 9.5h8M8 12.5h5" />
  </Svg>
);

export const ImagePost: React.FC<P> = (p) => (
  <Svg {...p}>
    <rect x="3.5" y="3.5" width="17" height="17" rx="4" />
    <circle cx="12" cy="12" r="4" />
    <circle cx="17" cy="7" r="0.8" />
  </Svg>
);

export const Sheet: React.FC<P> = (p) => (
  <Svg {...p}>
    <rect x="3.5" y="4" width="17" height="16" rx="2" />
    <path d="M3.5 9h17M3.5 14h17M9.5 4v16" />
  </Svg>
);

export const Browser: React.FC<P> = (p) => (
  <Svg {...p}>
    <rect x="3" y="4" width="18" height="16" rx="2.5" />
    <path d="M3 8.5h18" />
    <path d="M6.5 6.2h.01M9 6.2h.01" />
    <path d="M7 13h6M7 16h4" />
  </Svg>
);

export const Users: React.FC<P> = (p) => (
  <Svg {...p}>
    <circle cx="9" cy="8.5" r="3.2" />
    <path d="M3.5 19.5c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5" />
    <circle cx="16.8" cy="9.5" r="2.5" />
    <path d="M15.8 14.6c2.2.1 4 1.6 4.6 4.4" />
  </Svg>
);

export const Clock: React.FC<P> = (p) => (
  <Svg {...p}>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </Svg>
);

export const Check: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M5 12.5 10 17 19 7.5" />
  </Svg>
);

export const XMark: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M6.5 6.5l11 11M17.5 6.5l-11 11" />
  </Svg>
);

export const ArrowRight: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M4 12h15M13 6l6 6-6 6" />
  </Svg>
);

export const Flag: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M5 21V4" />
    <path d="M5 4h12l-2.5 4L17 12H5" />
  </Svg>
);

export const Loop: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M20 12a8 8 0 1 1-2.6-5.9" />
    <path d="M20 4v4.5h-4.5" />
  </Svg>
);

export const Moon: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M19 14.5A7.5 7.5 0 0 1 9.5 5a7.5 7.5 0 1 0 9.5 9.5Z" />
  </Svg>
);

/** Mano apuntando: el "a mano". */
export const Hand: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M9 11V4.8a1.6 1.6 0 0 1 3.2 0V10" />
    <path d="M12.2 10V9a1.6 1.6 0 0 1 3.2 0v1.5" />
    <path d="M15.4 10.5a1.6 1.6 0 0 1 3.2 0V14c0 3.6-2.4 6.5-6 6.5h-.8c-2.2 0-3.6-.9-4.8-2.6L4.4 14.5a1.6 1.6 0 0 1 2.5-2L9 14.5" />
  </Svg>
);

export const Spark: React.FC<P> = (p) => (
  <Svg {...p}>
    <path d="M4 16l5-5 4 3 7-8" />
    <path d="M15 6h5v5" />
  </Svg>
);

/** Puntero del mouse para la CTA. */
export const Cursor: React.FC<{ size?: number }> = ({ size = 64 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path
      d="M5 3l13 7.5-5.6 1.4 3.4 6.4-2.6 1.4-3.4-6.5L5 17.5Z"
      fill="#ffffff"
      stroke="#0a1022"
      strokeWidth="1.4"
      strokeLinejoin="round"
    />
  </svg>
);
