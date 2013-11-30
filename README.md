# Ansible Profiles Plugin

Hierarchical variables management plugin for Ansible.

## About

Ansible uses two folders to manage variables: `host_vars` and `group_vars`. This plugin uses additional folder, `profiles`, which may consists of unlimited hierarchy of folders to represent profiles. There is only one file inside each profile directory: `vars.yml`. Child profiles always overwrite variables from parent variables. We will show how it works soon.

Here is a possible structure of `profiles` folder:

```
[profiles]
   [production]
      [datacenter1]
         vars.yml
      [datacenter2]
         vars.yml
      vars.yml
   [stage]
      vars.yml
   [qa]
      vars.yml
   [local]
      [john]
         vars.yml
      [tom]
         vars.yml
      [brett]
         vars.yml
      vars.yml
   ...
   vars.yml
```

It defines several profiles, for instance:

1. `production`
2. `production/datacenter1`
3. `local`
4. `local/john`
5. _root_ profile (represented by empty string: `""`)
6. ...

## Turn on profile

There are two ways to select profile. 

Create `.profile` file in the same folder, where your `profiles` folder is located with the 
following content:

```
profile: production/datacenter1
```

This file should be marked as ignored for your SCM tool (git, svn etc.).

Or set environment variable `ANSIBLE_PROFILE`:

```
exports ANSIBLE_PROFILE=production/datacenter1
```

If you have specified `ANSIBLE_PROFILE` environment variable, than `.profile` file will be ignored.


## Example

If `profiles/vars.yaml` has the following configuration:

```
db_port: 4000
host: roothost.com
author: StarCompany
```

And `profiles/local/vars.yml` has the following configuration:

```
db_port: 5000
host: localhost
```

And finally `profiles/local/john/vars.yml` has the following configuration:

```
db_port: 6000
host: johnhost.org
```

Then, _root_ profile will have the following state (it is completely equal 
to the content of `profiles/vars.yml`):

```
db_port: 4000
host: roothost.com
author: StarCompany
```

Profile `local` will be:

```
db_port: 5000
host: localhost
author: StarCompany
```

Profile `local/john` will be:

```
db_port: 6000
host: johnhost.org
author: StarCompany
```

## Installation

Copy `profiles.py` file to `vars_plugins` folder near your root playbook:

```
[group_vars]
[host_vars]
[profiles]
[vars_plugins]
   profiles.py      <-- here is a Profiles Plugin
hosts
playbook.yml
```
