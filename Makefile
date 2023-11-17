PATH  := $(PATH)
SHELL := /bin/bash

pre-commit:
	pre-commit run --all-files  --unsafe-fixes
