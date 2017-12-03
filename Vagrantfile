Vagrant.configure(2) do |config|

  config.vm.box = "trusty-cloud-image"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

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

  config.vm.provision "shell", inline: <<-SCRIPT
    # install everything

    set -ev

    echo installing system packages
    if ! which npm; then
        apt-get update
        apt-get install -y \
            nodejs-legacy \
            npm sqlite3 \
            python-nose \
            python-setuptools \
            python-flask
    fi

    if ! which elm; then
        echo installing elm
        npm install -g elm
    fi

    echo installing python package
    cd ~vagrant/elmmit/python
    python ./setup.py develop
    nosetests

    echo starting python server
    cp -vp ~vagrant/elmmit/elmmit-server.conf /etc/init/elmmit-server.conf
    stop elmmit-server || true # in case it was already running
    start elmmit-server

    cd ~vagrant
    echo creating test data
    su - vagrant -c "sh -e elmmit/scripts/create-test-data-inner.sh"

    echo '*********************************************************************'
    echo 'Success!'
    echo ''
    echo 'You should run ./scripts/elm-reactor.sh to start the elm environment'
    echo 'and go to http://localhost:8000'
    echo 'and open your code editor to the elm directory'
    echo 'and start hacking!'
    echo '*********************************************************************'
  SCRIPT

  if File.exist? "deb-cache" then
    config.vm.synced_folder  "./deb-cache", "/var/cache/apt/archives",
        type: "rsync", rsync__auto: false
  end
end

