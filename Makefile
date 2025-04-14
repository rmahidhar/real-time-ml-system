dev:
	export SSL_CERT_FILE=$(python -m certifi)
	uv run services/${service}/src/${service}trades/main.py

build:
	docker build -t ${service}:dev -f docker/${service}.Dockerfile .

push:
	kind load docker-image ${service}:dev --name rwml-34fa

deploy: build push
	kubectl delete -f deployment/dev/${service}/${service}.yaml --ignore-not-found=true
	kubectl apply -f deployment/dev/${service}/${service}.yaml
 
 lint:
	ruff check . --fix