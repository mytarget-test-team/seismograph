Simple usage
============

Any of runnable objects can to work with db client.
Extension do wraps *sqlalchemy* engine and utilizes some operations.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['db'])


    @suite.register
    def simple_test(case):
        db = case.ext('db')

        with db.read() as execute:
            result = execute('SELECT * FROM some_table').fetchall()

        case.assertion.greater(len(result), 0)

        with db.write() as execute:
            execute('DELETE from some_table')
