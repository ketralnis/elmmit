Vagrant.configure(2) do |config|

  config.vm.box = "trusty-cloud-image"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  guest_ip = "dhcp"

  if guest_ip == "dhcp"
    config.vm.network "private_network", type: guest_ip
  else
    config.vm.network "private_network", ip: guest_ip
  end

  # http. puts the web UI at http://localhost:8080
  config.vm.network "forwarded_port", host: 8080, guest: 8080
  config.vm.hostname = "elmmit.local"

  config.vm.synced_folder  ".", "/home/vagrant/elmmit"

  config.vm.provision "shell", inline: <<-SCRIPT
    # install everything

    set -ev

    apt-get update
    apt-get install -y nodejs-legacy npm sqlite3 python-nose python-setuptools python-flask

    npm install -g elm

    cd ~vagrant/elmmit/python
    python ./setup.py develop
    nosetests
    # cp -vp ~vagrant/elmmit/elmmit-server.rc /etc/init/elmmit-server.conf

    # echo 'export PATH=$PATH:/home/vagrant/elmmit/node_modules' >> /home/vagrant/.bash_profile
    # chown vagrant:vagrant /home/vagrant/.bash_profile
  SCRIPT

  if File.exist? "deb-cache" then
    config.vm.synced_folder  "./deb-cache", "/var/cache/apt/archives",
        type: "rsync", rsync__auto: false
  end
end

