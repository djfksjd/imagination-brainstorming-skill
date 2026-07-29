<div align="center">

# ◇ Imagination Brainstorming

**Convierte una idea elegida en un concepto capaz de resistir la realidad.**

[![Tests](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml/badge.svg)](https://github.com/djfksjd/imagination-brainstorming-skill/actions/workflows/tests.yml)
![Versión](https://img.shields.io/badge/version-0.4.1-db2777)
![Preferencia](https://img.shields.io/badge/blind_preference-83.3%25-16a34a)
![Licencia](https://img.shields.io/badge/license-MIT-0f766e)

[English](README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (Brasil)](README.pt-BR.md)

</div>

---

> [!TIP]
> Para la mayoría recomendamos
> [Imagination](https://github.com/djfksjd/imagination): genera direcciones,
> espera tu elección y conecta la elegida con este taller.

Imagination Brainstorming empieza **después de elegir una dirección**. Antes de
implementar, contrasta la idea con su objetivo, restricciones, mejor alternativa,
operación cotidiana y modo de fallo propio.

```text
Idea elegida → control de restricciones → prueba de presión → concepto decisorio
```

## Ejemplo

```text
Usa $imagination-brainstorming para desarrollar esta opción. Incluye el primer
uso real, trabajo recurrente, fallo propio, falsador y siguiente decisión.
```

## Resultado medido

| Métrica | Frente a un prompt fuerte |
|---|---:|
| Preferencia para planificación | **25–5 (83,3 %)** |
| Aplicabilidad | **+1,37** |
| Ajuste decisorio | **+0,59** |
| Claridad causal | **+0,59** |
| Robustez | **+0,53** |

Es un resultado de jueces modelo en una prueba ciega prerregistrada, no una
garantía universal.

## Instalación independiente

```bash
curl -fsSL https://raw.githubusercontent.com/djfksjd/imagination-brainstorming-skill/main/install.sh | bash
```

Para la divergencia inicial, usa
[Imagination Engine](https://github.com/djfksjd/imagination-engine-skill).
El flujo anterior solo se conserva en `legacy/v0.3.0/`. Licencia MIT.
