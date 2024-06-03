#!/bin/bash
cd venv && ./waved \
    -oidc-client-id wave \
    -oidc-client-secret aJ0wyZbXiBdGxXbKxAZu73Dm3Wu2wMb2 \
    -oidc-redirect-url http://localhost:10101/_auth/callback \
    -oidc-provider-url http://localhost:8080/realms/master \
    -oidc-end-session-url http://localhost:8080/realms/master/protocol/openid-connect/logout
