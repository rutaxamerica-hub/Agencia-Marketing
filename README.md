# Agencia Marketing

Archivos del rediseño de la tienda Shopify de EJE: el tema original como respaldo y los scripts que generan las plantillas nuevas.

## Documentos

- [Descripciones originales de productos](shopify/original/productos_descripciones_originales.md): textos de productos, colecciones y páginas publicados antes del rediseño (respaldo del 2026-09-26). Léelo para recuperar o comparar el copy anterior.

## Carpetas

- `shopify/original/`: copia del tema tal como estaba (bloques, secciones, snippets, plantillas y configuración en Liquid/JSON). Es la base que leen los scripts de `shopify/new/`.
- `shopify/new/`: scripts de Python que parten de las plantillas originales y escriben las nuevas en `templates/`, `sections/` y `config/`.
  - `lib.py`: utilidades comunes: cargar y guardar JSON del tema y armar bloques (texto, botones, imágenes, secciones).
  - `build_index.py`: página de inicio.
  - `build_product.py`: ficha de producto.
  - `build_quiz.py`: página del diagnóstico (quiz).
  - `build_rest.py`: colección, carrito, header, footer y `settings_data.json`.
  - `productos.py` y `productos_mutation.graphql`: contenido nuevo de productos y la mutación GraphQL para subirlo.
