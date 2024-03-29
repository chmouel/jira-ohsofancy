#!/usr/bin/env python3
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
import readline
import sys

import jiraohsofancy.jiraohsofancy as jio
import jiraohsofancy.config as config

readline.parse_and_bind("tab: complete")


def newissue(args=None):
    parser = argparse.ArgumentParser(description="Create a JIRA issue.")
    parser.add_argument(
        "--editor", type=str, help="Editor to use default to $EDITOR or vim."
    )

    parser.add_argument("--complete", type=str, help="Used by shell completion.")

    parser.add_argument("--test", default=False, action="store_true", help="Test mode")

    parser.add_argument(
        "--open",
        default=os.environ.get("JIRA_OPEN") and True or False,
        action="store_true",
        help="Wether to open automatically "
        "the web browser after creating the issue. env:JIRA_OPEN",
    )

    parser.add_argument("--summary", type=str, help="Specify a summary for the issue.")

    parser.add_argument(
        "--project",
        type=str,
        default=os.environ.get("JIRA_PROJECT"),
        help="Specify a project. env:JIRA_PROJECT",
    )

    parser.add_argument(
        "--version",
        type=str,
        default=os.environ.get("JIRA_VERSION"),
        help="Specify a version. env:JIRA_VERSION",
    )

    parser.add_argument(
        "--issuetype",
        type=str,
        default=os.environ.get("JIRA_ISSUETYPE"),
        help="Specify an issue type. env:JIRA_ISSUETYPE",
    )

    parser.add_argument(
        "--component",
        default=os.environ.get("JIRA_COMPONENT"),
        type=str,
        help="Specify a component. env:JIRA_COMPONENT",
    )

    parser.add_argument(
        "--priority",
        default=os.environ.get("JIRA_PRIORITY"),
        type=str,
        help="Specify a priority. env:JIRA_PRIORITY",
    )

    parser.add_argument(
        "--assign",
        default=os.environ.get("JIRA_ASSIGN"),
        type=str,
        help="Assign to someone (use 'me' for yourself). env:JIRA_ASSIGN",
    )

    parser.add_argument(
        "--description-file",
        type=str,
        help="Use this file as the description content of the issue",
    )

    parser.add_argument(
        "--config-file",
        type=str,
        default=config.CONFIGFILE,
        help="Use this file for configuration.",
    )

    args = parser.parse_args(args or sys.argv[1:])
    m = jio.JIC(args)
    m.set_config()
    if args.complete:
        m.complete()
    else:
        m.issue()


if __name__ == "__main__":
    newissue()
