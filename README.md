# cisa-advisories

A script for scraping, parsing and storing CISA advisories to disk.

## Installation

### uv (recommended)

`uvx --from git+https://github.com/cameron-schmidt-dev/cisa-advisories cisa-advisories -p 3.11`

### pip

`pip install git+https://github.com/cameron-schmidt-dev/cisa-advisories.git`

## Usage

`cisa-advisories --max-pages 25 --output-dir /tmp/advisories`

Saves a checkpoint in the output directory, so if you run it again, only new or newly-revised advisories are downloaded.

## MCP server

A simple MCP server is included so that Claude or other tools can be wired up to the output. Usage

`mcp install mcp.py -v ADVISORY_DIR=/tmp/advisories`