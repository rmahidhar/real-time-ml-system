kindcluster:
	cd deployment/dev/kind; chmod +x create_cluster.sh; ./create_cluster.sh

kafka-ui-access:
	kubectl -n kafka port-forward svc/kafka-ui 8182:8080

send-test-topic:
	echo "{'key': 'value'}" | kcat -b 127.0.0.1:9092 -P -t first_topic

consume-test-topic:
	kcat -b 127.0.0.1:9092 -C -t test_topic

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