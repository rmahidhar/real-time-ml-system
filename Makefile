run-service:
	export SSL_CERT_FILE=$(python -m certifi)
	uv run services/trades/src/trades/main.py

build-service-container:
	docker build -t trades:dev -f docker/trades.Dockerfile .

push-service-container:
	kind load docker-image trades:dev --name rwml-34fa

deploy-service-container: build-service-container push-service-container
	kubectl delete -f deployment/dev/trades/trades.yaml --ignore-not-found=true
	kubectl apply -f deployment/dev/trades/trades.yaml
 