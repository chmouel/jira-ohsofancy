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
import configparser
import os
import pprint
import subprocess
import tempfile
import webbrowser

import iterfzf
import jira

from jiraohsofancy import config


class JIC(object):
    def __init__(self, args):
        self._cnx = False
        self.args = args
        self.config = None

    def set_config(self):
        username = os.environ.get("JIRA_USERNAME")
        password = os.environ.get("JIRA_PASSWORD")
        server = os.environ.get("JIRA_SERVER")
        if username and password and server:
            self.config = {
                'username': username,
                'password': password,
                'server': server,
            }
            return self.config
        configfile = os.path.expanduser(config.CONFIGFILE)
        if not os.path.exists(configfile):
            raise Exception("No configuration file has been set")
        cfg = configparser.ConfigParser()
        cfg.read(configfile)
        self.config = {
            "server": cfg.get('jira', 'server'),
            "username": cfg.get('jira', 'username'),
            "password": cfg.get('jira', 'password')
        }

    def inputstring(self, prompt):
        return input(prompt)

    def edit(self):
        tmpfile = tempfile.mkstemp(".md", "jira-issue-create-")[1]
        if self.args.editor:
            editor = self.args.editor
        elif 'EDITOR' in os.environ:
            editor = os.environ['EDITOR']
        else:
            editor = 'vi'
        editor = editor.split(" ")
        editor.append(tmpfile)
        subprocess.call([editor[0], *editor[1:]])
        blob = open(tmpfile, 'r').readlines()
        os.remove(tmpfile)
        return blob[0]

    def get_cnx(self):
        if self._cnx:
            return self._cnx
        self._cnx = jira.JIRA(
            server=self.config['server'],
            basic_auth=(self.config['username'], self.config['password']))
        return self._cnx

    # Not using the whole list if issue_type and only a static list cause a lot
    # of irrelevant stuff in there,
    def get_issuetype(self):
        return iterfzf.iterfzf(
            config.RESTRICT_ISSUE_TYPE, prompt="🐞 Issue Type> ")

    def _get(
            self,
            func,
            *args,
            prompt="",
    ):
        prompt += "> "
        objs = func(*args)
        if not objs:
            return
        oname = iterfzf.iterfzf(
            reversed(sorted([ob.name for ob in objs])), prompt=prompt)
        if not oname:
            raise Exception("You need to choose a " + prompt)
        return [o for o in objs if o.name == oname][0]

    def get_project(self):
        cnx = self.get_cnx()
        return self._get(cnx.projects, prompt="📚 Project")

    def get_priorities(self):
        cnx = self.get_cnx()
        return self._get(cnx.priorities, prompt="💁‍♂️ Priority")

    def get_component(self, project):
        cnx = self.get_cnx()
        return self._get(cnx.project_components, project, prompt="👜 Component")

    def get_versions(self, project):
        cnx = self.get_cnx()
        return self._get(cnx.project_versions, project, prompt="💼 Version")

    def complete(self):
        cnx = self.get_cnx()
        ctype = self.args.complete
        comp = ""
        if ctype == "component":
            comp = " ".join([
                ob.name.strip()
                for ob in cnx.project_components(self.args.project)
            ])
        elif ctype == "version":
            comp = " ".join([
                ob.name.strip()
                for ob in cnx.project_versions(self.args.project)
            ])
        elif ctype == "project":
            comp = " ".join([ob.key for ob in cnx.projects()])

        print(comp)

    def issue(self):
        cnx = self.get_cnx()
        summary = self.args.summary or self.inputstring(
            "✍🏼  Enter a title for your issue: ")
        if self.args.project:
            project = self.args.project
        else:
            _project = self.get_project()
            project = _project.key

        if self.args.version:
            version = self.args.version
        else:
            _version = self.get_versions(_project)
            version = _version and _version.name

        issuetype = self.args.issuetype or self.get_issuetype()
        if self.args.component:
            component = self.args.component
        else:
            _component = self.get_component(_project)
            component = _component and _component.name
        if self.args.priority:
            priority = self.args.priority
        else:
            _priority = self.get_priorities()
            priority = _priority and _priority.name

        assign = self.args.assign or self.inputstring(
            "🥺 Enter an assignee ('me' for yourself): ")

        if self.args.description_file:
            description = open(self.args.description_file).read()
        else:
            print(
                "🛣Launching your editor to edit the description of the issue.")
            description = self.edit()

        if assign == 'me':
            assignee = {'name': self.config['username']}

        fields = {
            'project': project,
            'summary': summary,
            'description': description,
            'issuetype': {
                'name': issuetype
            },
            'assignee': assignee,
            'components': [{
                'name': component
            }],
            'versions': [{
                'name': version
            }],
            'priority': {
                'name': priority
            }
        }

        if self.args.test:
            pprint.pprint(fields)
        else:
            created = cnx.create_issue(fields=fields)
            permalink = created.permalink()
            print(permalink)
            if self.args.open:
                webbrowser.open(permalink)
