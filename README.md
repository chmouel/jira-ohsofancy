# JIRA - OHSOFANCY

A simple tool to create a Jira Issue and save you 3 minutes and 37 seconds back to your life each time you are creating an issue on the web interface.

This will use fzf for quick filtering of fields and spin up your `$EDITOR` to type your issue description.

# REQUIREMENT

* python3
* [fzf](https://github.com/junegunn/fzf)

# INSTALL

This will the binary `jira-new-issue` into your PATH and the depedencies that goes with it.

```shell
python3 -m pip install -r requirements.txt git+https://github.com/chmouel/jira-ohsofancy
```

# Configuration

You need to have a file called `~/.config/jira.ini` with this kind of content :

```ini
[jira]
server=https://localhost.examle.com
username=joe
password=jane
```

# Usage

It is pretty much interactive at the moment so it will ask you for whatever you
fields it needs to.


# Demo

[![asciicast](https://asciinema.org/a/w7MmcseAkk4vBg3JlSMIbC1dW.svg)](https://asciinema.org/a/w7MmcseAkk4vBg3JlSMIbC1dW)

# Authors

Chmouel Boudjnah <chmouel@chmouel.com>

# License

Apache 2.0
