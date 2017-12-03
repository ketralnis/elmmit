#!/bin/sh

## Copy the .deb files from the guest to the host so they can be reused between
## bootstraps. See Vagrantfile for details

set -e

if ! [ -f Vagrantfile ] || [ $(id -un) = "vagrant" ]; then
    echo "execute me from the top level of spamurai on the host like">&2
    echo "    scripts/deb-cache.sh">&2
    exit 1
fi

# make the directory if it's not present
if ! [ -e deb-cache ]; then
    mkdir deb-cache
elif ! [ -d deb-cache ]; then
    echo "deb-cache exists but isn't a directory?">&2
    exit 1
fi

# figure out the right options
OPTIONS=`vagrant ssh-config | grep -v '^Host' | awk -v ORS=' ' '{print "-o " $1 "=" $2}'`

# copy out the debs
exec scp ${OPTIONS} -rp vagrant@localhost:/var/cache/apt/archives/\*.deb ./deb-cache/
