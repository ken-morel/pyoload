build:
	docker-compose build --pull

lint:
	docker-compose run --rm dev flake8

test:
	docker-compose run --rm dev pytest --cov --cov-report term-missing:skip-covered

test38:
	docker-compose run --rm test38
test39:
	docker-compose run --rm test39
test310:
	docker-compose run --rm test310
test311:
	docker-compose run --rm test311
test312:
	docker-compose run --rm test312

ci: build lint test test38 test39 test310 test311 test312

sdist:
	docker-compose run --rm dev python setup.py sdist
