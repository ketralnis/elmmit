#!/bin/sh

set -ev

exec vagrant ssh -c 'python -m elmmit.cmd -f elmmit.db server'
