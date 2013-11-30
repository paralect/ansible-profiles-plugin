# Ansible Profiles Plugin

Hierarchical variables management plugin for Ansible.

## About

Ansible uses two folders to manage variables: `host_vars` and `group_vars`. This plugin uses additional folder, `profiles`, which may consists of unlimited hierarchy of folders to represent profiles. There is only one file inside each profile directory: `vars.yml`. 

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


