# pylint: disable=import-error
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

from simple_term_menu import TerminalMenu
import jira

from jiraohsofancy import config


def show_menu(options: list, prompt: None | str = None) -> str:
    if prompt:
        print(prompt)
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    if not menu_entry_index:
        return ""
    return options[menu_entry_index]


class ConfigurationFileError(Exception):
    def __init__(self, message):
        self.message = message


class ChoiceceError(Exception):
    def __init__(self, message):
        self.message = message


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
                "username": username,
                "password": password,
                "server": server,
            }
            return self.config
        configfile = os.path.expanduser(self.args.config_file)
        if not os.path.exists(configfile):
            raise ConfigurationFileError("No configuration file has been set")
        cfg = configparser.ConfigParser()
        cfg.read(configfile)
        self.config = {
            "server": cfg.get("jira", "server"),
            "username": cfg.get("jira", "username", fallback=None),
            "password": cfg.get("jira", "password", fallback=None),
            "token": cfg.get("jira", "token", fallback=None),
        }
        if not self.config["password"] and not self.config["token"]:
            raise ConfigurationFileError(
                "No password or token has been set in the configuration file"
            )

    def inputstring(self, prompt):
        return input(prompt)

    def edit(self):
        tmpfile = tempfile.mkstemp(".md", "jira-issue-create-")[1]
        if self.args.editor:
            editor = self.args.editor
        elif "EDITOR" in os.environ:
            editor = os.environ["EDITOR"]
        else:
            editor = "vi"
        editor = editor.split(" ")
        editor.append(tmpfile)
        subprocess.call([editor[0], *editor[1:]])
        blob = open(tmpfile, "r", encoding="utf-8").readlines()
        os.remove(tmpfile)
        if not blob:
            raise ChoiceceError("You need to enter a description")
        return blob[0]

    def get_cnx(self):
        if self._cnx:
            return self._cnx
        kwords = {}
        kwords["server"] = self.config["server"]
        if "token" in self.config:
            kwords["token_auth"] = self.config["token"]
        elif "username" in self.config and "password" in self.config:
            kwords["basic_auth"] = (self.config["username"], self.config["password"])

        self._cnx = jira.JIRA(**kwords)
        return self._cnx

    # Not using the whole list if issue_type and only a static list cause a lot
    # of irrelevant stuff in there,
    def get_issuetype(self):
        return show_menu(config.RESTRICT_ISSUE_TYPE, prompt="🐞 Issue Type> ")

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
        oname = show_menu(sorted([ob.name for ob in objs]), prompt=prompt)
        if not oname:
            raise ChoiceceError("You need to choose a " + prompt)
        return [o for o in objs if o.name == oname][0]

    def get_project(self):
        cnx = self.get_cnx()
        return self._get(cnx.projects, prompt="📚 Project")

    def get_priorities(self):
        cnx = self.get_cnx()
        return self._get(cnx.priorities, prompt="💁‍♂️ Priority")

    # def get_project_priorities(self, project):
    #     cnx = self.get_cnx()
    #     r_json = cnx._get_json(f"project/{project}/priority")
    #     return [
    #         jira.Priority(cnx._options, cnx._session, raw_priority_json)
    #         for raw_priority_json in r_json
    #     ]

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
            comp = " ".join(
                [ob.name.strip() for ob in cnx.project_components(self.args.project)]
            )
        elif ctype == "version":
            comp = " ".join(
                [ob.name.strip() for ob in cnx.project_versions(self.args.project)]
            )
        elif ctype == "project":
            comp = " ".join([ob.key for ob in cnx.projects()])

        print(comp)
        return comp

    def issue(self):
        cnx = self.get_cnx()

        summary = self.args.summary or self.inputstring(
            "🔏 Enter a title for your issue: "
        )

        if not summary:
            raise ChoiceceError("You need to have a Summary")

        if self.args.project:
            project = self.args.project
        else:
            _project = self.get_project()
            project = _project.key

        if self.args.version:
            version = self.args.version
        else:
            _version = self.get_versions(project)
            version = _version and _version.name

        issuetype = self.args.issuetype or self.get_issuetype()
        if self.args.component:
            component = self.args.component
        else:
            _component = self.get_component(project)
            component = _component and _component.name

        if self.args.priority:
            priority = self.args.priority
        else:
            _priority = self.get_priorities()
            priority = _priority and _priority.name

        assign = self.args.assign or self.inputstring(
            "🥺 Enter an assignee ('me' for yourself): "
        )

        if not assign:
            raise ChoiceceError("You need to choose an assignee")

        if self.args.description_file:
            description = open(self.args.description_file, encoding="utf-8").read()
        else:
            print("🛣Launching your editor to edit the description of the issue.")
            description = self.edit()

        assignK = {}
        if assign:
            if assign == "me":
                assign = self.get_cnx().current_user()
            assignK = {"name": assign}

        fields = {
            "project": project,
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype},
            "assignee": assignK,
            "components": [{"name": component}],
            "versions": [{"name": version}],
            "priority": {"name": priority},
        }

        if self.args.test:
            pprint.pprint(fields)
        else:
            created = cnx.create_issue(fields=fields)
            permalink = created.permalink()

            # if self.args.agile:
            #     cnx.add_issues_to_epic(sprint, created.id)

            print(permalink)
            if self.args.open:
                webbrowser.open(permalink)
