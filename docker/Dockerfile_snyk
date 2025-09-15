# snyk/snyk:alpine as of 9/15/2025
ARG SNYK_VERSION="sha256:169b3545c8305d311d9756e3b60ce16de7ce35c92d90273def868c79f7a62fad"
ARG BASE_IMAGE_REGISTRY="ghcr.io"
ARG BASE_IMAGE_REPOSITORY="fullstacks-gmbh/universal-airgapper"
ARG BASE_IMAGE_TAG="latest"
FROM snyk/snyk@${SNYK_VERSION} AS snyk

FROM ${BASE_IMAGE_REGISTRY}/${BASE_IMAGE_REPOSITORY}:${BASE_IMAGE_TAG}

COPY --from=snyk /usr/local/bin/snyk /usr/local/bin/snyk
