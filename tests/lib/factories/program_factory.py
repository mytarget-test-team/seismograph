# -*- coding: utf-8 -*-

from seismograph.program import Program


def create(config, **kwargs):
    program = Program()
    set_config(program, config)
    return program


def set_config(program, config):
    program._Program__config = config
