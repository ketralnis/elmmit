#!/bin/sh -e

exec vagrant ssh -c 'python -m elmmit.api_docs'

