Config
======

You should to use **SELENIUM_EX** option in config for configure extension.
Config is python dictionary which has structure. Description is below.


Config description
------------------

+-----------------------+---------------------------------------------------------------------+
| **USE_REMOTE**        | Bool option. If will set True that to use remote driver.            |
+-----------------------+---------------------------------------------------------------------+
| **POLLING_TIMEOUT**   | This is time to wait for correct execution method                   |
+-----------------------+---------------------------------------------------------------------+
| **POLLING_DELAY**     | Time for sleep. If you need to sleep between iterations of          |
|                       | execution method then you can to set delay for that.                |
+-----------------------+---------------------------------------------------------------------+
| **SCRIPT_TIMEOUT**    | This is value for **set_script_timeout**                            |
|                       | method from selenium lib                                            |
+-----------------------+---------------------------------------------------------------------+
| **WAIT_TIMEOUT**      | Value for set implicitly wait to web driver                         |
+-----------------------+---------------------------------------------------------------------+
| **PAGE_LOAD_TIMEOUT** | Value for **set_page_load_timeout** method from selenium lib        |
+-----------------------+---------------------------------------------------------------------+
| **WINDOW_SIZE**       | Tuple value for set size of window                                  |
+-----------------------+---------------------------------------------------------------------+
| **MAXIMIZE_WINDOW**   | Bool value. If True then maximize window will set.                  |
+-----------------------+---------------------------------------------------------------------+
| **DEFAULT_BROWSER**   | Browser name by default.                                            |
|                       | Can be in ("ie", "opera", "chrome", "firefox", "phantomjs")         |
+-----------------------+---------------------------------------------------------------------+
| **PROJECT_URL**       | Base URL of your project.                                           |
|                       | Without slash in the end (it's recommendation only)                 |
+-----------------------+---------------------------------------------------------------------+
| **SCREEN_PATH**       | Absolute path to directory for save screenshots on problem          |
+-----------------------+---------------------------------------------------------------------+
| **LOGS_PATH**         | Absolute path to directory for save logs from driver                |
|                       | in the end of test                                                  |
+-----------------------+---------------------------------------------------------------------+
| **IE**                | Dict value. Settings for internet explorer driver.                  |
|                       | `Description is below <#internet-explorer-settings>`_.              |
+-----------------------+---------------------------------------------------------------------+
| **OPERA**             | Dict value. Settings for opera driver.                              |
|                       | `Description is below <#opera-settings>`_.                          |
+-----------------------+---------------------------------------------------------------------+
| **FIREFOX**           | Dict value. Settings for firefox driver.                            |
|                       | `Description is below <#firefox-settings>`_.                        |
+-----------------------+---------------------------------------------------------------------+
| **PHANTOMJS**         | Dict value. Settings for phantomjs driver.                          |
|                       | `Description is below <#phantomjs-settings>`_.                      |
+-----------------------+---------------------------------------------------------------------+
| **CHROME**            | Dict value. Settings for chrome driver.                             |
|                       | `Description is below <#chrome-settings>`_.                         |
+-----------------------+---------------------------------------------------------------------+
| **REMOTE**            | Dict value. Settings for remote driver.                             |
|                       | `Description is below <#remote-settings>`_.                         |
+-----------------------+---------------------------------------------------------------------+


Internet explorer settings
--------------------------

+---------------------+--------------------------------------------------------+
| **executable_path** | Absolute path to executable file                       |
+---------------------+--------------------------------------------------------+
| **capabilities**    | Capabilities for driver                                |
+---------------------+--------------------------------------------------------+
| **port**            | Port which listen driver                               |
+---------------------+--------------------------------------------------------+
| **host**            | Host for up driver                                     |
+---------------------+--------------------------------------------------------+
| **log_level**       | Logging level of executable                            |
+---------------------+--------------------------------------------------------+
| **log_file**        | Path to log file of executable                         |
+---------------------+--------------------------------------------------------+


Opera settings
--------------

+---------------------------+--------------------------------------------------+
| **executable_path**       | Absolute path to executable file                 |
+---------------------------+--------------------------------------------------+
| **desired_capabilities**  | Capabilities for driver                          |
+---------------------------+--------------------------------------------------+
| **port**                  | Port which listen driver                         |
+---------------------------+--------------------------------------------------+
| **service_log_path**      | Path to log file of executable                   |
+---------------------------+--------------------------------------------------+
| **service_args**          | Arguments of driver service                      |
+---------------------------+--------------------------------------------------+
| **opera_options**         | Instance of                                      |
|                           | **selenium.webdriver.opera.options.Options**     |
+---------------------------+--------------------------------------------------+


Firefox settings
----------------

+---------------------------+----------------------------------------------------------------+
| **firefox_profile**       | Instance of                                                    |
|                           | **selenium.webdriver.firefox.firefox_profile.FirefoxProfile**  |
+---------------------------+----------------------------------------------------------------+
| **firefox_binary**        | Bin file name                                                  |
+---------------------------+----------------------------------------------------------------+
| **timeout**               | Set timeout for client connection                              |
+---------------------------+----------------------------------------------------------------+
| **capabilities**          | Capabilities for driver                                        |
+---------------------------+----------------------------------------------------------------+
| **proxy**                 | Instance of                                                    |
|                           | **selenium.webdriver.common.proxy.Proxy**                      |
+---------------------------+----------------------------------------------------------------+
| **executable_path**       | Absolute path to executable file                               |
+---------------------------+----------------------------------------------------------------+


PhantomJS settings
------------------

+---------------------------+----------------------------------------------------------------+
| **executable_path**       | Absolute path to executable file                               |
+---------------------------+----------------------------------------------------------------+
| **port**                  | Port which listen driver                                       |
+---------------------------+----------------------------------------------------------------+
| **desired_capabilities**  | Capabilities for driver                                        |
+---------------------------+----------------------------------------------------------------+
| **service_args**          | Arguments for driver service                                   |
+---------------------------+----------------------------------------------------------------+
| **service_log_path**      | Path to log file for executable                                |
+---------------------------+----------------------------------------------------------------+


Chrome settings
---------------

+---------------------------+----------------------------------------------------------------+
| **executable_path**       | Absolute path to executable file                               |
+---------------------------+----------------------------------------------------------------+
| **port**                  | Port which listen driver                                       |
+---------------------------+----------------------------------------------------------------+
| **chrome_options**        | Instance of                                                    |
|                           | selenium.webdriver.chrome.option.Options                       |
+---------------------------+----------------------------------------------------------------+
| **service_args**          | Arguments for driver service                                   |
+---------------------------+----------------------------------------------------------------+
| **desired_capabilities**  | Capabilities for driver                                        |
+---------------------------+----------------------------------------------------------------+
| **service_log_path**      | Path to log file for executable                                |
+---------------------------+----------------------------------------------------------------+


Remote settings
---------------

+---------------------------+----------------------------------------------------------------+
| **command_executor**      | URL to selenium hub                                            |
+---------------------------+----------------------------------------------------------------+
| **desired_capabilities**  | Capabilities for driver                                        |
+---------------------------+----------------------------------------------------------------+
| **browser_profile**       | Profile for firefox browser                                    |
|                           | **selenium.webdriver.firefox.firefox_profile.FirefoxProfile**  |
+---------------------------+----------------------------------------------------------------+
| **proxy**                 | Instance of                                                    |
|                           | **selenium.webdriver.common.proxy.Proxy**                      |
+---------------------------+----------------------------------------------------------------+
| **keep_alive**            | Bool option. Use keep alive connection if True                 |
+---------------------------+----------------------------------------------------------------+
