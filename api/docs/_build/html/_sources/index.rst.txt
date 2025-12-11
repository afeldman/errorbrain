ErrorBrain Server Documentation
================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   modules

Introduction
------------

ErrorBrain Server is a FastAPI application for error tracking and AI analysis.
It captures errors from applications, analyzes them with LLM (Local or Cloud),
and stores them in an Obsidian vault for searchable engineering knowledge.

Features
--------

* **REST API**: FastAPI-based error submission endpoint
* **LLM Analysis**: AI-powered error explanation using any LLM provider
* **Obsidian Integration**: Store errors as markdown in your vault
* **Multi-language**: Support for Python, Go, Terraform, and more
* **Tagging & Metadata**: Organize errors with tags and custom metadata

Quick Start
-----------

Installation::

    cd api
    uv sync --all-extras

Configuration::

    export ERRORBRAIN_LLM_PROVIDER=openai
    export ERRORBRAIN_LLM_MODEL=gpt-4
    export ERRORBRAIN_LLM_BASE_URL=http://localhost:1234/v1
    export ERRORBRAIN_OBSIDIAN_PATH=~/vault/errors

Run Development Server::

    make dev-api
    # or
    uv run errorbrain-server-dev

Run Production Server::

    uv run errorbrain-server

API Endpoints
-------------

Health Check
~~~~~~~~~~~~

``GET /healthz``

Returns API health status.

Submit Error
~~~~~~~~~~~~

``POST /v1/errors``

Submit an error for analysis and storage.

Request body::

    {
        "language": "python",
        "project": "my-service",
        "message": "Connection timeout",
        "traceback": "Traceback (most recent call last)...",
        "tags": ["prod", "database"],
        "metadata": {"host": "server-01"},
        "store_in_vault": true
    }

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
