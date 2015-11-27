Layers
======

Any of runnable objects can get layers for expanded logic on different levels.
Layers is chain of callbacks. Context object call to chain of layers, he is responsible for that.


Program layer
-------------

.. autoclass:: seismograph.program.ProgramLayer
    :members:
    :exclude-members: __dict__, __weakref__
    :private-members:
    :special-members:


.. code-block:: python

    import seismograph


    class ExampleProgramLayer(seismograph.ProgramLayer):
        pass


    class ExampleProgram(seismograph.Program):

        __layers__ = (
            ExampleProgramLayer(),
        )


    # or


    program = seismograph.Program(layers=[ExampleProgramLayer()])


Suite layer
-----------

.. autoclass:: seismograph.suite.SuiteLayer
    :members:
    :exclude-members: __dict__, __weakref__
    :private-members:
    :special-members:


.. code-block:: python

    import seismograph


    class ExampleSuiteLayer(seismograph.SuiteLayer):
        pass


    class ExampleSuite(seismograph.Suite):

        __layers__ = (
            ExampleSuiteLayer(),
        )


    # or


    suite = seismograph.Suite(__name__, layers=[ExampleSuiteLayer()])


Case layer
----------


.. autoclass:: seismograph.case.CaseLayer
    :members:
    :exclude-members: __dict__, __weakref__
    :private-members:
    :special-members:


.. code-block:: python

    import seismograph


    class ExampleCaseLayer(seismograph.CaseLayer):
        pass


    class ExampleCase(seismograph.Case):

        __layers__ = (
            ExampleCaseLayer(),
        )


    # or


    suite = seismograph.Suite(__name__)


    @suite.register(layers=[ExampleCaseLayer()])
    class ExampleCase2(seismograph.Case):
        pass
