[![Codecov](https://img.shields.io/codecov/c/github/chmouel/jira-ohsofancy/master.svg?style=flat-square)](https://codecov.io/gh/chmouel/jira-ohsofancy)  [![License](https://img.shields.io/pypi/l/jira-ohsofancy.svg?style=flat-square)](https://pypi.python.org/pypi/jira-ohsofancy) [![PYPI](https://img.shields.io/pypi/v/jira-ohsofancy.svg?style=flat-square)](https://pypi.python.org/pypi/jira-ohsofancy) 

# JIRA - OHSOFANCY

A collection of tools for JIRA. It aim to get your JIRA tasks done as quickly as possible.

 * **jira-new-issue** -- A simple tool to create a Jira Issue and save you 3 minutes and 37 seconds back to your life each time you are creating an issue on the web interface.
This will use [fzf](https://github.com/junegunn/fzf) for quick filtering and spin up your `$EDITOR` so you can confortably type your issue description.

# REQUIREMENT

* python3
* [fzf](https://github.com/junegunn/fzf)

# INSTALL

You can install the latest release version directly from the https://pypi.io repository :

```shell
python3 -mpip install jira-ohsofancy
```

Or if you want to use the latest version from GitHUB you can do :

```shell
python3 -mpip install git+https://github.com/chmouel/jira-ohsofancy
```

You can as wel install the [zsh completion file](./misc/jira-new-issue.completion.zsh)
to your `fpath` as documented on this [stackoverflow
answer](https://unix.stackexchange.com/a/33898) to get the zsh completion. 
The completion tries to be pretty fancy too, it will complete `components`, `version`
of the specified project and do the right thing when you specify another project than the default one.

# Configuration

You need to have a file called `~/.config/jira.ini` with this kind of content :

```ini
[jira]
server=https://issue.redhat.com/
username=joe # optional if you use token
password=jane # optional if you use token
token=token # optional if you use username/token
```

Most command can be overriden by environmenet flags for example for example `JIRA_PROJECT` will be
used unless specified with the `--project` flag.

See `--help` for a complete list of environment variables that can be specified.


# Usage

Unless you override it with a flag (see `--help` for details) it will ask you
interactively with `fzf` what's needed to create an issue.

If you specify the `--description-file` it will use the file content as the description.

# Demo


https://user-images.githubusercontent.com/98980/214076784-c5e5c2de-1544-4c63-9fd9-0576176c0fcc.mov



# Authors

[Chmouel Boudjnah](https://github.com/chmouel)

# License

Apache 2.0
