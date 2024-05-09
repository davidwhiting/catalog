# Arguments for 

ARG WAVE_VERSION="1.1.1"
ARG PYTHON_VERSION="3.10.12"
ARG PYTHON_MODULE="app.py"

FROM python:${PYTHON_VERSION}-slim
ENV PYTHON_MODULE="app.py"
ENV USER="appuser"
ENV HOME="/home/$USER"

# Install OS dependencies
RUN apt-get update && apt-get -y upgrade \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl build-essential libsqlite3-dev

# Create a non-root user
RUN useradd --create-home $USER
USER $USER
WORKDIR $HOME

## Install Python dependencies

# Copy app code
COPY --chown=$USER:$USER  . .

# Note: requirements_docker.txt is a trimmed down version of 
# the development requirements.txt
RUN python3 -m venv venv && \
    venv/bin/pip install --upgrade pip && \
    venv/bin/pip install --no-cache-dir -r requirements_docker.txt

## Install Wave server
ENV WAVE_HOME="$HOME/wave"
#ARG WAVE_FILENAME="https://h2o-wave.s3.amazonaws.com/releases/wave-${WAVE_VERSION}-linux-amd64.tar.gz"
ARG WAVE_FILENAME="https://h2o-wave.s3.amazonaws.com/releases/wave-1.1.1-linux-amd64.tar.gz"
RUN \
    mkdir -p "${WAVE_HOME}" && \
    curl -fsSL ${WAVE_FILENAME} | tar -C ${WAVE_HOME} -xzv 2>&1

ENV WAVE_PATH="${WAVE_HOME}/wave-${WAVE_VERSION}-linux-amd64"
ENV PATH="$VIRTUAL_ENV/bin:$WAVE_PATH:$PATH"

# Set permissions for the Entrypoint script
RUN chmod +x docker-entrypoint.sh
#ENTRYPOINT [ "./docker-entrypoint.sh" ]
