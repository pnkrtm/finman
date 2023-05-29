SHELL := /bin/bash
CODE = src

format:
	autoflake $(CODE)
	isort $(CODE)
	black $(CODE)
