import argparse
import os
import sys
from importlib.resources import files
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
import scipy
from scipy import stats
from scipy.stats import lognorm
from scipy.stats import norm
from nuctransportdb.add_default import add_default_df
from nuctransportdb.data_tagging import filter_tagged_data
from nuctransportdb.dataframe2yaml import convert_to_flow_sequence
from nuctransportdb.dataframe2yaml import export2yaml
from nuctransportdb.merge_method import merge_property_value
from nuctransportdb.property2dataframe import load_nuclide_sorption_data

from nuctransportdb.merge_method import generate_lognorm, format_number_adaptive
from nuctransportdb.generate_id import get_entry_str
from nuctransportdb.generate_id import ntd_namespace
from uuid import UUID
import uuid


def load_all_emitted_energy():
    data_path = files("nuctransportdb") / "dataset"
    path_to_yaml = os.path.join(data_path, "emitted_energy", "emitted_energy.yaml")
    with open(path_to_yaml, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_all_species_type_data():
    data_path = files("nuctransportdb") / "dataset"
    path_to_yaml = os.path.join(data_path,"species_type", "species_type.yaml")
    with open(path_to_yaml, encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_diffusivity_data(diffusion_group):
    # load diffusivity data
    data_path = files("nuctransportdb") / "dataset" / "diffusivity_in_water"
    with open(os.path.join(data_path, f"{diffusion_group}.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def export_species_diffusivity_data(input_config) -> None:

    with open(input_config["path_to_site_yaml"], encoding="utf-8") as f:
            yaml_config = yaml.safe_load(f)
    yaml_config.pop("name", None)
    yaml_config.pop("description", None)

    all_species_type_data = load_all_species_type_data()
    nuclides_list = input_config["nuclide_to_consider"]

    selected_species_type_data = {nuclide: all_species_type_data[nuclide] for nuclide in nuclides_list}

    path_to_save_nuclide_species_data = input_config["path_to_save_nuclide_species_data"]

    with open(os.path.join(path_to_save_nuclide_species_data, "species_type.yaml"), "w") as f:
        yaml.safe_dump(selected_species_type_data, f, sort_keys=False)

    slow_categories = ["alkaline_earth_metal","transition_metal","lanthanide","actinide"]
    fast_element = ["Cl", "Br", "I", "K", "Cs", "Ag", "H"]

    results = {}
    for nuclide in nuclides_list:
        info = all_species_type_data.get(nuclide)
        if info is None:
            results[nuclide] = load_diffusivity_data(diffusion_group="high_diffusivity")['diffusion_coefficient']
            continue

        category = (info.get("element_category") or "").lower()

        element = nuclide.partition("-")[0]

        if category in slow_categories:
            results[nuclide] = load_diffusivity_data(diffusion_group="low_diffusivity")['diffusion_coefficient']
        elif element in fast_element:
            results[nuclide] = load_diffusivity_data(diffusion_group="high_diffusivity")['diffusion_coefficient']
        else: # Unclassified nuclided treated as fast per your rule
            results[nuclide] = load_diffusivity_data(diffusion_group="high_diffusivity")['diffusion_coefficient']

        lognorm_dist = generate_lognorm(value=results[nuclide][0]['value'], value_std=results[nuclide][0]['value_std'], value_min=0, as_string=True)
        samples_string = lognorm_dist + '.rvs(size=1000000, random_state=21)'
        samples = eval(samples_string)

        results[nuclide][0]['value'] = format_number_adaptive(np.mean(samples))
        results[nuclide][0]['value_min'] = format_number_adaptive(np.min(samples))
        results[nuclide][0]['value_max'] = format_number_adaptive(np.max(samples))
        results[nuclide][0]['value_std'] = format_number_adaptive(np.std(samples))
        results[nuclide][0]['unit_base'] = convert_to_flow_sequence(results[nuclide][0]['unit_base'])
        results[nuclide][0]['source'] = 'merged'
        results[nuclide][0]['probability_distribution']['sampled_data'] = samples_string
        results[nuclide][0]['description'] = f"A lognormal distribution fitted from 1 dataset with id: {results[nuclide][0]['tag']['ID']}."
        results[nuclide][0]['tag'] = {'ID': None}

        keys_to_remove = ['variable_name', 'variable_unit_str', 'variable_unit_base']
        for key in keys_to_remove:
            results[nuclide][0].pop(key, None)
            
        NTD_NAMESPACE = ntd_namespace()
        results[nuclide][0]['tag']["ID"] = str(uuid.uuid5(NTD_NAMESPACE, get_entry_str(results[nuclide][0], nuclide_name=nuclide)))


    path_to_save_nuclide_water_diffusivity_data = input_config["path_to_save_nuclide_water_diffusivity_data"]
    for rock_unit in yaml_config.keys():
        with open(os.path.join(path_to_save_nuclide_water_diffusivity_data, f"{rock_unit}.yaml"), "w") as f:
            yaml.safe_dump(results, f, sort_keys=False)

def export_nuclide_emitted_energy(input_config) -> None:
    all_emitted_energy = load_all_emitted_energy()
    nuclides_list = input_config["nuclide_to_consider"]
    nuclide_emitted_energy = {}
    for nuclide in nuclides_list:
        info = all_emitted_energy.get(nuclide)
        if info is None:
            nuclide_emitted_energy[nuclide] = {"source": None,
                                                "alpha": 0.0,
                                                "electron": 0.0,
                                                "photon": 0.0,
                                                "total": 0.0,
                                                "unit_str": "kg*m^3/s^2",
                                                "unit_base": convert_to_flow_sequence([1, 2, -2, 0, 0, 0, 0])}
            continue
        MEV_TO_JOULE = 1.602176634e-13
        nuclide_emitted_energy[nuclide] = {"source": info["source"],
                                            "alpha": float(info["alpha"] * MEV_TO_JOULE),
                                            "electron": float(info["electron"] * MEV_TO_JOULE),
                                            "photon": float(info["photon"] * MEV_TO_JOULE),
                                            "total": float(info["total"] * MEV_TO_JOULE),
                                            "unit_str": "kg*m^3/s^2",
                                            "unit_base": convert_to_flow_sequence([1, 2, -2, 0, 0, 0, 0])}


    path_to_save_nuclide_emitted_energy_data = input_config["path_to_save_nuclide_emitted_energy_data"]


    with open(os.path.join(path_to_save_nuclide_emitted_energy_data, "emitted_energy.yaml"), "w") as f:
        yaml.safe_dump(nuclide_emitted_energy, f, sort_keys=False)


def export_sorption_data_for_site(input_config) -> None:
    with open(input_config["path_to_site_yaml"], encoding="utf-8") as f:
        yaml_config = yaml.safe_load(f)
    yaml_config.pop("name", None)
    yaml_config.pop("description", None)

    nuclides_list = input_config["nuclide_to_consider"]

    for rock_unit, rock_infos in yaml_config.items():

        tag_dict = {"simplified_lithology": rock_infos["simplified_lithology"]}

        mdfnsds = []
        for nuclide in nuclides_list:
            element = nuclide.partition("-")[0]
            # load all sorption data for all nuclides
            nsd = load_nuclide_sorption_data()
            # filter data with simplified lithologies
            fnsd = filter_tagged_data(nsd, tag_dict)
            fnsd = fnsd[fnsd["nuclide"]==element]

            # add default data based on the litholgies for the merged rock unit
            dfnsd = add_default_df(fnsd, tag_dict["simplified_lithology"], nuclide=element)
            # Fill none simplified_lithology with rock_type
            dfnsd["simplified_lithology"] = dfnsd["simplified_lithology"].fillna(
                dfnsd["rock_type"],
            )
            # make sure all properties are sorption_coefficient
            dfnsd["nuclide_property"] = "sorption_coefficient"
            dfnsd["nuclide"] = nuclide

            mdfnsd = merge_property_value(dfnsd, source_type="merged")
            mdfnsds.append(mdfnsd)

        result = pd.concat(mdfnsds, ignore_index=True)

        # Replace np.nan with None
        result = result.replace({np.nan: None, "": None})

        # save the sorption data for the specific rock unit
        path_to_save_sorption_data = input_config["path_to_save_sorption_data"]

        export2yaml(result, f"{path_to_save_sorption_data}/{rock_unit}.yaml")

REQUIRED_FIELDS = ["nuclide_to_consider"]

def parse_args():

    parser = argparse.ArgumentParser(
        description="Export nuclide transport data based on a YAML configuration file.",
    )

    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Path to the rock configuration YAML file.",
    )

    parser.add_argument(
        "--path_to_site_yaml_file",
        type=str,
        required=True,
        help="Path to the site YAML file (contains a summary of rock unit lithologies).",
    )

    parser.add_argument(
        "--path_to_save_sorption_data",
        type=str,
        required=True,
        help="Output directory for sorption coefficient data.",
    )

    parser.add_argument(
        "--path_to_save_nuclide_species_data",
        type=str,
        required=True,
        help="Output directory for nuclide species data.",
    )

    parser.add_argument(
        "--path_to_save_nuclide_water_diffusivity_data",
        type=str,
        required=True,
        help="Output directory for nuclide diffusivity data.",
    )
    parser.add_argument(
        "--path_to_save_nuclide_emitted_energy_data",
        type=str,
        required=False,
        help="Output directory for emitted energy data.",
    )

    return parser.parse_args()

def load_nuclide_yaml_config(config_path):
    """Load a YAML configuration file.

    Args:
        config_path (str): Path to the input YAML configuration file

    Raises:
        FileNotFoundError: not found message.
        ValueError: empty config file message.

    Returns:
        dict: configuration dictionary.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        msg = f"Config file not found: {config_path}"
        raise FileNotFoundError(msg)

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        msg = f"Config file is empty: {config_path}"
        raise ValueError(msg)

    return config

def validate_config(config) -> None:
    """Validate that all required fields are present in the config.

    Args:
        config (dict): configuration dictionary

    Raises:
        ValueError: missing required field message.
    """
    missing = [field for field in REQUIRED_FIELDS if field not in config]
    if missing:
        msg = f"Missing required config field(s): {missing}"
        raise ValueError(msg)

def build_nuclide_config(config_path, path_to_site_yaml, path_to_save_sorption_data, path_to_save_nuclide_species_data, path_to_save_nuclide_water_diffusivity_data, path_to_save_nuclide_emitted_energy_data):
    """Load and validate, a site configuration file. Save rock, site, geometry data with output paths given via CLI.

    Args:
        config_path (str): path to the configuration file.
        path_to_site_yaml (str): Path to a site YAML file.
        path_to_save_sorption_data (str): Output directory for sorption coefficient data.
        path_to_save_nuclide_species_data (str): Output directory for nuclide species data.
        path_to_save_nuclide_water_diffusivity_data (str): Output directory for nuclide diffusivity data.
        path_to_save_nuclide_emitted_energy_data (str): Output directory for emitted energy data.

    Returns:
        dict: configuration dictionary with output paths given via CLI.
    """
    raw_config = load_nuclide_yaml_config(config_path)
    validate_config(raw_config)

    return {
        "nuclide_to_consider": raw_config["nuclide_to_consider"],
        "path_to_site_yaml": path_to_site_yaml,
        "path_to_save_sorption_data": path_to_save_sorption_data,
        "path_to_save_nuclide_species_data": path_to_save_nuclide_species_data,
        "path_to_save_nuclide_water_diffusivity_data": path_to_save_nuclide_water_diffusivity_data,
        "path_to_save_nuclide_emitted_energy_data": path_to_save_nuclide_emitted_energy_data,
    }


def main() -> None:
    args = parse_args()

    try:
        nuclide_config = build_nuclide_config(
            args.config,
            args.path_to_site_yaml_file,
            args.path_to_save_sorption_data,
            args.path_to_save_nuclide_species_data,
            args.path_to_save_nuclide_water_diffusivity_data,
            args.path_to_save_nuclide_emitted_energy_data,
        )
    except (FileNotFoundError, ValueError):
        sys.exit(1)

    for path_key in ["path_to_save_sorption_data", "path_to_save_nuclide_water_diffusivity_data", "path_to_save_nuclide_species_data"]:
        Path(nuclide_config[path_key]).mkdir(parents=True, exist_ok=True)

    export_species_diffusivity_data(nuclide_config)
    export_sorption_data_for_site(nuclide_config)

    if args.path_to_save_nuclide_emitted_energy_data is not None:
        Path(nuclide_config["path_to_save_nuclide_emitted_energy_data"]).mkdir(parents=True, exist_ok=True)
        export_nuclide_emitted_energy(nuclide_config)

if __name__ == "__main__":
    main()
