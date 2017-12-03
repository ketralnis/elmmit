#!/bin/sh
set -ev
cd ~/elmmit/elm
exec elm-reactor --address=0.0.0.0 "$@"

