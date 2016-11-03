#e -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
VAGRANTFILE_LOCAL = 'Vagrantfile.local'

$script = <<SCRIPT
echo 'yes' | sudo add-apt-repository 'ppa:fkrull/deadsnakes-python2.7'
sudo apt-get update && sudo apt-get install -y python2.7 python-pip python-dev git libffi-dev libssl-dev build-essential virtualenvwrapper python-virtualenv devscripts debhelper cdbs
sudo pip install 'setuptools>=18.3' 'ansible>=2.1' versioneer markupsafe
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provision "shell", inline: $script
  config.vm.box = 'ubuntu/trusty64'

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--cpus", "2", "--ioapic", "on", "--memory", "512" ]
  end

  if File.file?(VAGRANTFILE_LOCAL)
    external = File.read VAGRANTFILE_LOCAL
    eval external
  end
end
