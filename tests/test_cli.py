# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from unittest import mock

import pytest

from jiraohsofancy import cli, jiraohsofancy


@pytest.mark.usefixtures("reset_env")
class TestCLI(object):
    @mock.patch('jiraohsofancy.jiraohsofancy.JIC.set_config')
    @mock.patch('jiraohsofancy.jiraohsofancy.JIC.issue')
    def test_cli_issue(self, msetc, missue):
        argsetup = [
            '--test', '--project="PRJ1"', '--component="COM"',
            '--priority="Low"', '--summary="Hello Moto"', '--assign="me"',
            '--version=v0.1', '--description-file=tmpfile.name',
            '--issuetype=Bug'
        ]
        cli.newissue(argsetup)
        missue.assert_called()

    @mock.patch('jiraohsofancy.jiraohsofancy.JIC.set_config')
    @mock.patch('jiraohsofancy.jiraohsofancy.JIC.complete')
    def test_cli_complete(self, msetc, mcomplete):
        argsetup = [
            '--complete=version',
            '--project=PRJ1',
        ]
        cli.newissue(argsetup)
        mcomplete.assert_called()

    @mock.patch('jiraohsofancy.jiraohsofancy.JIC.issue')
    def test_configureation_file_error(self, missue):
        argsetup = [
            '--test', '--project="PRJ1"', '--component="COM"',
            '--priority="Low"', '--summary="Hello Moto"', '--assign="me"',
            '--version=v0.1', '--config-file=/tmp/null',
            '--description-file=tmpfile.name', '--issuetype=Bug'
        ]
        with pytest.raises(jiraohsofancy.ConfigurationFileError):
            cli.newissue(argsetup)
