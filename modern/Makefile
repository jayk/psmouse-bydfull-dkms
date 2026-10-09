# SPDX-License-Identifier: GPL-2.0-only
PYTHON ?= python3
.PHONY: test
test:
	CC="$(CC)" $(PYTHON) tests/test_byd.py
	$(PYTHON) -m unittest discover -s tests -p 'test_build.py'
