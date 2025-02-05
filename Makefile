
install:
	poetry install

lint:
	poetry run black ./src;
	poetry run isort ./src;

run:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py runserver

migrations:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py makemigrations

migrate:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py migrate

collectstatic:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py collectstatic -c --noinput

docker-build:
	docker build -f ./docker/Dockerfile . -t visible-ideas-homework

docker-up: docker-build
	docker run --name visible-ideas-homework -p 8000:8000 -it visible-ideas-homework

docker-down:
	docker container rm visible-ideas-homework
