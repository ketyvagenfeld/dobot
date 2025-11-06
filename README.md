# dobot

[![ci](https://github.com/ketyvagenfeld/dobot/workflows/ci/badge.svg)](https://github.com/ketyvagenfeld/dobot/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://ketyvagenfeld.github.io/dobot/)
[![pypi version](https://img.shields.io/pypi/v/dobot.svg)](https://pypi.org/project/dobot/)
[![gitter](https://img.shields.io/badge/matrix-chat-4DB798.svg?style=flat)](https://app.gitter.im/#/room/#dobot:gitter.im)

## Installation

```bash
pip install dobot
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv tool install dobot
```

## Running

```bash
# start robot
uv run robot
# start controller
uv run controller
# start both together
uv run robot &; uv run controller
```
