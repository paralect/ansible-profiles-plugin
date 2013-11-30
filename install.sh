# Create vars_plugins directory if it not exists.
# This location should be equal to the values in ansible.cfg,
# that is usually located in /etc/ansible/ansible.cfg and/or ~/.ansible.cfg
sudo mkdir -p /usr/share/ansible_plugins/vars_plugins

# Copy profiles.py to the vars_plugins folder
sudo cp profiles.py /usr/share/ansible_plugins/vars_plugins/profiles.py