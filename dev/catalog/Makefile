default: start

activate:
	bash -c "source .venv/bin/activate"

run:
	.venv/bin/wave run app

server:
	cd .venv && ./waved

#wavedb: 
#	./bin/wavedb -access-key-id uzer -access-key-secret pa55word
#
#wavedb_test: 
#	./bin/wavedb

copy_venv:
	.venv/bin/pip freeze > requirements.txt

clone_venv:
	.venv/bin/pip install -r requirements.txt

docker:
	docker buildx build --platform linux/amd64 \
	-t umgc-catalog-wave:0.1.0 \
	--build-arg PYTHON_VERSION=3.10.12 \
	--build-arg WAVE_VERSION=1.1.1 \
	--build-arg PYTHON_MODULE="app.py" \
	-f Dockerfile .

run_docker:
	docker run --rm --name umgc_catalog \
	-p 10101:10101 \
	-e PORT=10101 \
	umgc-catalog-wave:0.1.0
