[![IIIA-CSIC][iiia-image]][iiia-url]

[iiia-image]: https://img.shields.io/badge/brewing%20at-IIIA--CSIC-blue
[iiia-url]: https://iiia.csic.es

# geoloc
Code for image geolocalization

## Quick start

### Set-up 

Clone the project:

```bash
git clone --recurse-submodules git@github.com:IIIA-ML/geoloc.git
cd geoloc
```

Create the `etc/geoloc.env` file and edit the default values:

```bash
cp etc/geoloc.env.default etc/geoloc.env
```

### Before every run

Run the initialization script:

```bash
source bin/init-local.sh
```

## Development routines

### Pulling changes from the repository

```bash
git pull --recurse-submodules
```

### Committing changes to the repository
* Use `git status` to determine the files that you have changed.
* For each of the modified submodules:
    * Go inside the submodule and use `git add` to include every file you have changed in a commit. 
    * Use `git commit -m "<my commit message here>"` to commit changes to the local repository"
    * Use `git push origin develop` to send the changes in the module to the repo.
* Use `git add` to include every file you have changed in the commit. Do not forget to add the directories of the 
modified submodules.
* Use `git commit -m "<my commit message here>"` to commit changes to the local repository.
* Use `git push origin develop` to send the changes to the remote repo. 

### Merging `develop` into `master`

Create a _New [pull request](https://github.com/IIIA-ML/geoloc/pulls)_ with `base:master` and `compare:develop` setting.

### Adding new `env` vars

If you need a new variable in the `etc/geoloc.env`, be sure to add it to the `etc/geoloc.env.default` with a non-secret 
default value too. 