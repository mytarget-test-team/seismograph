Scripts
=======

Scripts is independent essences unlike suite and case.
You can write your script and implement run logic for him.
Script can run separately of suites. Let look example...


.. code-block:: python

    import traceback
    import seismograph
    from seismograph.utils.common import measure_time


    class ExampleBeforeScript(seismograph.BeforeScript):

        is_run = False

        def check_something(self):
            seismograph.assertion.equal(1, 1)

        def main(self):
            # program config available as self.config for usage
            self.check_something()

        def __is_run__(self):
            return self.is_run

        def __run__(self, result):
            self.is_run = True
            timer = measure_time()

            try:
                self.main()
                result.add_success(
                    self, timer(),
                )
            except AssertionError as fail:
                result.add_fail(
                    self, traceback.format_exc(), timer(), fail,
                )
            except BaseException as error:
                result.add_error(
                    self, traceback.format_exc(), timer(), error,
                )


    if __name__ == '__main__':
        program = seismograph.Program(exit=False)
        program.register_script(ExampleBeforeScript)

        program()
