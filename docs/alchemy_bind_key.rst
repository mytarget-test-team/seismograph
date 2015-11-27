Bind key
========

You can to manage databases with help bind key. This is perhaps how from db client that from models.


Usage by db client
------------------

.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['db'])


    @suite.register
    def simple_test(case):
        db = case.ext('db')

        with db.read('some_bind_key') as execute:
            result = execute('SELECT * FROM some_table').fetchall()

        with db.write('some_bind_key') as execute:
            execute('DELETE from some_table')


Usage by models
---------------


.. code-block:: python

    import sqlalchemy
    from seismograph.ext.alchemy.orm import BaseModel


    class ExampleModel(BaseModel):

        __tablename__ = 'some_table'
        __bind_key__ = 'some_bind_key'

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


Yuo can change bind key on the fly


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['db'])


    @suite.register
    def simple_test(case):
        db = case.ext('db')

        with db('some_bind_key', ExampleModel):
            ExampleModel.create(name='some name')


or that...


.. code-block:: python

    @suite.register
    def simple_test(case):
        with ExampleModel.bind_key('some_bind_key'):
            ExampleModel.objects.get(1)
