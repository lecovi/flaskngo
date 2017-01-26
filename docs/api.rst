.. _api:

API
===

.. automodule:: app.auth

This part of the documentation covers all the interfaces of Flask.  For
parts where Flask depends on external libraries, we document the most
important right here and provide links to the canonical documentation.

User Models
-----------

.. automodule:: app.auth.models

.. autoclass:: Permission
    :members:

.. autoclass:: RoleGroup
    :members:

.. autoclass:: Role
    :members:

.. autoclass:: User
    :members:

.. autoclass:: UserRole
    :members:

Decorators
----------

.. automodule:: app.auth.decorators
    :members:

Routes
------

.. automodule:: app.auth.routes
    :members:
