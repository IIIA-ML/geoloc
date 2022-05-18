#!/usr/bin/env bash
# Create a virtual environment
if [[ ! -d .venv ]]; then
    python3 -m venv .venv
fi

# Install requirements into the venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# Add current dir to the $PYTHONPATH
export PYTHONPATH=$PYTHONPATH:${PWD}

# Update pulled submodules
git submodule update --recursive

# Create env file to be edited locally (and git ignored)
if [[ ! -f etc/geoloc.env ]]; then
    cp etc/geoloc.env.default etc/geoloc.env
fi

# Load local environment variables
source etc/geoloc.env && export $(cut -d= -f1 etc/geoloc.env)
