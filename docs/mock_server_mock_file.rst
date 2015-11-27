Mock file
=========

Mock file have own format for writing mocks and should have extension ".resp" or ".json".
This is for example.


::

    # This is comment line
    #
    # Order of lines is not important in reality
    # but body should be in the end of file
    #
    # Meta data for response
    # URL is url rule from flask lib
    #
    GET 200 /hello
    #
    # Headers
    # Content-type is preset on Mock class
    #
    Server: nginx/1.2.1
    #
    # Remind, body should be in the end
    #
    {
        "hello": "hello world!",
        "data": [
            1,
            2,
            3,
            4,
            5
        ],
        "test": {
            "test": 3.5
        }
    }
