.PHONY: all paper verify fill-plan fill-summary physical-readiness fill-photo-panel fill-molds planned-gcode fill-packet trial-readiness transcript-evidence claim-scope claim-evidence ieee-readiness submission-package audit manifest render outputs clean

PAPER_DIR := paper
PDF := $(PAPER_DIR)/magma_ieee.pdf
TEX := $(PAPER_DIR)/magma_ieee.tex
VERIFY_DIR := output/verification
RENDER_DIR := tmp/pdfs

all: manifest

verify:
	python3 tools/summarize_injection_gcode.py

fill-summary:
	python3 tools/summarize_fill_trials.py

physical-readiness: fill-summary
	python3 tools/check_physical_data_readiness.py

fill-photo-panel: fill-summary
	python3 tools/build_fill_photo_panel.py

fill-plan:
	python3 tools/summarize_fill_trial_plan.py

fill-molds:
	python3 tools/generate_standard_molds.py

planned-gcode:
	python3 tools/generate_planned_injection_gcode.py

fill-packet: fill-molds planned-gcode
	python3 tools/generate_fill_trial_packet.py

trial-readiness: fill-packet
	python3 tools/check_trial_execution_readiness.py

transcript-evidence:
	python3 tools/check_transcript_evidence.py

claim-scope:
	python3 tools/check_claim_scope.py

claim-evidence:
	python3 tools/check_claim_evidence_map.py

ieee-readiness: render
	python3 tools/check_ieee_submission_readiness.py

submission-package: audit
	python3 tools/build_submission_package.py

audit: verify fill-plan fill-summary physical-readiness fill-photo-panel fill-packet trial-readiness transcript-evidence claim-scope claim-evidence ieee-readiness
	python3 tools/audit_magma_paper.py

manifest: audit submission-package
	python3 tools/write_submission_manifest.py

paper:
	cd $(PAPER_DIR) && tectonic --keep-logs --keep-intermediates magma_ieee.tex

outputs: paper
	mkdir -p output/pdf output/tex
	cp $(PDF) output/pdf/magma_ieee_paper.pdf
	cp $(PDF) output/tex/magma_ieee.pdf

render: outputs
	mkdir -p $(RENDER_DIR)
	rm -f $(RENDER_DIR)/magma_ieee_page-*.png
	pdftoppm -png -r 180 $(PDF) $(RENDER_DIR)/magma_ieee_page
	pdfinfo $(PDF) | sed -n '1,12p'

clean:
	rm -f $(PAPER_DIR)/magma_ieee.aux $(PAPER_DIR)/magma_ieee.log
	rm -f $(RENDER_DIR)/magma_ieee_page-*.png
