# pylint: disable=C0103, R0801, R0914, R0915
"""Baselining process of harmonizing tally and one click files."""

from pathlib import Path
from logging import getLogger
import pandas as pd
import wblca_benchmark_v2_data_prep.utils.general as utils
from wblca_benchmark_v2_data_prep.utils.loggers import setup_logger
import wblca_benchmark_v2_data_prep.lca_results.baseline as base


def baseline():
    """ """
    # set file path locations
    current_file_path = Path(__file__)
    main_directory = current_file_path.parents[2]
    setup_logger(
        log_file_path=main_directory.joinpath("data/logs/lca_results/baseline_lca_results.log"),
        level="info",
    )

    main_baseline_logger = getLogger("8_baseline_script")
    main_baseline_logger.info("Logger has been set up.")

    main_baseline_logger.info("Begin configuration.")
    baselined_write_path = main_directory.joinpath("data/lca_results/baselined")
    tally_harmonized_path = main_directory.joinpath(
        "data/lca_results/harmonized/tally_harmonized.csv"
    )
    oneclick_harmonized_path = main_directory.joinpath(
        "data/lca_results/harmonized/oneclick_harmonized.csv"
    )
    insulation_config_path = main_directory.joinpath(
        "references/baseline_material_insulation_ecc.csv"
    )
    material_baseline_config_path = main_directory.joinpath("references/baseline_material_ecc.yml")
    config = utils.read_yaml(material_baseline_config_path)
    assert config is not None, "The config dictionary could not be set"
    baseline_material_ecc = config.get("baseline_material_ecc")
    assert (
        baseline_material_ecc is not None
    ), "Baseline embodied carbon coefficients could not be set"
    main_baseline_logger.info("End configuration.")

    # read combined files
    main_baseline_logger.info("Read combined lca_results files.")
    harmonized_tally = utils.read_csv(tally_harmonized_path)
    harmonized_oneclick = utils.read_csv(oneclick_harmonized_path)

    # read insulation config
    insulation_config = utils.read_csv(insulation_config_path)

    # run tally insulation baselining
    baselined_tally = base.baseline_insulation_tally(
        original_tally_df=harmonized_tally, insulation_data=insulation_config
    )
    # run one click insulation baselining
    baselined_oneclick = base.baseline_insulation_oneclick(
        original_oneclick_df=harmonized_oneclick, insulation_data=insulation_config
    )
    # run tally material baselining
    baselined_tally = base.baseline_typ_materials(
        original_df=baselined_tally, baseline_material_yaml_config=baseline_material_ecc
    )
    # run one click material baselining
    baselined_oneclick = base.baseline_typ_materials(
        original_df=baselined_oneclick, baseline_material_yaml_config=baseline_material_ecc
    )

    baselined_tally_for_analysis = baselined_tally[
        [
            "CLF Model ID",
            "Thickness of material (m)",
            "Cumulative instance area (m2)",
            "Cat_Mat_2",
            "Cat_Mat_3",
            "Life Cycle Stage",
            "Service Life",
            "Global Warming Potential_Ebio",
            "Mass Total (kg)",
            "MQ_1",
            "MQ_2",
            "R_value_thickness_in",
            "R_value",
            "clf_b_thickness_in",
            "clf_b_mass",
            "clf_b_gwp",
        ]
    ]

    # write to csv
    utils.write_to_csv(baselined_tally, baselined_write_path, "tally_baselined")
    utils.write_to_csv(baselined_oneclick, baselined_write_path, "oneclick_baselined")
    utils.write_to_csv(
        baselined_tally_for_analysis, baselined_write_path, "tally_baselined_reduced"
    )


if __name__ == "__main__":
    baseline()
