#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_psst
----------------------------------

Tests for `psst` module.
"""

import pytest

from contextlib import contextmanager
from click.testing import CliRunner

from psst import psst
from psst import cli


class TestPsst(object):
    @classmethod
    def setup_class(cls):
        pass

    def test_something(self):
        pass

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.cli)
        assert result.exit_code == 0
        assert "cli" in result.output
        help_result = runner.invoke(cli.cli, ["--help"])
        assert help_result.exit_code == 0
        assert "Show this message and exit." in help_result.output

    @classmethod
    def teardown_class(cls):
        pass
