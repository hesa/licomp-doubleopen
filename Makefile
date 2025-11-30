# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

MATRIX_FILE = licomp_doubleopen/data/doubleopen-bindist.json

.PHONY: build

all: $(MATRIX_FILE)

$(MATRIX_FILE):
	PYTHONPATH=. matrix/create_matrix.py | jq . > $@

matrix: $(MATRIX_FILE)

clean:
	rm -f $(MATRIX_FILE)
	find . -name "*~" | xargs rm -fr
	rm -fr licomp_doubleopen.egg-info
	rm -fr build
	rm -fr dist sdist
	rm -fr licomp_doubleopen/__pycache__
	rm -fr tests/python/__pycache__
	rm -fr matrix/__pycache__
	rm -fr .pytest_cache

build: $(MATRIX_FILE) 
	rm -fr build && python3 setup.py sdist

lint:
	PYTHONPATH=. flake8 licomp_doubleopen

check_version:
	@echo -n "Checking api versions: "
	@MY_VERSION=`grep api_version licomp_doubleopen/config.py | cut -d = -f 2 | sed -e "s,[ ']*,,g"` ; LICOMP_VERSION=`grep licomp requirements.txt | cut -d = -f 3 | sed -e "s,[ ']*,,g" -e "s,[ ']*,,g" -e "s,\(^[0-9].[0-9]\)[\.0-9\*]*,\1,g"` ; if [ "$$MY_VERSION" != "$$LICOMP_VERSION" ] ; then echo "FAIL" ; echo "API versions differ \"$$MY_VERSION\" \"$$LICOMP_VERSION\"" ; exit 1 ; else echo OK ; fi

test:
	PYTHONPATH=. python3 -m pytest --log-cli-level=10 tests/

test-local:
	PYTHONPATH=.:../licomp python3 -m pytest --log-cli-level=10 tests/

install:
	pip install .

reuse:
	reuse --suppress-deprecation lint

check: clean $(MATRIX_FILE) reuse lint test check_version build
	@echo 
	@echo 
	@echo "All tests passed :)"
	@echo 
	@echo 

compare: $(MATRIX_FILE)
	PYTHONPATH=. devel/compare-relicense.py
