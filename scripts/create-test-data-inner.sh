#!/bin/sh

set -e

for num in `seq 1 20`; do
    python -m elmmit.cmd -f elmmit.db create-author --author_id="user${num}"
    python -m elmmit.cmd -f elmmit.db submit-link \
        --author_id="user${num}" \
        --title="title #${num}" \
        --body="body${num}" \
        --url="http://www.google.com/?q=${num}"

done
