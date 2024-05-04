from pathlib import Path

from setuptools import setup, find_packages

from pyoload import __version__

project_dir = Path(__file__).parent
try:
    long_description = (project_dir / 'README.md').read_text()
except FileNotFoundError:
    long_description = ''

deps = ()

extra_flake8 = (
    'flake8',
    'flake8-commas',
    'flake8-quotes',
    'flake8-multiline-containers',
)

extra_test = (
    'pytest',
    'pytest-cov',
)

extra_dev = (
    *extra_flake8,
    *extra_test,
)

extra_ci = (
    *extra_flake8,
    *extra_test,
    'coveralls',
)

setup(
    name='pyoload',
    version=__version__,
    packages=find_packages(exclude=['tests', 'tests.*']),
    url='https://github.com/ken-morel/pyoload',
    license='MIT',
    author='ken-morel',
    author_email='engonken8@gmail.com',
    description='Python package for function argument overload, typechecking and casting',
    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=deps,
    extras_require={
        'dev': extra_dev,
        'ci': extra_ci,
    },

    classifiers=[
        # See https://pypi.org/classifiers/

        'Intended Audience :: Developers',

        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',

        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
