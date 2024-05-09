## Needs editing

# Accept Python version during build
ARG PYTHON_VERSION="3.10.12"

FROM python:${PYTHON_VERSION}-slim

# Install OS dependencies
RUN apt-get update && apt-get -y upgrade \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl build-essential libsqlite3-dev

# Create a non-root user
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser/app

# Install Wave
ARG WAVE_VERSION="1.1.1"

ENV WAVE_HOME="/home/appuser/wave"
RUN \
    mkdir -p "${WAVE_HOME}" && \
    curl -fsSL https://github.com/h2oai/wave/releases/download/v${WAVE_VERSION}/wave-${WAVE_VERSION}-linux-amd64.tar.gz | tar -C ${WAVE_HOME} -xzv 2>&1
ENV WAVE_PATH="${WAVE_HOME}/wave-${WAVE_VERSION}-linux-amd64"

# Create a virtual environment
ENV VIRTUAL_ENV=/home/appuser/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY --chown=appuser:appuser  . .

# Set permissions for the Entrypoint script
RUN chmod +x docker-entrypoint.sh

ARG PYTHON_MODULE
ENV PYTHON_MODULE="${PYTHON_MODULE}"

ENTRYPOINT [ "./docker-entrypoint.sh" ]
