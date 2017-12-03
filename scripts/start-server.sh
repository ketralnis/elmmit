#!/bin/sh

set -e

exec vagrant ssh -c 'sudo start elmmit-server'

