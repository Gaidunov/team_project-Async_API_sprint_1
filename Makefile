

go: collect-static docker-up-dev create-db populate-db django-setup

collect-static:
	cd app && python3 manage.py collectstatic && cd ..


docker-up-dev:collect-static
	docker compose -f docker-compose-dev.yml up -d

docker-up-prod:
	docker compose -f docker-compose-prod.yml up -d

populate-db:create-db	
	python3 -m utils.data_transfer.load

create-db:docker-up
	docker exec admin_panel-postgres-1 bash /docker-entrypoint-initdb.d/moi_sql.sh  || true
	
django-setup:docker-up
	docker exec admin_panel-service-1 python3 manage.py migrate --fake-initial
	docker exec admin_panel-service-1 python3 manage.py createsuperuser --noinput || true
 

restart:
	docker rm -f admin_panel-service-1 admin_panel-postgres-1 admin_panel-etl-1 admin_panel-nginx-1 admin_panel-elastic-1
	docker image rm -f admin_panel_service admin_panel_etl docker.elastic.co/elasticsearch/elasticsearch postgres
	docker volume prune
	docker system prune
	make setup
