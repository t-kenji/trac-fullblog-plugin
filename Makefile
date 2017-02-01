
# ----------------------------------------------------------------------------
#
# Settings. Define in Makefile.cfg or pass on command-line when needed.
#

-include Makefile.cfg

env ?= $(trac)/testenv/trac
pyshell ?= ${python}

# ----------------------------------------------------------------------------
#
# Help

define HELP

 Requires variable 'trac' set in Makefile.cfg or passed as parameter. The
 variable must point to a source checkout of trac (with test infrastructure).

 Please use 'make <target>' where <target> is one of:

  status              show which Python is used and other infos
  egg-info            generate egg meta for plugin
  trac.egg-info       generate Trac egg meta information
  testenv             generate a functional test environment to run shell
                      and server commands
  clean-bytecode      deletes project .py[oc] files
  clean-testenv       deletes the Trac functional test project

  python              run python command-line or interactive shell
    args=...          arguments to pass to python, no arguments starts a shell
    pyshell=...       if shell, alternative python shell or version
    env=...           if shell, preload a 'myenv' trac.env.Environment

  test                run plugin tests

  trac-admin          start interactive trac-admin for the project

  server              start a tracd server
    port=...          specify alternative port to use

 Settings and switches for makefile or command-line (most commands):

  trac=...            location for Trac source code
  python=...          specify alternative python version to use

 Example Makefile.cfg:

  # The path to a Trac source checkout or other full source (with tests)
  trac = ../../path/to/trac/source
  # The python executable to use, or empty for default
  python = alt/python2.x
  # The python executable to use for shell, empty for default
  pyshell = path/to/ipython2.x
  # Other commands and settings are also supported, like PYTHONPATH
  PYTHONPATH=/path/to/genshi$(SEP)/path/to/babel$(SEP)/path/to/twill

 For proper execution of all targets, ensure that all dependencies are
 available to Python, either specified in PYTHONPATH or pre-installed.
 This includes genshi, twill, svn, babel, pytz, pygments and others.

endef
export HELP

.PHONY: help

help:
	@echo "$$HELP"

all: help

# ----------------------------------------------------------------------------
#
# Main targets, setup & teardown

.PHONY: status trac.egg-info egg-info testenv
.PHONY: clean-bytecode clean-testenv

status: trac.egg-info
ifdef trac
	@echo
	@$(python) -c "import sys; \
	               print 'python: ', \
	                     sys.version.split()[0], \
	                     ' @ ', \
	                     sys.executable"
	@echo "PYTHONPATH=$$PYTHONPATH"
	@echo "server-options=$(server-options)"
	@$(python) -c "import trac; \
	               from os.path import dirname; \
	               print 'trac: ', \
	               	     trac.__version__, \
	                     ' @ ', \
	                     dirname(dirname(trac.__file__))"
	@echo "env=$(env)"
	@echo
endif
ifndef trac
	@echo "No Trac source code defined. See 'trac' variable."
	@false
endif

egg-info:
	@$(python) setup.py egg_info

trac.egg-info:
ifdef trac
	cd $(trac); \
	$(python) setup.py egg_info
endif

testenv: status
ifdef trac
	@if (test -d $(trac)/testenv); then \
		echo "'testenv' exists, use 'make clean-testenv' to remove first."; \
		echo; \
		false; fi
	# Create the testenv using Trac functional setup code
	$(python) -c "from trac.tests.functional import FunctionalTestSuite;\
				  fts = FunctionalTestSuite(); \
				  fts.setUp(); \
				  fts.tearDown()"
	# Make sure template changes gets picked up automatically
	$(python) -m trac.admin.console "$(trac)/testenv/trac" \
						config set trac auto_reload true
	# Install plugin and upgrade environment
	$(python) setup.py develop -mxd $(trac)/testenv/trac/plugins
	$(python) -m trac.admin.console "$(trac)/testenv/trac" \
						config set components tracfullblog.\* enabled
	$(python) -m trac.admin.console "$(trac)/testenv/trac" \
						upgrade
	# Done
	@echo "Project created and upgraded. Plugin linked. Hopefully."
endif

clean-bytecode:
	find . -name \*.py[co] -exec rm {} \;

clean-testenv:
ifdef trac
	rm -rf $(trac)/testenv
endif

Makefile Makefile.cfg: ;

# ----------------------------------------------------------------------------
#
# Testing

.PHONY: test

test: status
	$(python) setup.py test

# ----------------------------------------------------------------------------
#
# Shells

.PHONY: python trac-admin

python: egg-info status
ifdef args
	$(python) $(args)
else
ifdef env
		$(pyshell) -i -c "from trac.env import Environment;\
				   myenv = Environment('$(env)')"
else
		$(pyshell)
endif
endif

trac-admin: egg-info status
ifdef env
	$(python) -m trac.admin.console $(env)
else
	@echo "'env' variable was not specified. See 'make help'."
endif

# ----------------------------------------------------------------------------
#
# Server

port ?= 8000
tracdopts ?= -r
auth ?= *,$(trac)/testenv/htpasswd,tracdev

define server-options
 $(if $(port),-p $(port))\
 $(if $(auth),--basic-auth '$(auth)')\
 $(tracdopts)\
 $(if $(wildcard $(env)/VERSION),$(env),-e $(env))
endef

.PHONY: server

server: trac.egg-info egg-info
ifdef env
	$(python) -m trac.web.standalone $(server-options)
else
	@echo "'env' variable was not specified. See 'make help'."
endif

# ----------------------------------------------------------------------------
#
# Setup environment variables

python-home := $(python.$(if $(python),$(python),$($(db).python)))

ifeq "$(OS)" "Windows_NT"
    ifndef python-home
        # Detect location of current python 
        python-exe := $(shell python -c 'import sys; print sys.executable')
        python-home := $(subst \python.exe,,$(python-exe))
    endif
    SEP = ;
    python-bin = $(python-home)$(SEP)$(python-home)/Scripts
else
    SEP = :
endif

ifdef python-bin
    export PATH := $(python-bin)$(SEP)$(PATH)
endif
export PYTHONPATH := .$(SEP)$(trac)$(SEP)$(PYTHONPATH)

# ----------------------------------------------------------------------------
#
# Misc.

space = $(empty) $(empty)
comma = ,
