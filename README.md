## NucTransportDB
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21462868.svg)](https://doi.org/10.5281/zenodo.21462868) [![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/mbd-rwth/nuctransportdb) [![github license badge](https://img.shields.io/github/license/mbd-rwth/nuctransportdb)](https://github.com/mbd-rwth/nuctransportdb) [![Documentation Status](https://readthedocs.org/projects/nuctransportdb/badge/?version=latest)](https://nuctransportdb.readthedocs.io/en/latest/?badge=latest) [![build](https://github.com/mbd-rwth/nuctransportdb/actions/workflows/build.yml/badge.svg)](https://github.com/mbd-rwth/nuctransportdb/actions/workflows/build.yml) [![cffconvert](https://github.com/mbd-rwth/nuctransportdb/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/mbd-rwth/nuctransportdb/actions/workflows/cffconvert.yml) [![link-check](https://github.com/mbd-rwth/nuctransportdb/actions/workflows/link-check.yml/badge.svg)](https://github.com/mbd-rwth/nuctransportdb/actions/workflows/link-check.yml)




A simulation-ready database for radionuclide transport simulations, providing emitted energy data and diffusion coefficients under the condition of pure water at a reference temperature of 25 Celsius degree for a selected set of nuclides, sorption coefficient cross rock types, and chemical-species data.

## Installation

To install nuctransportdb from GitHub repository, do:

```console
git clone git@github.com:mbd-rwth/nuctransportdb.git
cd nuctransportdb
python -m pip install .
```

## Exporting Nuclide Data

Use [export_data.py](./src/nuctransportdb/export_data.py) to extract nuclide data for a specific candidate site and defined model setup. The script reads a YAML configuration file that specifies which nuclides to extract. 

### Configuration file format 

| Field                 | Description                                  |
|-----------------------|----------------------------------------------|
| `nuclide_to_consider` | List of nuclides to extract (e.g., `I-129`). |

Users have to define an input path for a site YAML file. 
A site YAML file has the following structure:

```yaml
name: name for the candidate site
description: a short description on the site
Rock_Unit_1: 
  source:  References describing the lithofacies of Rock Unit 1
  simplified_lithology: A list of strings containing different rock types, e.g., [Sandstone, Conglomerate] 
Rock_Unit_2:
  source: similar to Rock_Unit_1
  simplified_lithology: similar to Rock_Unit_1
...
```

In addition, users must provide output paths for different data types.


| Path                                          | Description                                     |
|-----------------------------------------------|-------------------------------------------------|
| `path_to_save_sorption_data`                  | Output directory for sorption coefficient data. |
| `path_to_save_nuclide_species_data`           | Output directory for nuclide species data.      |
| `path_to_save_nuclide_water_diffusivity_data` | Output directory for nuclide diffusivity data.  |
| `path_to_save_nuclide_emitted_energy_data`    | Output directory for emitted energy data.       |

### Usage:

```bash
python nuctransportdb.export_data --config path/to/nuclide_config.yaml \
    --path_to_site_yaml_file path/to/site/yaml/file \
    --path_to_save_sorption_data output/path/to/sorption_data \
    --path_to_save_nuclide_species_data output/path/to/nuclide_species_data \
    --path_to_save_nuclide_water_diffusivity_data output/path/to/nuclide_water_diffusivity_data \
    --path_to_save_nuclide_emitted_energy_data output/path/to/emitted_energy_data \
```

#### Example:
```yaml
nuclide_to_consider:
  - Cm-247
  - U-235
```

##### Running the script

```bash
python -m nuctransportdb.export_data --config  \
    --path_to_site_yaml_file input/DE_South_Claystone_Germany/site_data/DE_South_Claystone.yaml \
    --path_to_save_sorption_data output/DE_South_Claystone_Germany/sorption_data \
    --path_to_save_nuclide_species_data output/DE_South_Claystone_Germany/nuclide_species_data \
    --path_to_save_nuclide_water_diffusivity_data output/DE_South_Claystone_Germany/nuclide_water_diffusivity_data \
    --path_to_save_nuclide_emitted_energy_data output/DE_South_Claystone_Germany/emitted_energy_data \
```

## Documentation

[see our readthedocs](https://nuctransportdb.readthedocs.io/en/latest/)

## Contributing

If you want to contribute to the development of nuctransportdb,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## Credits
The code in `src/` is developed based on and heavily relies on source code from
[mbd-rwth/smart_data_hub](https://github.com/mbd-rwth/smart_data_hub).
The authors of this project is [@CQ-QianChen](https://github.com/CQ-QianChen).
