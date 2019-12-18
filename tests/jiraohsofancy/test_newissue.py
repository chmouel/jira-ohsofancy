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
from unittest.mock import MagicMock

import iterfzf
import jira

from jiraohsofancy import config, jiraohsofancy


class FakeObject(object):
    name = None
    key = None

    def __init__(self, name, key=None):
        self.name = name
        self.key = key and key


class FakeJIRA(object):
    _projects = []
    _priorities = []
    _components = []
    _versions = []

    def set_projects(self, projects):
        for p in projects:
            self._projects.append(FakeObject(p))

    def set_priorities(self, priorities):
        for p in priorities:
            self._priorities.append(FakeObject(p))

    def set_components(self, components):
        for p in components:
            self._components.append(FakeObject(p))

    def set_versions(self, versions):
        for p in versions:
            self._versions.append(FakeObject(p))

    def projects(self):
        return self._projects

    def priorities(self):
        return self._priorities

    def project_components(self, project):
        return self._components

    def project_versions(self, project):
        return self._versions


def test_get_config(monkeypatch):
    [
        monkeypatch.delenv(x, raising=False)
        for x in ["JIRA_USERNAME", "JIRA_PASSWORD", "JIRA_SERVER"]
    ]

    # TODO(chmou): fake the os.environ
    with monkeypatch.context() as m:
        m.setenv("JIRA_USERNAME", "foo")
        m.setenv("JIRA_PASSWORD", "bar")
        m.setenv("JIRA_SERVER", "https://blah")
        j = jiraohsofancy.JIC(None)
        ret = j.set_config()
        assert (ret['username'] == "foo")

    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.write(b"""[jira]\n
server=http://hahaha\n
username=hello\n
password=moto\n
""")
    tmpfile.close()

    monkeypatch.setattr(config, "CONFIGFILE", tmpfile.name)
    j.set_config()
    assert (j.config["username"] == "hello")
    os.remove(tmpfile.name)


def test_get_objects():
    j = jiraohsofancy.JIC(None)
    fake = FakeJIRA()
    j._cnx = fake

    projects = ["INI", "MANI", "MOH"]
    iterfzf.iterfzf = MagicMock(return_value=projects[0])
    fake.set_projects(projects)
    assert (j.get_project().name == projects[0])

    priorities = ["OYLO", "ROUKO", "DEAG"]
    iterfzf.iterfzf = MagicMock(return_value=priorities[-1])
    fake.set_priorities(priorities)
    assert (j.get_priorities().name == priorities[-1])

    components = ["ATTA", "BOYA", "KASHA"]
    iterfzf.iterfzf = MagicMock(return_value=components[-2])
    fake.set_components(components)
    assert (j.get_component("fake").name == components[-2])

    versions = ["ATTA", "BOYA", "KASHA"]
    iterfzf.iterfzf = MagicMock(return_value=versions[-2])
    fake.set_versions(versions)
    assert (j.get_versions("fake").name == versions[-2])


def test_new_issue(monkeypatch):
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
    ji._cnx = MagicMock()
    ji._cnx.permalink = MagicMock()
    ji.set_config()
    ji.issue()

    ji.args.test = False
    ji.issue()
    ji._cnx.create_issue.assert_called()
    os.remove(tmpfile.name)
