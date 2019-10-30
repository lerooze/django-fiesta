# These targets are not files
.PHONY: docs sandbox

help: ## Display this help message
	@echo "Please use \`make <target>\` where <target> is one of"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

##################
# Install commands
##################
init:
	pip install pipenv --upgrade
	pipenv install --dev
	
# install-migrations-testing-requirements: ## Install migrations testing requirements
# 	pipenv install -r requirements_migrations.txt

#############################
# Migrations commands
#############################
build_migrations: migrations_reset migrations_make

migrations_reset:
	find . -path "./src/fiesta/apps/*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "./src/fiesta/apps/*/migrations/*.pyc"  -delete

migrations_make:
	sandbox/manage.py makemigrations

#############################
# Sandbox management commands
#############################
sandbox: init build_sandbox

build_sandbox: sandbox_clean

sandbox_clean: ## Clean sandbox images,cache,static and database
	# Remove media
	-rm -f sandbox/db.sqlite3
	# Create database
	sandbox/manage.py migrate

sandbox_image: ## Build latest docker image of django-oscar-sandbox
	docker build -t django-oscar-sandbox:latest .

##################
# Tests and checks
##################
test_migrations: 
	# install-migrations-testing-requirements
	cd sandbox && ./test_migrations.sh

test:
	# This runs all of the tests
	tox

######################
# Project Management
######################
clean: ## Remove files not in source control
	find . -type f -name "*.pyc" -delete
	rm -rf nosetests.xml coverage.xml htmlcov *.egg-info *.pdf dist violations.txt

docs: ## Compile docs
	cd docs && make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"

todo: ## Look for areas of the code that need updating when some event has taken place (like Oscar dropping support for a Django version)
	-grep -rnH TODO *.txt
	-grep -rnH TODO src/oscar/apps/
	-grep -rnH "django.VERSION" src/oscar/apps

release: clean ## Creates release
	pip install twine wheel
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload -s dist/*

flake8:
	pipenv run flake8 --ignore=E501,F401,E128,E402,E731,F821 requests

coverage:
	pipenv run py.test --cov-config .coveragerc --verbose --cov-report term --cov-report xml --cov=requests tests

ci:
	pipenv run py.test -n 8 --boxed --junitxml=report.xml

#######################
# Translations Handling
#######################
extract_translations: ## Extract strings and create source .po files
	cd src/oscar; django-admin.py makemessages -a

compile_translations: ## Compile translation files and create .mo files
	cd src/oscar; django-admin.py compilemessages


