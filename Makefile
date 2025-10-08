VENV := .virtual_environment

all: help

help:
	@echo
	@echo "Targets:"
	@echo "install                     - Install environment necessary to support this project."
	@echo "install-deb                 - Install OS packages necessary to support this project. Assumes apt/dpkg package management system."
	@echo "install-pip                 - Install Python pakcages necessary to suport this project."
	@echo "code-agent-gemini-demo      - Run the demo CodeAgent using the Gemini API."
	@echo

$(VENV):
	python3 -m venv $(VENV)

install: install-deb install-pip

install-deb:
	@echo python3.12-venv is necessary for venv.
	@echo ffmpeg is necessary to read audio files for ASR
	for package in python3.12-venv ffmpeg; do \
		dpkg -l | egrep '^ii *'$${package}' ' 2>&1 > /dev/null || sudo apt install $${package}; \
	done

install-pip: $(VENV)
	. $(VENV)/bin/activate; pip3 install --upgrade -r requirements.txt

test: $(VENV)
	. $(VENV)/bin/activate; pytest tests/ -v

research-agent:
	. $(VENV)/bin/activate; python3 -m phoenix.server.main serve > /dev/null 2>&1 & python3 src/investment_research_agent.py

kill-phoenix:
	@echo "Killing Phoenix server processes..."
	@pkill -f "phoenix.server.main" && echo "Phoenix server killed" || echo "No Phoenix server processes found"

