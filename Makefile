run-trades-service:
	export SSL_CERT_FILE=$(python -m certifi)
	uv run services/trades/src/trades/main.py

trades-container:
	docker build -t trades:dev -f docker/trades.Dockerfile .