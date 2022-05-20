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
