Scope
=====

Yuo can tune global context, within a reasonable of course :)


Match suite to layer
--------------------

This is way to create relationship layer to class and him heirs.


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
