# Anuncios Sella — F (crecer) y G (marketing a mano)

Dos anuncios verticales nuevos (1080×1920, 30 fps) con la misma estética y estructura de los
anuncios A–E: gancho con dolor → dato con fuente → "Sella…" + Panel Sella → CTA con calendario.

| Video | Dolor | Duración |
|---|---|---|
| `videos/Anuncio_F_-_V3_crecer_negocio.mp4` | Querer hacer crecer el negocio | 27,1 s |
| `videos/Anuncio_G_-_V3_marketing_a_mano.mp4` | Administrar todo el marketing a mano | 28,9 s |

V3: misma voz chilena y mismas escenas de la V2, pero con la locución más pausada y natural (ritmo parecido
a A–E), respiros en comas y puntos, un timbre más suave y ganchos nuevos con más intención. V1 y V2 quedaron
en el historial de git.

## Guiones

**F — Crecer**
> ¿Quieres hacer crecer tu negocio? Pero… cada mes vendes lo mismo. No es falta de ganas. Es falta de un plan.
> El 84% de las pymes parte el año queriendo crecer, pero las que tienen un plan de marketing tienen
> tres veces más probabilidades de que les funcione.
> En Sella armamos tu plan y lo ejecutamos: anuncios, web y seguimiento de clientes.
> Entra a nuestra web y agenda una llamada de 30 minutos. Revisamos tu caso.

**G — Marketing a mano**
> ¿Sigues haciendo todo tu marketing… a mano? Publicar, responder mensajes, ajustar anuncios,
> anotar clientes en un Excel… y mañana, todo de nuevo.
> El 81% de los dueños de pyme dice estar agotado. Y el 70% le dedica menos de cinco horas a la semana a su marketing.
> Sella se encarga de todo eso por ti, en un solo panel. Tú solo revisas los resultados.
> Entra a nuestra web y agenda una llamada de 30 minutos. Revisamos tu caso.

## Fuentes de los datos

- **84%** de los dueños de pymes empieza 2026 con planes para nuevas iniciativas de crecimiento —
  Novuna Business Finance, 2 de enero de 2026 (muestra de 1.000 dueños de pymes, Reino Unido).
- **3×**: los dueños con un plan de marketing documentado tienen 3 veces más probabilidades de calificar su
  marketing como efectivo — Enji, *State of Small Business 2025* (245 dueños, EE.UU., sept. 2025).
- **81%** de los dueños de pyme reporta burnout — Enji, *State of Small Business 2025*.
- **70%** de los dueños dedica menos de 5 horas a la semana a su marketing — Fiverr Small Business Survey,
  mayo 2025 (casi 6.000 negocios en 25 países).

Las cifras de ventas del gancho de F ($3,2M por mes) y los paneles marcados "EJEMPLO ILUSTRATIVO"
son ilustrativos, igual que en los anuncios A–E.

## Voz

- ElevenLabs, voz chilena **Cristian Cornejo — Español Chileno Fluido** (`ClNifCEVq1smkl4M3aTk`),
  modelo `eleven_multilingual_v2` (el que mejor conserva el acento). Tomas en `sella-anuncios/locucion/`.
- Ganchos regenerados (`F-cristian-gancho2`, `G-cristian-gancho2`): F hace una pausa después de
  "¿…tu negocio?" y G antes de "a mano", para que el dolor se escuche claro. El resto sale de
  `F-cristian-toma4` y `G-cristian-toma1`.
- `scripts/armar_locucion.py` arma la locución final:
  - baja la velocidad (gancho al 88 %, resto al 85 %, sin cambiar el timbre);
  - agrega respiros en comas y puntos, y pausas entre bloques;
  - ecualiza (menos nasal y menos siseo);
  - nivela a −14,9 LUFS, pico −1,5 dBTP, igual que A–E;
  - retranscribe con whisper para los subtítulos.
- Las escenas se sincronizan solas: `src/timing.ts` busca en `src/data/voz-*.json` el momento de cada palabra.

Para cambiar la voz: reemplaza las tomas en `locucion/` (y sus `.palabras.json`, tiempos por palabra con
whisper), ajusta los tramos en `scripts/armar_locucion.py`, corre el script y vuelve a renderizar (si cambia el
texto, revisa las palabras que buscan `T` y `S` en `src/AnuncioF.tsx` / `src/AnuncioG.tsx`).

## Volver a renderizar

```bash
cd anuncios/sella-anuncios
npm i
python3 scripts/armar_locucion.py          # sólo si cambias la locución (requiere ffmpeg y faster-whisper)
npx remotion studio                         # vista previa
npm run render:f
npm run render:g
```

Código: `src/AnuncioF.tsx` y `src/AnuncioG.tsx` (escenas), `src/Cta.tsx` (calendario + botón),
`src/Captions.tsx` (subtítulos palabra por palabra), `src/Owner.tsx` (personaje), `src/fx.tsx`
(notificaciones, sellos, confeti, partículas), `src/ui.tsx` / `src/theme.ts` (estilo Sella).
La fuente Poppins va incluida en `public/fonts` (licencia OFL).
