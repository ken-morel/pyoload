ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}

WORKDIR /src
COPY src/setup.py README.md LICENSE ./
COPY src/py_overload/__init__.py ./py_overload/__init__.py
RUN pip install -e .[dev]

COPY src .
