default: start

copy_venv:
	venv/bin/pip freeze > requirements.txt

clone_venv:
	venv/bin/pip install -r requirements.txt

build_amd:
	docker build --platform linux/amd64 \
	-t umgc-catalog-wave:latest \
	-f Dockerfile .

build_arm:
	docker build --platform linux/arm64 \
	-t umgc-catalog-wave_arm:latest \
	-f Dockerfile_arm .

build_all:
	build_amd
	build_arm

build: 
	build_amd

run_amd:
	docker run --rm --name umgc_catalog \
	-p 10101:10101 \
	-p 8000:8000 \
	-e PORT=10101 \
	umgc-catalog-wave:latest

run_arm:
	docker run --rm --name umgc_catalog_arm \
	-p 10101:10101 \
	-p 8000:8000 \
	-e PORT=10101 \
	umgc-catalog-wave_arm:latest

