Scripts
=======

Scripts is independent essences unlike suite and case.
Script can to run separately of suites by **run_scripts** method. Let look example...


.. code-block:: python

    import seismograph

    class ExampleAfterScript(seismograph.AfterScript):

        def task_one(self):
            pass

        def task_two(self):
            pass


    class ExampleBeforeScript(seismograph.BeforeScript):

        def task_one(self):
            pass

        def task_two(self):
            pass


    if __name__ == '__main__':
        program = seismograph.Program(scripts=(ExampleBeforeScript, ExampleAfterScript))
        program()
