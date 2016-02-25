Config
======

Program has config object who always available for all runnable objects as **config property** after mounting to parent.
You can to expand it with help python module. Use environment variable **SEISMOGRAPH_CONF** for that.
Path can be import path and absolute path to python file.


How to create and switch config
-------------------------------

.. code-block:: python

    # this is base.py file

    MY_OPTION = None


Give away config

::

    SEISMOGRAPH_CONF=project.etc.base seismograph /path/to/suites/

or like

::

    SEISMOGRAPH_CONF=/path/to/project/etc/base.py seismograph /path/to/suites/


Config path can be set with creating instance of program.


.. code-block:: python

    import seismograph


    program = seismograph.Program(config_path='project.etc.base')


If you will use config path with creating instance of program that config path is default value of environment variable.
In this way config path is path by default for your program.


Available sections
------------------

+----------------------+-------------------------------------------+
| **LOGGING_SETTINGS** | dict config for logging lib               |
+----------------------+-------------------------------------------+
| **SELENIUM_EX**      | dict config for selenium extension        |
|                      | `details... <selenium_config.html>`_      |
+----------------------+-------------------------------------------+
| **ALCHEMY_EX**       | dict config for alchemy extension         |
|                      | `details... <alchemy_config.html>`_       |
+----------------------+-------------------------------------------+
| **MOCKER_EX**        | dict config for mocker extension          |
|                      | `details... <mock_server_config.html>`_   |
+----------------------+-------------------------------------------+


How can i add options to command line?
--------------------------------------


Options parser doesn't store in program context but you can to get it with help layer of program.


.. code-block:: python

    import seismograph
    from optparse import OptionGroup


    class ProgramOptionsLayer(seismograph.Program):

        def on_option_parser(self, parser):
            group = OptionGroup(parser, 'My project options')
            group.add_option('--my-option', dest='MY_OPTION')
            parser.add_option_group(group)


    suite = seismograph.Suite(__name__)


    @suite.register
    def function_test(case):
        # do something


    if __name__ == '__main__':
        seismograph.main(layers=[ProgramOptionsLayer()])
