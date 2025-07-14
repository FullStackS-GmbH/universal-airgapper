FROM snyk/snyk:python-alpine AS snyk

# Use official Python image as base
ARG BASE_IMAGE_REGISTRY=""
FROM ${BASE_IMAGE_REGISTRY}python:3.12-alpine as image

ARG APP_COMMIT_SHA=""
ARG APP_VERSION=""
ENV APP_COMMIT_SHA=$APP_COMMIT_SHA
ENV APP_VERSION=$APP_VERSION

# Set CNSpec version
ARG CNSPEC_VERSION="11.49.0"

# Install packages and CNSpec
RUN apk update && \
    apk add --no-cache \
    git \
    bash \
    curl \
    tar \
    openssh-client

# copy snyk CLI from snyk image
COPY --from=snyk /usr/local/bin/snyk /usr/local/bin/snyk

RUN curl -L "https://github.com/mondoohq/cnspec/releases/download/v${CNSPEC_VERSION}/cnspec_${CNSPEC_VERSION}_linux_amd64.tar.gz" \
        -o cnspec.tar.gz && \
    tar -xzf cnspec.tar.gz cnspec && \
    chmod +x cnspec && \
    mv cnspec /usr/local/bin/cnspec && \
    rm cnspec.tar.gz

# Create a non-root user and group
RUN addgroup -S airgapper && adduser -S airgapper -G airgapper

USER airgapper

# Set working directory
WORKDIR /home/airgapper

# Copy requirements first to leverage Docker cache
COPY pyproject.toml requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all local packages and files
COPY src/ .

# Specify the command to run the app
ENTRYPOINT ["python", "main.py"]
