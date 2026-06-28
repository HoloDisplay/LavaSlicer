# Magma IEEE Paper Draft

This directory contains the IEEE-style two-column paper draft for the Magma
hybrid FFF mold injection project.

## Files

- `magma_ieee.tex` - IEEEtran LaTeX source.
- `magma_ieee_paper.pdf` - compiled four-page PDF.
- `figures/` - QuiverAI-generated figure assets used by the paper.

## Build

The paper was compiled with Tectonic:

```bash
tectonic -X compile --outdir output magma_ieee.tex
```

The generated PDF will be written to `output/magma_ieee.pdf`.
