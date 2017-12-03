#!/bin/sh

set -e

exec vagrant ssh -c 'python -m elmmit.cmd server -f elmmit.db'
