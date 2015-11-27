Alchemy
=======

.. toctree::
    :maxdepth: 2

   alchemy_simple
   alchemy_config
   alchemy_orm
   alchemy_bind_key


Alchemy extension is wrapper for *sqlalchemy* lib.
This make for work with database and not think about session, engine and etc...
All what you needed is configure extension and working with him.
See `config documentation <alchemy_config.html>`_ for that.

You can use ORM and db connection from *sqlalchemy* engine.
We implemented db client for that.
He is available as extension for runnable objects.
Should to use **seismograph.ext.alchemy.orm.BaseModel** class for usage ORM.


Features
--------

* Bind key

Engines can be related to database by bind key.

* Easy CRUD operations from base model.

You not need to work with session. Model will do it for you.