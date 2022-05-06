# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.134.1/containers/python-3/.devcontainer/base.Dockerfile
FROM python:3.8.13-buster

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3.8 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

COPY ./src /opt/dockmon/


# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update \
#     && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
