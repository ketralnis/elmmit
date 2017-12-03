#!/bin/sh

set -ev

vagrant ssh -c 'cd elmmit/python && nosetests'
