build:
	docker image build -t auth:${cat version.txt} .
