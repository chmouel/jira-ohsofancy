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
import argparse
import os
import pprint
import tempfile
from unittest import mock

import iterfzf
import pytest

from jiraohsofancy import jiraohsofancy
from . import fixtures


@pytest.mark.usefixtures("reset_env")
class TestJIC():
    def test_get_config_env(self, monkeypatch):
        monkeypatch.setenv("JIRA_USERNAME", "foo")
        monkeypatch.setenv("JIRA_PASSWORD", "bar")
        monkeypatch.setenv("JIRA_SERVER", "https://blah")
        j = jiraohsofancy.JIC(None)
        ret = j.set_config()
        assert (ret['username'] == "foo")

    def test_get_config_file(self, monkeypatch, tmp_path):
        tmpfile = tmp_path / "config.ini"
        fd = open(tmpfile, 'wb')
        fd.write(b"""[jira]\n
    server=http://hahaha\n
    username=hello\n
    password=moto\n
    """)
        fd.close()

        argsetup = argparse.Namespace(config_file=tmpfile)
        j = jiraohsofancy.JIC(argsetup)
        j.set_config()
        assert (j.config["username"] == "hello")

    def test_get_objects(self):
        j = jiraohsofancy.JIC(None)
        fake = fixtures.FakeJIRA()
        j._cnx = fake

        projects = ["INI", "MANI", "MOH"]
        iterfzf.iterfzf = mock.MagicMock(return_value=projects[0])
        fake.set_projects(projects)
        assert (j.get_project().name == projects[0])

        priorities = ["OYLO", "ROUKO", "DEAG"]
        iterfzf.iterfzf = mock.MagicMock(return_value=priorities[-1])
        fake.set_priorities(priorities)
        assert (j.get_priorities().name == priorities[-1])

        components = ["ATTA", "BOYA", "KASHA"]
        iterfzf.iterfzf = mock.MagicMock(return_value=components[-2])
        fake.set_components(components)
        assert (j.get_component("fake").name == components[-2])

        versions = ["ATTA", "BOYA", "KASHA"]
        iterfzf.iterfzf = mock.MagicMock(return_value=versions[-2])
        fake.set_versions(versions)
        assert (j.get_versions("fake").name == versions[-2])

    def test_new_issue(self, monkeypatch, reset_env):
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        tmpfile.write(b"""Alatouki la marakena""")
        tmpfile.close()

        argsetup = argparse.Namespace(
            test=True,
            open=False,
            project="SRVKP",
            component="CLI",
            priority="Low",
            summary="Hello Moto",
            assign="me",
            version='v0.1',
            description_file=tmpfile.name,
            issuetype="Bug")

        monkeypatch.setenv("JIRA_USERNAME", "foo")
        monkeypatch.setenv("JIRA_PASSWORD", "bar")
        monkeypatch.setenv("JIRA_SERVER", "https://blah")

        def mypp(_output):
            assert (_output["description"] == "Alatouki la marakena")
            assert (_output["versions"][0]['name'] == argsetup.version)
            assert (_output["summary"] == argsetup.summary)
            assert (_output["components"][0]['name'] == argsetup.component)

        monkeypatch.setattr(pprint, "pprint", mypp)
        ji = jiraohsofancy.JIC(argsetup)
        ji._cnx = mock.MagicMock()
        ji._cnx.permalink = mock.MagicMock()
        ji.set_config()
        ji.issue()

        ji.args.test = False
        ji.issue()
        ji._cnx.create_issue.assert_called()
        os.remove(tmpfile.name)

    @mock.patch('tempfile.mkstemp')
    @mock.patch('subprocess.call')
    def test_edit(self, sc, ts):
        tmpfile = tempfile.NamedTemporaryFile(delete=False)
        tmpfile.write(b"Hello Moto")
        tmpfile.close()
        ts.return_value = [0, tmpfile.name]
        argsetup = argparse.Namespace(editor=None)
        ji = jiraohsofancy.JIC(argsetup)
        ret = ji.edit()
        assert (ret == "Hello Moto")

    def test_complete(self, capsys):
        ff = fixtures.FakeJIRA()
        # Python is weird, wtf i need that for
        ff._projects = []
        ff._versions = []
        ff._components = []
        for o in [("project", ff.set_projects, ["PROJ1", "PRJ2", "PRJ3"]),
                  ("component", ff.set_components, ["COMP1", "COMP2",
                                                    "COMP3"]),
                  (["version", ff.set_versions, ["v1", "v2", "v3"]])]:
            argsetup = argparse.Namespace(complete=o[0], project="BLAH")
            o[1](o[2])

            ji = jiraohsofancy.JIC(argsetup)
            ji._cnx = ff

            ret = ji.complete()
            assert (ret == " ".join(o[2]))
