# -*- coding: utf-8 -*-

from . import pyv


def filter_result(result, **kwargs):
    if kwargs and isinstance(result, list):
        for item in result:
            comparison = all(
                item.get(k) == v
                if isinstance(v, (int, pyv.basestring))
                else
                True
                for k, v in kwargs.items()
            )
            if comparison:
                return item
        else:
            raise LookupError(
                'JSON item from response is not found by filters: {}'.format(kwargs),
            )

    return result


def _clean_dict(d1, d2):
    """
    Recursively cleans Dictionary d1
    leaving him only the keys that
    are in the d2.
    """
    def prepare_lists(l1, l2):
        assert len(l1) == len(l2)

        for i in l1:
            if isinstance(i, dict):
                l1[l1.index(i)] = _clean_dict(i, l2[l1.index(i)])

        return l1

    return dict(
        (
            k,
            _clean_dict(v, d2[k])
            if isinstance(v, dict) and isinstance(d2[k], dict)
            else
            v.sort() or d2[k].sort() or prepare_lists(v, d2[k])
            if isinstance(v, list) and isinstance(d2[k], list)
            else
            v,
        )
        for k, v in d1.items()
        if k in d2
    )


def reduce_dicts(d1, d2):
    """
    Leads dictionaries to the same species.
    The standard dictionary is d2.
    """
    return _clean_dict(d1, d2), d2
