API Reference
=============

Main Module
-----------

.. automodule:: errorbrain_server.main
   :members:
   :undoc-members:
   :show-inheritance:

Models
------

ErrorReport
~~~~~~~~~~~

.. autoclass:: errorbrain_server.main.ErrorReport
   :members:
   :undoc-members:
   :show-inheritance:

ErrorResponse
~~~~~~~~~~~~~

.. autoclass:: errorbrain_server.main.ErrorResponse
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

build_error_prompt
~~~~~~~~~~~~~~~~~~

.. autofunction:: errorbrain_server.main.build_error_prompt

explain_error_with_llm
~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: errorbrain_server.main.explain_error_with_llm

save_markdown_to_obsidian
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: errorbrain_server.main.save_markdown_to_obsidian

Endpoints
---------

healthz
~~~~~~~

.. autofunction:: errorbrain_server.main.healthz

create_error
~~~~~~~~~~~~

.. autofunction:: errorbrain_server.main.create_error

Entry Points
------------

run_dev
~~~~~~~

.. autofunction:: errorbrain_server.main.run_dev

run
~~~

.. autofunction:: errorbrain_server.main.run
