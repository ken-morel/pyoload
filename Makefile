build:
	docker-compose build --pull

lint:
	docker-compose run --rm dev flake8

test:
	docker-compose run --rm dev pytest --cov --cov-report term-missing:skip-covered

test37:
	docker-compose run --rm test37

test38:
	docker-compose run --rm test38

test39:
	docker-compose run --rm test39

test310:
	docker-compose run --rm test310

ci: build lint test test37 test38 test38 test39 test310

sdist:
	docker-compose run --rm dev python setup.py sdist
