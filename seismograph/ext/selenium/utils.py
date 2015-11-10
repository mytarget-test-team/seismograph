# -*- coding: utf-8 -*-

import time
from random import randint


def random_file_name(file_ex=None):
    file_ex = file_ex or ''
    file_name = str(
        int(time.time() + randint(0, 1000)),
    )
    file_name += file_ex
    return file_name


def change_name_from_python_to_html(name):
    name = name.replace('_', '-')
    if name.startswith('-'):
        return name[1::]
    return name
