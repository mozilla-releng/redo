# ***** BEGIN LICENSE BLOCK *****
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
# ***** END LICENSE BLOCK *****

import unittest

from redo import cmd


class CommandTests(unittest.TestCase):
    """
    Tests for `python -m redo.cmd`.
    """

    def test_cmd_remainder(self):
        """
        Passing a command that has an argument with `--` works.
        """
        cmd.main(["redo", "true", "--stuff"])
