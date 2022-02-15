<p align="center">
    <a href="https://jadbio.com/">
        <img alt="JADBio" src="https://www.jadbio.com/jadbio/wp-content/uploads/github_logo/full_logo_rgb.svg" width="480">
    </a>
</p>

<p align="center">
    <a href="https://jadbio.com">Homepage</a> |
    <a href="https://support.jadbio.com/docs/pythonapi/latest">Python Client Docs</a> |
    <a href="https://support.jadbio.com/api/getting-started/general-approach">REST API Docs</a>
</p>

***

JADBio's purpose-built AutoML platform provides leading-edge AI tools and automation capabilities enabling life-science 
professionals to build and deploy accurate and interpretable predictive models with speed and ease, even if they have no
data science expertise.

This client provides the major JADBio functionality to python users using API calls. Requests are HTTP GET and POST
only. POST requests are used for any kind of resource creation, mutation, or deletion. GET requests are read-only and
idempotent.

## Installation

### From source

You can install the package locally from source as follows:

```bash
pip install .
```

> **Note**: This repository contains possibly unreleased updates, which are subject to change. To install a released
> version either install from a specific tag locally, or install it directly from PyPI (see below).

#### Documentation

You can generate documentation using Sphinx as follows:

```bash
# Install Sphinx if necessary
pip install -U Sphinx

# Generate documentation
sphinx-build -M html docs/src docs/build
```

To view the docs, open *docs/build/html/index.html*.

### From PyPI

The package is also available on [PyPI](https://pypi.org/project/jadbio/) and can be installed as follows:

```bash
pip install jadbio
```

#### Documentation
- latest release: https://support.jadbio.com/docs/pythonapi/latest
- version ``x.y.z``: https://support.jadbio.com/docs/pythonapi/x.y.z

## Examples

You can experiment with the client running the example python code in the *src/examples/* folder and using the example 
datasets provided in the *src/examples/resources* folder.

## Contact

Contact us at *support@jadbio.com* for any questions or feedback.
