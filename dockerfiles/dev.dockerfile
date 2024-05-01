ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}

WORKDIR /src
COPY src/setup.py README.md LICENSE ./
COPY src/pip_package_template_docker/__init__.py ./pip_package_template_docker/__init__.py
RUN pip install -e .[dev]

COPY src .
