Alchemy
=======

.. toctree::
    :maxdepth: 2

   alchemy_simple
   alchemy_config
   alchemy_orm
   alchemy_bind_key


Alchemy extension is wrapper over *sqlalchemy* lib.
This make for work with database and not think about session, engine and etc...
All what you need is configure extension and work with it.
See `config documentation <alchemy_config.html>`_ for that.

You can to use db connection from *sqlalchemy* engine.
We implemented db client for that.
It's available as extension for runnable objects.
Should to use **seismograph.ext.alchemy.orm.BaseModel** class for usage ORM.


Features
--------

* Bind key

Engines can be related to database by bind key.

* Easy CRUD operations with help base model.

You aren't needing to work with session. Model will do it for you.