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

### Data crawler

To crawl Flickr data into `flickr_raw.csv` run the script:

```bash
python3 flickr_crawler.py
```

To crawl Mapillary data into `mapillary_raw.csv` run the script:

```bash
python3 mapillary_crawler.py
```

### Data preparation

Please follow [Data preparation](./Data&#32;Preparation.ipynb) for cleaning and downloading image data for multiple sources (Flickr, Mapillary).

### To run FocalNets

Please follow [FocalNets' README](./FocalNet/classification/README.md) for installation, data preparation and classification steps.

## Development routines

<details>

<summary>Note for contributors</summary>

### Branching workflow

We follow the `master-develop` workflow. 
That is, we work on the `develop` until it is stable to be merged into `master`. You can also use short-lived local 
branches that diverges from the `develop` and later merged into it. 
See the git [docs](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows) for further reading.

### Pulling changes from the repository

```bash
git pull --recurse-submodules
```

### Committing changes to the repository
* Use `git status` to determine the files that you have changed.
* For each of the modified submodules:
    * Go inside the submodule and use `git add` to include every file you have changed in a commit. 
    * Use `git commit -m "<my commit message here>"` to commit changes to the local repository.
    * Use `git push origin develop` to send the changes in the module to the repo.
* Use `git add` to include every file you have changed in the commit. Do not forget to add the directories of the 
modified submodules.
* Use `git commit -m "<my commit message here>"` to commit changes to the local repo.
* Use `git push origin develop` to send the changes to the remote repo. 

### Merging `develop` into `master`

Create a new pull request with `base:master` and `compare:develop` setting.

### Adding new `env` vars

If you need a new variable in the `etc/geoloc.env`, be sure to add it to the `etc/geoloc.env.default` with a non-secret 
default value too. 

</details>