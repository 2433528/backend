-include .env
up:
	docker compose up -d
	
down:
	docker compose down
	
rebuild-server:
	docker compose build django-webserver

migrate-db:
	docker exec -it ${APP_NAME}-django-webserver python3 manage.py makemigrations 								
	docker exec -it ${APP_NAME}-django-webserver python3 manage.py migrate

createsuperuser:
	docker exec -it ${APP_NAME}-django-webserver python3 manage.py createsuperuser

collectstatic:
	docker exec -it ${APP_NAME}-django-webserver python3 manage.py collectstatic --no-input
