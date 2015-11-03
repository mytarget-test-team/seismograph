# -*- coding: utf-8 -*-


def create_reason(name, desc, *args):
    return u'{} ({}): \n{}\n\n'.format(
        name, desc, u'\n'.join(u'  {}'.format(s) for s in args),
    )


def get_pool_size_of_value(value, in_two=False):
    from multiprocessing import cpu_count

    size = value

    if size <= 0:
        size = cpu_count()

    if in_two:
        return int(round(size / 2)) or 2

    return size
