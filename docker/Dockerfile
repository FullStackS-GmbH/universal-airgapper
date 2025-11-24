ARG BASE_IMAGE_REGISTRY="library"
ARG BASE_IMAGE_REPOSITORY="python"
ARG BASE_IMAGE_TAG="3.12-alpine3.22"
FROM ${BASE_IMAGE_REGISTRY}/${BASE_IMAGE_REPOSITORY}:${BASE_IMAGE_TAG}

ARG APP_COMMIT_SHA="changeme"
ARG APP_VERSION="v0.0.1"
ENV APP_COMMIT_SHA=$APP_COMMIT_SHA
ENV APP_VERSION=$APP_VERSION
ENV SETUPTOOLS_SCM_PRETEND_VERSION=$APP_VERSION

# install uv
COPY --from=docker.io/astral/uv@sha256:e4644cb5bd56fdc2c5ea3ee0525d9d21eed1603bccd6a21f887a938be7e85be1 /uv /uvx /bin/

# Install packages and CNSpec
RUN apk update && \
    apk add --no-cache \
    git

# Create a non-root user and group
RUN addgroup -S airgapper && adduser -S airgapper -G airgapper

USER airgapper

# Set working directory
WORKDIR /home/airgapper

# makes heavy use of .dockerignore
COPY --chown=airgapper:airgapper --chmod=744 . .

# Install dependencies
RUN uv sync --frozen

# Specify the command to run the app
ENTRYPOINT ["uv", "run", "cnairgapper"]
CMD ["--help"]
