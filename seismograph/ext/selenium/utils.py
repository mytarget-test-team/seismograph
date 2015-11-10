# -*- coding: utf-8 -*-


def change_name_from_python_to_html(name):
    name = name.replace('_', '-')
    if name.startswith('-'):
        return name[1::]
    return name
