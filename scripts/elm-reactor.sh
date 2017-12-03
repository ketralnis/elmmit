#!/bin/sh -e

vagrant ssh -c 'sh -e elmmit/scripts/elm-reactor-inner.sh $@'
