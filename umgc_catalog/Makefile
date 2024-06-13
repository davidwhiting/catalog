default: run

## Docker build commands

build_amd:
	docker build --platform linux/amd64 \
	--build-arg PLATFORM=amd64 \
	--build-arg PYTHON_VERSION=3.10.12 \
	-t umgc-wave-app:latest \
	-f dockerfile .

build_arm:
	docker build --platform linux/arm64 \
	--build-arg PLATFORM=arm64 \
	--build-arg PYTHON_VERSION=3.10.12 \
	-t umgc-wave-app_arm:latest \
	-f dockerfile .

build: build_amd

build_all: build_amd build_arm

# Docker run commands

run_amd:
	docker run --rm --name umgc_catalog \
	-p 10101:10101 \
	-p 8000:8000 \
	-e PORT=10101 \
	umgc-wave-app:latest

run_arm:
	docker run --rm --name umgc_catalog_arm \
	-p 10101:10101 \
	-p 8000:8000 \
	-e PORT=10101 \
	umgc-wave-app_arm:latest

run: run_amd


copy_venv:
	.venv/bin/pip freeze > requirements.txt

clone_venv:
	.venv/bin/pip install -r requirements.txt
