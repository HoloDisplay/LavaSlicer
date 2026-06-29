# IEEE Submission Checklist

This checklist tracks submission-facing requirements for the Magma paper package. It is based on current IEEE Author Center and IEEE PDF eXpress guidance as of 2026-06-28.

## Required Local Artifacts

- Final manuscript PDF: `output/pdf/magma_ieee_paper.pdf`
- PDF production report: `output/verification/pdf_production_check.md`
- IEEE submission readiness report: `output/verification/ieee_submission_check.md`
- PDF eXpress source archive: `output/submission/magma_ieee_pdf_express_source.zip`
- Local review bundle: `output/submission/magma_ieee_review_bundle.zip`

## PDF Requirements Checked Locally

- IEEE conference template source is used.
- All four named authors and their affiliation metadata are present in the TeX source.
- PDF is letter size.
- PDF page count remains within the target conference limit.
- PDF is not encrypted.
- PDF contains no forms or JavaScript.
- Fonts are embedded and subset.
- The rendered PDF pages have been inspected visually.
- The PDF includes searchable title/reference text.

## Source Archive Contents

The PDF eXpress source archive should contain only the files needed to rebuild the manuscript source:

- `magma_ieee.tex`
- External figure assets referenced by `\\includegraphics`

The source archive is for PDF eXpress conversion or validation. The review bundle is for internal handoff and includes reports and evidence artifacts; it should not be uploaded as the official paper unless a conference explicitly asks for supplementary files.

## Remaining Non-Compliance Risk

The package is still missing publication-ready physical fill-trial evidence. That is a scientific acceptance risk rather than a PDF-format risk.
