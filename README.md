<p align="center">
    <a href="https://jadbio.com/">
        <img alt="JADBio" src="https://www.jadbio.com/jadbio/wp-content/uploads/github_logo/full_logo_rgb.svg" width="480">
    </a>
</p>

<p align="center">
    <a href="https://jadbio.com">Homepage</a> |
    <a href="https://support.jadbio.com/api/getting-started/general-approach/">REST API Docs</a>
</p>

***

JADBio's purpose-built AutoML platform provides leading-edge AI tools and automation capabilities enabling life-science 
professionals to build and deploy accurate and interpretable predictive models with speed and ease, even if they have no
data science expertise.

This client provides the major JADBio functionality to python users using API calls. Requests are HTTP GET and POST
only. POST requests are used for any kind of resource creation, mutation, or deletion. GET requests are read-only and
idempotent.

## Installation

Install the package locally from source:

```bash
pip install .
```

Generate documentation using Sphinx:

```bash
sphinx-build -M html docs/src docs/build
```

To view the docs, open *docs/build/html/index.html*.

## Examples

You can experiment with the client running the example python code in the *src/examples/* folder and using the example 
datasets provided in the *src/examples/resources/* folder.

## Contact

Contact us at *support@jadbio.com* for any questions or feedback.

## Test for pull request

