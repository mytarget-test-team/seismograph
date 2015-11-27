ORM
===

You can use column and types from *sqlalchemy* lib, but should to use BaseModel class from extension.
Sqlalchemy session query is available as query property on BaseModel class.


Model example
-------------


.. code-block:: python

    import sqlalchemy
    from seismograph.ext.alchemy.orm import BaseModel


    class ExampleModel(BaseModel):

        __tablename__ = 'some_table'

        id = sqlalchemy.Column(
            sqlalchemy.Integer,
            nullable=False,
            primary_key=True,
            autoincrement=True,
        )
        name = sqlalchemy.Column(
            sqlalchemy.String(255),
            nullable=False,
        )


Select operations
-----------------

Select query is doing so


.. code-block:: python

    # get by primary key
    ExampleModel.objects.get(1)

    # get list
    ExampleModel.objects.getlist()
    # Also, you can set limit and offset to query
    # limit is 100 by default
    ExampleModel.objects.getlist(limit=50, offset=10)

    # get by
    ExampleModel.objects.get_by(name='some name')


Create, update, delete operations
---------------------------------


.. code-block:: python

    new_record = ExampleModel.create(name='some name')
    new_record.update(name='new name')
    new_record.remove()



Multiple updates and deletes
----------------------------

You can to update many records by one operation


.. code-block:: python

    where = {'name': 'some name'}

    ExampleModel.objects.update_by(where, name='new_name')


Also, deletes


.. code-block:: python

    ExampleModel.objects.remove_by(name='some name')
