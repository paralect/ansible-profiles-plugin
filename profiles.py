# (c) 2013, Paralect <info@paralect.com>
#
# ansible-profiles-plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ansible-profiles-plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ansible-profiles-plugin.  If not, see <http://www.gnu.org/licenses/>.


import os
import glob
from ansible import errors
from ansible import utils
import ansible.constants as C

class VarsModule(object):
    
    """
    Loads variables from 'profiles/' directory in inventory base directory or in the same directory
    as the playbook. If inventory base directory and playbook base directory both contain 'profiles/'
    directory, then only 'profiles/' in playbook directory will be used.
    
    You can explicitly specify ANSIBLE_PROFILES_DIRECTORY environment variable. In this case it will 
    take precedence, and 'profiles/' folders in inventory base directory and playbook base directory
    will not be scanned at all.
    """

    def __init__(self, inventory):

        """ constructor """

        self.inventory = inventory
        self.inventory_basedir = inventory.basedir()
        
        basedir = inventory.playbook_basedir()
        if basedir is not None: 
            basedir = os.path.abspath(basedir)
        self.playbook_basedir = basedir
        
        
    def get_profiles_path(self):
        
        """
        Returns absolute path to the 'profiles/' folder or None, if it cannot be calculated.
        """
        
        # First try to use ANSIBLE_PROFILES_DIRECTORY environment variable
        # Use this path, if it exists and not empty
        env_ansible_profiles_path = os.environ.get('ANSIBLE_PROFILES_DIRECTORY')
        if env_ansible_profiles_path is not None and env_ansible_profiles_path != "":
            
            profiles_path = os.path.abspath(env_ansible_profiles_path)
            
            # In case there is no such directory, stop
            if (not os.path.exists(profiles_path) or 
                not os.path.isdir(profiles_path)):
                raise errors.AnsibleError("Profiles directory that is specified by ANSIBLE_PROFILES_DIRECTORY does not exists or not a directory: %s" % env_ansible_profiles_path)
            
            return profiles_path
        
        # Second, try to use 'profiles/' directory in playbook directory.
        # If not found, then use 'profiles/' in inventory directory.
        for basedir in [ self.playbook_basedir, self.inventory_basedir ]:
            
            if basedir is None:
                continue
            
            profiles_path = os.path.abspath(os.path.join(basedir, "profiles"))
            
            if (not os.path.exists(profiles_path) or
                not os.path.isdir(profiles_path)):
                continue
            
            return profiles_path
            
        # It means that we didn't find path to 'profiles/' directory
        return None
        
        
    def get_config(self):
        
        """
        Returns config dictionary or None, if config cannot be constructed.
        """        
            
        config = {}
        
        # First, try to use ANSIBLE_PROFILE environment variable
        # Use this variable if it exists
        env_ansible_profile = os.environ.get('ANSIBLE_PROFILE')
        if env_ansible_profile is not None:
            config['profile'] = env_ansible_profile
            
        # Second, try to use '.profile' file in playbook directory.
        # If not found, then use '.profile' in inventory directory.
        else: 
            for basedir in [ self.playbook_basedir, self.inventory_basedir ]:
                
                if basedir is None:
                    continue
                
                config_path = os.path.abspath(os.path.join(basedir, ".profile"))
                
                # If there is no such file, proceed to the next folder
                if (not os.path.exists(config_path) or
                    not os.path.isfile(config_path)):
                    continue
                
                data = utils.parse_yaml_from_file(config_path)
                if type(data) != dict:
                    raise errors.AnsibleError("%s must be stored as a dictionary/hash" % path)

                config = data
        
        if not config:
            return None
        
        return self.sanitize_config(config)

    
    def sanitize_config(self, config):
    
        if 'profile' not in config or config['profile'] is None:
            config['profile'] = ''
            
        # Remove leading '/' symbol
        # We do not support absolute paths for now
        if config['profile'].startswith('/'):
            config['profile'] = config['profile'][1:]
    
        return config
        

    def run(self, host):

        """ Main body of the plugin, does actual loading """

        results = {}

        # Load config
        config = self.get_config()
        if config is None:
            return results

        # Calculate profiles path (path to the 'profiles/' directory)
        profiles_path = self.get_profiles_path()
        if profiles_path is None:
            return results
        
        # Prepare absolute profile path (path to the actual profile folder
        # in 'profiles/' folder)
        profile_path = os.path.join(profiles_path, config['profile'])
        if not os.path.exists(profile_path) or not os.path.isdir(profile_path):
            raise errors.AnsibleError("There is no such profile: %s" % profile_path)            
        
        # Start from specified profile path
        current_path = os.path.abspath(profile_path)
        
        # Traverse directories up, until we reach 'profiles_path'
        while True:
            
            vars_path = os.path.join(current_path, "vars.yml")
            
            if (os.path.exists(vars_path) and 
                os.path.isfile(vars_path) and
                os.stat(vars_path).st_size != 0):            
            
                data = utils.parse_yaml_from_file(vars_path)
                if type(data) != dict:
                    raise errors.AnsibleError("%s must be stored as a dictionary/hash" % vars_path)            
                
                results = utils.combine_vars(data, results)
            
            # if we reached profiles folder, than we traversed all 
            # directories till profiles folder.
            if current_path == profiles_path:
                break;
            
            # select parent directory
            current_path = os.path.abspath(os.path.join(current_path, os.pardir))
            
        # all done, results is a dictionary of variables
        return results

