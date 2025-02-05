
install:
	poetry install

run:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py runserver

migrations:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py makemigrations

migrate:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py migrate

collectstatic:
	PYTHONPATH=./src/:${PYTHONPATH} poetry run python ./src/manage.py collectstatic -c --noinput