#!/bin/bash
## See https://wave.h2o.ai/docs/development
docker run \
  -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  --volume ~/.keycloak:/opt/jboss/keycloak/standalone/data \
  quay.io/keycloak/keycloak:21.0.1 \
  start-dev
