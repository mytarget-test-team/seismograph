Config
======

Should to use **ALCHEMY_EX** option in config for configure extension.


Common settings
---------------

+-----------------+----------------------------------------------------+
| **PROTOCOL**    | This is protocol to dns URL.                       |
|                 | For example: "mysql+mysqlconnector"                |
+-----------------+----------------------------------------------------+
| **HOST**        | Database host                                      |
+-----------------+----------------------------------------------------+
| **PORT**        | Port which listen database                         |
+-----------------+----------------------------------------------------+
| **USER**        | Database user                                      |
+-----------------+----------------------------------------------------+
| **PASSWORD**    | Password access to database                        |
+-----------------+----------------------------------------------------+
| **DNS_PARAMS**  | Dict value. GET params to DNS URL.                 |
+-----------------+----------------------------------------------------+
| **DATABASES**   | Dict value where key is database name and          |
|                 | value is dict params for.                          |
|                 | `details <#database-settings>`_                    |
+-----------------+----------------------------------------------------+
| **SESSION**     | Settings for *sqlalchemy* session.                 |
|                 | `details <#session-settings>`_                     |
+-----------------+----------------------------------------------------+
| **POOL_CLASS**  | Connection pool class for db engine                |
+-----------------+----------------------------------------------------+


Database settings
-----------------

Any settings of common can to be changed through DATABASES key.

.. code-block:: python

    ALCHEMY_EX = {
        'HOST': '192.0.0.1',  # it's host by default
        'DATABASES': {
            'some_database': {
                'host': '127.0.0.1',  # here we can change him
            },
        },
    }


+-----------------+----------------------------------------------------+
| **protocol**    | Protocol for dns URL to database                   |
+-----------------+----------------------------------------------------+
| **host**        | Database host                                      |
+-----------------+----------------------------------------------------+
| **port**        | Port which listen database                         |
+-----------------+----------------------------------------------------+
| **user**        | Database user                                      |
+-----------------+----------------------------------------------------+
| **password**    | Password access to database                        |
+-----------------+----------------------------------------------------+
| **dns_params**  | Dict value. GET params to DNS URL.                 |
+-----------------+----------------------------------------------------+
| **pool_class**  | Connection pool class for db engine                |
+-----------------+----------------------------------------------------+
| **bind_key**    | Key for link database engine to..                  |
+-----------------+----------------------------------------------------+


Session settings
----------------

+------------------------+----------------------------------------------------+
| **autoflush**          | The autoflush setting to use with newly created    |
|                        | Session objects.                                   |
+------------------------+----------------------------------------------------+
| **autocommit**         | The autocommit setting to use with newly created   |
|                        | Session objects.                                   |
+------------------------+----------------------------------------------------+
| **info**               | Optional dictionary of information that            |
|                        | will be available                                  |
+------------------------+----------------------------------------------------+
| **expire_on_commit**   | The expire_on_commit setting to use with newly     |
|                        | created Session objects.                           |
+------------------------+----------------------------------------------------+
