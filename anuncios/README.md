# Anuncios Sella — F (crecer) y G (marketing a mano)

Dos anuncios verticales nuevos (1080×1920, 30 fps) con la misma estética y estructura de los
anuncios A–E: gancho con dolor → dato con fuente → "Sella…" + Panel Sella → CTA con calendario.

| Video | Dolor | Duración |
|---|---|---|
| `videos/Anuncio_F_-_V1_crecer_negocio.mp4` | Querer hacer crecer el negocio | 29,6 s |
| `videos/Anuncio_G_-_V1_marketing_a_mano.mp4` | Administrar todo el marketing a mano | 33,7 s |

## Guiones

**F — Crecer**
> ¿Quieres hacer crecer tu negocio? Las ganas no te faltan… te falta un plan.
> El 84% de las pymes parte el año con planes para crecer. Pero las que tienen un plan de
> marketing tienen 3 veces más probabilidades de que les funcione.
> Sella arma tu plan de crecimiento y lo ejecuta: anuncios, web y seguimiento de clientes, paso a paso.
> Entra a nuestra web y agenda una llamada de 30 minutos. Revisamos tu caso.

**G — Marketing a mano**
> ¿Sigues haciendo todo tu marketing a mano? Publicar, responder mensajes, ajustar anuncios,
> anotar clientes en un Excel… y mañana, otra vez.
> El 81% de los dueños de pyme dice estar agotado. Y el 70% le dedica menos de 5 horas a la semana a su marketing.
> Sella se encarga de todo eso por ti: publicaciones, anuncios y seguimiento de clientes, en un solo panel.
> Tú solo revisas los resultados.
> Entra a nuestra web y agenda una llamada de 30 minutos. Revisamos tu caso.

## Fuentes de los datos

- **84%** de los dueños de pymes empieza 2026 con planes para nuevas iniciativas de crecimiento —
  Novuna Business Finance, 2 de enero de 2026 (muestra de 1.000 dueños de pymes, Reino Unido).
- **3×**: los dueños con un plan de marketing documentado tienen 3 veces más probabilidades de calificar su
  marketing como efectivo — Enji, *State of Small Business 2025* (245 dueños, EE.UU., sept. 2025).
- **81%** de los dueños de pyme reporta burnout — Enji, *State of Small Business 2025*.
- **70%** de los dueños dedica menos de 5 horas a la semana a su marketing — Fiverr Small Business Survey,
  mayo 2025 (casi 6.000 negocios en 25 países).

Los paneles marcados "EJEMPLO ILUSTRATIVO" (12 publicaciones, 3 anuncios, etc.) son ilustrativos,
igual que en los anuncios A–E.

## Voz

- Cuerpo de cada anuncio: ElevenLabs, voz **Javier Riveros** (`HtFUbkhkGhVk2L0Z9I2L`), modelo `eleven_v3`
  con etiquetas de emoción al inicio (`[curious]`, `[tired] … [sighs]`). Tomas en `sella-anuncios/locucion/`.
- CTA final: el mismo clip de los anuncios A–E (`locucion/cta-original.wav`), que es idéntico en los cinco.
- Volumen igualado a los originales: −14,9 LUFS, pico −1,7 dBFS.

Para cambiar la voz: reemplaza `locucion/F-toma2.mp3` / `G-toma1.mp3` (y sus `.palabras.json`, tiempos por
palabra con whisper), ajusta los cortes en `scripts/armar_locucion.py` y vuelve a renderizar.

## Volver a renderizar

```bash
cd anuncios/sella-anuncios
npm i
python3 scripts/armar_locucion.py          # sólo si cambias la locución
npx remotion studio                         # vista previa
npx remotion render AnuncioF-Crecer ../videos/Anuncio_F_-_V1_crecer_negocio.mp4
npx remotion render AnuncioG-MarketingAMano ../videos/Anuncio_G_-_V1_marketing_a_mano.mp4
```

Código: `src/AnuncioF.tsx` y `src/AnuncioG.tsx` (escenas), `src/Cta.tsx` (calendario + botón),
`src/Captions.tsx` (subtítulos palabra por palabra), `src/ui.tsx` / `src/theme.ts` (estilo Sella).
La fuente Poppins va incluida en `public/fonts` (licencia OFL).
