# GARP skeleton entrypoints (stdlib only; no network)
.PHONY: test selfcheck

test:
	python3 -m unittest discover -s tests/unit -v

selfcheck:
	python3 apps/cli/selfcheck.py
