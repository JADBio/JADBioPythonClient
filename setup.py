# Minimal setup.py for backwards compatibility.
# See: https://setuptools.pypa.io/en/latest/setuptools.html#setup-cfg-only-projects

from setuptools import setup

# Read the version number
jadbio_globals = {}
with open('jadbio/__init__.py') as f:
    exec(f.read(), jadbio_globals)

setup(
    project_urls={
        "Homepage": "https://jadbio.com",
        "Documentation": "https://support.jadbio.com/pythonclient/" + jadbio_globals['__version__'],
        "Source code": "https://github.com/JADBio/JADBioPythonClient",
    },
    # Description for pypi
    long_description="""
    JADBio's purpose-built AutoML platform provides leading-edge AI tools and automation capabilities enabling life-science professionals to build and deploy accurate and interpretable predictive models with speed and ease, even if they have no data science expertise.

    This client provides the major JADBio functionality to python users using API calls. Requests are HTTP GET and POST only. POST requests are used for any kind of resource creation, mutation, or deletion. GET requests are read-only and idempotent.
    """,
    long_description_content_type='text/plain')
