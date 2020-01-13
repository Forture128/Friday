clean-pyc:
	find . -name '*.pyc' -exec rm --force {} \;
	find . -name '*.pyo' -exec rm --force {} \;

clean-cov:
	rm --force --recursive htmlcov/

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

lint:
	flake8 src

test: clean-pyc clean-cov
	python -m pytest --cov=src --cov-branch --cov-fail-under=100 --cov-report=html --verbose --color=yes

run:
	echo "No run file"
