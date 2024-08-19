# Makefile for UMGC Wave App

# Variables
DOCKER_IMAGE_NAME := umgc-wave-app
DOCKER_IMAGE_NAME_ARM := $(DOCKER_IMAGE_NAME)_arm
PYTHON_VERSION := 3.10.12
PORT := 10101
HOST_PORT := 8000
VENV_PATH := .venv  # Default virtual environment path

# Phony targets
.PHONY: default build build_amd build_arm build_all run run_amd run_arm copy_venv clone_venv

# Default target
default: run

# Docker build commands
build_amd:
	docker build --platform linux/amd64 \
		--build-arg PLATFORM=amd64 \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		-t $(DOCKER_IMAGE_NAME):latest \
		-f dockerfile .

build_arm:
	docker build --platform linux/arm64 \
		--build-arg PLATFORM=arm64 \
		--build-arg PYTHON_VERSION=$(PYTHON_VERSION) \
		-t $(DOCKER_IMAGE_NAME_ARM):latest \
		-f dockerfile .

build: build_amd

build_all: build_amd build_arm

# Docker run commands
run_amd:
	docker run --rm --name umgc_catalog \
		-p $(PORT):$(PORT) \
		-p $(HOST_PORT):$(HOST_PORT) \
		-e PORT=$(PORT) \
		$(DOCKER_IMAGE_NAME):latest

run_arm:
	docker run --rm --name umgc_catalog_arm \
		-p $(PORT):$(PORT) \
		-p $(HOST_PORT):$(HOST_PORT) \
		-e PORT=$(PORT) \
		$(DOCKER_IMAGE_NAME_ARM):latest

run: run_amd

# Virtual environment management
copy_venv:
	$(VENV_PATH)/bin/pip freeze > requirements.txt

clone_venv:
	$(VENV_PATH)/bin/pip install -r requirements.txt

