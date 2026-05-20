[![JADExpert](JADExpert.png)](https://jadbio.com/) [![Funding](funding.png)](https://greece20.gov.gr/)

[Homepage](https://jadbio.com) | [JADExpert Docs](https://support.jadbio.com/pythonclient/latest) | [REST API Docs](https://support.jadbio.com/api/getting-started/general-approach)

---

> \[!WARNING\]  
> The API URL to JADBio has changed, and requests with client versions \<= 1.2.12 will fail.  
> We recommend updating the client to a newer version.  
> Alternatively, the URL can be set when creating a JADExpert client object: `JadbioClient(username, password, host='https://app.jadbio.com')`

JADBio's purpose-built AutoML platform provides leading-edge AI tools and automation capabilities enabling life-science  
professionals to build and deploy accurate and interpretable predictive models with speed and ease, even if they have no  
data science expertise.

This client (namely JADExpert) provides the major JADBio functionality to python users using API calls. Requests are HTTP GET and POST  
only. POST requests are used for any kind of resource creation, mutation, or deletion. GET requests are read-only and  
idempotent.

## Installation

### From source

Install the package locally from source:

```
pip install .
```

> **Note**: This repository contains possibly unreleased updates, which are subject to change. To install a released  
> version either install from a specific tag locally, or install it directly from PyPI (see below).

#### Documentation

Generate documentation using Sphinx:

```
# Install Sphinx if necessary
pip install -U Sphinx

# Generate documentation
sphinx-build -M html docs/src docs/build
```

To view the docs, open _docs/build/html/index.html_.

### From PyPI

Install the package from [PyPI](https://pypi.org/project/jadbio/):

```
pip install jadbio
```

### From Anaconda

Install the package from [Anaconda](https://anaconda.org/JADBio/jadbio):

```
conda install -c jadbio jadbio
```

#### Documentation

Documentation for all releases is available [here](https://support.jadbio.com/pythonclient/).

## Examples

You can experiment with the JADExpert, running the example python code in the _src/examples/_ folder and using the example  
datasets provided in the _src/examples/resources_ folder.

## Contact

Contact us at _support@jadbio.com_ for any questions or feedback.
