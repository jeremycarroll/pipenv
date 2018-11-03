# -*- coding: utf-8 -*-
from __future__ import absolute_import


"""
Subcommands enabled by the --developer option.
These are usually hidden.
"""


def _make_dependency_test():
    print("Not yet implemented")


def add_developer_options(cli):
    from .options import pass_state

    @cli.command(short_help="Create dependency resolution test case.")
    @pass_state
    def maketest(
        state,
        **kwargs
    ):
        _make_dependency_test()
