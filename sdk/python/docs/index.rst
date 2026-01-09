ErrorBrain Python SDK Documentation
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   modules

Introduction
------------

The ErrorBrain Python SDK provides a simple client for submitting errors
to the ErrorBrain API for AI analysis and storage in Obsidian vault.

Features
--------

* **Simple API**: Clean Pythonic interface
* **Type Safety**: Full Pydantic model validation
* **Exception Handling**: Automatic exception capture and formatting
* **Customizable**: Tags, metadata, and vault storage options

Installation
------------

Using uv::

    uv add errorbrain

Using pip::

    pip install errorbrain

Quick Start
-----------

Basic Usage::

    from errorbrain import ErrorBrainClient

    client = ErrorBrainClient("http://localhost:8000")

    # Manual error submission
    response = client.send_error(
        language="python",
        project="my-service",
        message="Database connection failed",
        traceback="...",
        tags=["prod", "database"]
    )

    print(f"Error ID: {response.id}")
    print(f"Explanation: {response.explanation}")

Exception Handling::

    try:
        # Your code
        result = risky_operation()
    except Exception as e:
        client.send_exception(
            exc=e,
            language="python",
            project="my-service",
            tags=["prod"]
        )
        raise

Health Check::

    if client.health_check():
        print("API is healthy")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
