# pip-package-template-docker

[![Release Status](https://github.com/MichaelKim0407/pip-package-template-docker/actions/workflows/python-publish.yml/badge.svg)](https://github.com/MichaelKim0407/pip-package-template-docker/releases)
[![PyPI package](https://badge.fury.io/py/pip-package-template-docker.svg)](https://pypi.org/project/pip-package-template-docker)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pip-package-template-docker)](https://pypi.org/project/pip-package-template-docker)
[![Build Status](https://github.com/MichaelKim0407/pip-package-template-docker/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/MichaelKim0407/pip-package-template-docker/tree/main)
[![Coverage Status](https://coveralls.io/repos/github/MichaelKim0407/pip-package-template-docker/badge.svg?branch=main)](https://coveralls.io/github/MichaelKim0407/pip-package-template-docker?branch=main)

Project template for Dockerized pip package development.

## Overview

1. This project is fully Dockerized. For convenience, a [`Makefile`](Makefile) is provided to build/test during development.
2. Python 3.11 is the primary version for development, while 3.7 - 3.10 are included for compatibility. You may want to change them in the future.
   See [`docker-compose.yml`](docker-compose.yml) and [`Makefile`](Makefile).
   Refer to [this page](https://devguide.python.org/versions/) for Python versions you may want to support.
3. Linting is done using `flake8` and testing is done using `pytest`.
4. CI is designed for GitHub Actions. See [`.github`](.github). Coverage is reported to [Coveralls](https://coveralls.io/).
5. An automatic release to Pypi is made through GitHub Actions whenever you publish a new release on GitHub.
6. `LICENSE` in the template is MIT.

## How to use

1. Please familiarize yourself with all the concept involved. I am not responsible for things breaking if you use this template.
   * Python and different Python versions
   * Creating pip packages. I made a tutorial a few years ago, which you can see [here](https://github.com/MichaelKim0407/tutorial-pip-package).
   * Docker and docker-compose
   * Linting and flake8
   * Unit testing and pytest
   * CI and GitHub Actions
   * Code coverage
2. Find all instances of `pip-package-template-docker` and replace them with your desired package name.
   This is the **name** of your package known to Pypi and `pip install`.
3. Rename the [`src/pip_package_template_docker`](src/pip_package_template_docker) folder.
   Find all instances of `pip_package_template_docker` and replace them accordingly.
   This is what your `import` statement would use in Python code.
4. Go through [`src/setup.py`](src/setup.py) and make necessary changes. Please do not link your project to my name, email, or GitHub.
5. Replace [`README.md`](README.md) with your own. If you would like to use the badges, please change the links to point to your project.
6. Replace [`LICENSE`](LICENSE) with your own. Please do not license your project under my name.
7. Project version is found in the [`__init__.py`](src/pip_package_template_docker/__init__.py) file in your package.
   Update it accordingly as you develop your package.
8. Put unittests under [`src/tests`](src/tests).
9. Sign up for necessary accounts, such as [Pypi](https://pypi.org/) and [Coveralls](https://coveralls.io/).
10. Acquire a Pypi token and put it under your project as `PYPI_API_TOKEN`.
    On Pypi it is found under Account settings -> API tokens -> Add API token.
    On GitHub it is located in your project settings -> Security -> Secrets and variables -> Repository secrets.
    You may need to manually update once before a project-specific token can be acquired.
