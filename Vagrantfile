Vagrant.configure(2) do |config|

  config.vm.box = 'ubuntu/trusty64'

  guest_ip = "dhcp"

  if guest_ip == "dhcp"
    config.vm.network "private_network", type: guest_ip
  else
    config.vm.network "private_network", ip: guest_ip
  end

  config.vm.network "forwarded_port", host: 8080, guest: 8080
  config.vm.network "forwarded_port", host: 8000, guest: 8000
  config.vm.hostname = "elmmit.local"

  config.vm.synced_folder  ".", "/home/vagrant/elmmit"

  if File.exist? "deb-cache" then
    config.vm.synced_folder  "./deb-cache", "/var/cache/apt/archives",
        type: "rsync", rsync__auto: false
  end

  config.vm.provision "shell", inline: <<-SCRIPT
    # install everything

    set -e

    if ! which npm; then
        echo installing node
        # yep, this is really how node wants you to install it. the httpS is
        # for security
        # https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions
        curl -sL https://deb.nodesource.com/setup_9.x | bash
        apt-get install -y build-essential
        apt-get install -y nodejs
    fi

    if ! which sqlite3; then
        echo installing server dependencies
        apt-get install -y \
            sqlite3 \
            python-nose \
            python-setuptools \
            python-flask
    fi

    if ! which elm; then
        echo installing elm
        # unsafe perm flags to work around
        # https://github.com/elm-lang/elm-platform/issues/218
        # don't do this at home kiddies
        npm install -g elm --unsafe-perm=true --allow-root
        npm install -g elm-format --unsafe-perm=true --allow-root
    fi

    echo installing python server
    cd ~vagrant/elmmit/python
    python ./setup.py develop
    nosetests

    if ! [ -f /etc/init/elmmit-server.conf ]; then
        echo starting python server
        cp -vp ~vagrant/elmmit/elmmit-server.conf /etc/init/elmmit-server.conf
        start elmmit-server
        # we need to sleep for a moment so the race to create the db file doesn't
        # break it
        sleep 5

        echo polluting your database with test data
        cd ~vagrant
        su - vagrant -c "sh -e elmmit/scripts/create-test-data-inner.sh"
    fi


    echo '*********************************************************************'
    echo 'Success!'
    echo ''
    echo 'You should run ./scripts/elm-reactor.sh to start the elm environment'
    echo 'and go to http://localhost:8000 for elm'
    echo 'and go to http://localhost:8080/docs for the API docs'
    echo 'and open your code editor to the elm directory'
    echo 'and start hacking!'
    echo '*********************************************************************'
  SCRIPT

end

