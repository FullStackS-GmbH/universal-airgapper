ARG CNSPEC_VERSION="12.0.0"
ARG BASE_IMAGE_REGISTRY="ghcr.io"
ARG BASE_IMAGE_REPOSITORY="fullstacks-gmbh/universal-airgapper"
ARG BASE_IMAGE_TAG="latest"
FROM mondoo/cnspec:${CNSPEC_VERSION}-rootless AS cnspec

FROM ${BASE_IMAGE_REGISTRY}/${BASE_IMAGE_REPOSITORY}:${BASE_IMAGE_TAG}

COPY --from=cnspec /usr/local/bin/cnspec /usr/local/bin/cnspec
