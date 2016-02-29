Scope
=====

Yuo can tune global context, within a reasonable of course :)


Layers matching
---------------

This is way to creating relationships of layer to class and it heirs.


.. code-block:: python

    import seismograph
    from seismograph import scope


    class ExampleCaseLayer(seismograph.CaseLayer):
        pass


    class ExampleCase(seismograph.Case):
        pass


    scope.match_case_to_layer(ExampleCase, ExampleCaseLayer())


You can do that for suite also.


Configure
---------

.. autofunction:: seismograph.scope.configure
