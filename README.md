# JADBioPythonClient

JADBio’s purpose-built AutoML platform (www.jadbio.com) provides leading-edge AI tools and automation capabilities enabling life-science professionals
to build and deploy accurate and interpretable predictive models with speed and ease, even if they have no data science expertise.

This client provides the major JADBio functionality to python users using API calls. Requests are HTTP GET and POST only.
POST requests are used for any kind of resource creation, mutation, or deletion. GET requests are read-only and idempotent.

**Note that this client uses internally the REST API client available in *www.jadbio.com/jadbio-automl-rest-api*.**

## Installing the Python package

Install the JADBioPythonClient and the requirements.

```bash
$ pip install .
$ pip install -r requirements.txt
```

## Generating docs using Sphinx (www.sphinx-doc.org)

1. Go to the *docs* folder.

2. Execute the following commands:

```bash
$ pip install sphinx
$ mkdir build
$ sphinx-apidoc -f -o source/ build
$ make html
```
3. Run *docs/build/html/index.html*

## Experimenting with examples

You can experiment with the client running the example python code in the *src/examples/* folder and using the example datasets provided in the 
*src/examples/resources/* folder.

**Questions or feedback can also be sent via e-mail at support@jadbio.com**
