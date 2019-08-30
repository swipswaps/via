[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

via.hypothes.is
================

This project uses the live web rewriting and banner injection capabilities of
[pywb web replay system](https://github.com/ikreymer/pywb) to automatically add
[hypothes.is](https://hypothes.is) annotations to any web pages.

Hosted at: https://via.hypothes.is/

Some examples:

[https://via.hypothes.is/http://hypothes.is/](https://via.hypothes.is/http://hypothes.is/)

[https://via.hypothes.is/http://www.autodidacts.io/openbci-brain-basics-neurons-structure-and-biology/](https://via.hypothes.is/http://www.autodidacts.io/openbci-brain-basics-neurons-structure-and-biology/)

Installing Via in a development environment
-------------------------------------------

### You will need

* Via integrates with h and the Hypothesis client, so you will need to
  set up development environments for each of those before you can develop Via:

  * https://h.readthedocs.io/en/latest/developing/install/
  * https://h.readthedocs.io/projects/client/en/latest/developers/developing/

* [Git](https://git-scm.com/)

* [pyenv](https://github.com/pyenv/pyenv)
  Follow the instructions in the pyenv README to install it.
  The Homebrew method works best on macOS.

### Clone the git repo

    git clone https://github.com/hypothesis/via.git

This will download the code into a `via` directory in your current working
directory. You need to be in the `via` directory from the remainder of the
installation process:

    cd via

### Set the environment variables

Set these environment variables in your shell (see
[Configuration](#configuration) below for documentation of all bouncer's
environment variables and what they do):

    export H_EMBED_URL="http://localhost:5000/embed.js"

### Start the development server

    make dev

The first time you run `make dev` it might take a while to start because it'll
need to install the application dependencies and build the assets.

This will start the server on port 9080 (http://localhost:9080), reload the
application whenever changes are made to the source code, and restart it should
it crash for some reason.

**That's it!** You’ve finished setting up your Via development environment. Run
`make help` to see all the commands that're available for running the tests,
linting, code formatting, etc.

### Serving Via over SSL in development

To serve Via over SSL locally, you will need to:

1. Create SSL certificates for localhost (you can reuse these for other Hypothesis
   services). See https://hyp.is/5xXOUMiuEeiDy2smINki5w/letsencrypt.org/docs/certificates-for-localhost/
2. Copy or symlink the certificate and private key as `.tlscert.pem` and
   `.tlskey.pem` respectively in the root of your checkout of this repository.
3. Start Via using `make dev-ssl`

Steps (1) and (2) are the same as for setting up SSL support in other Hypothesis
projects.

Note that this configuration is *not* suitable for production use.
Hypothesis' production services use SSL termination provided by AWS load
balancers.
