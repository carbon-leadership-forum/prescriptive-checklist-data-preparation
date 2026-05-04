"""Utility functions for use in the harmonization workflow for src.lca_results.baseline."""

import numpy as np
from logging import getLogger
import pandas as pd

# pylint: disable=E1130, W0718, C0103, W0719

baseline_logger = getLogger("lca_results.baseline")


def baseline_insulation_tally(
    original_tally_df: pd.DataFrame, insulation_data: pd.DataFrame
) -> pd.DataFrame:
    """

    Args:
        tally_df (pd.DataFrame): raw dataframe of Tally Models
    Returns:
        pd.DataFrame: baselined Tally dataframes
    """
    baseline_logger.info("Begin adding CLF baselines to tally dataframe.")

    baseline_logger.info("Create CLF baseline insulation additional columns.")
    # make a copy to ensure we're not making changes in place
    updated_tally_df = original_tally_df.copy()
    # make a mask to only apply to insulation
    insulation_mask = (updated_tally_df["Cat_Mat_3"].isin(insulation_data["insulation_types"])) & (
        updated_tally_df["Life Cycle Stage"] == "A1-A3"
    )

    # add insulation data for tally
    updated_tally_df = updated_tally_df.merge(
        insulation_data, how="left", left_on="Cat_Mat_3", right_on="insulation_types"
    )
    # create new columns
    updated_tally_df["R_value_thickness_in"] = updated_tally_df["Thickness of material (m)"]
    updated_tally_df["R_value"] = 0.0
    updated_tally_df["clf_b_thickness_in"] = updated_tally_df["Thickness of material (m)"]
    updated_tally_df["clf_b_mass"] = updated_tally_df["Mass Total (kg)"]
    updated_tally_df["clf_b_gwp"] = updated_tally_df["Global Warming Potential_Ebio"]
    updated_tally_df["clf_b_gwp_insul_only"] = updated_tally_df["Global Warming Potential_Ebio"]
    updated_tally_df["insulation_name"] = "NA"
    updated_tally_df["modeled_geo_to_mass_ratio"] = 0.0

    # make targeted changes to insulation only
    updated_tally_df.loc[
        insulation_mask,
        "R_value_thickness_in",
    ] = (
        updated_tally_df["Mass Total (kg)"]
        / updated_tally_df["Cumulative instance area (m2)"]
        / updated_tally_df["tool_density"]
        / 0.0254
    ).replace(np.inf, 0)

    updated_tally_df.loc[
        (insulation_mask)
        & (updated_tally_df["Thickness of material (m)"] == 0)
        & (updated_tally_df["Cumulative instance area (m2)"] == 0),
        "R_value_thickness_in",
    ] = (
        updated_tally_df["Mass Total (kg)"]
        / updated_tally_df["Cumulative instance volume (m3)"]
        / updated_tally_df["tool_density"]
        / 0.0254
    ).replace(
        np.inf, 0
    )

    updated_tally_df.loc[
        insulation_mask,
        "R_value",
    ] = (
        updated_tally_df["R_value_thickness_in"] * updated_tally_df["tool_r_per_in"]
    )

    updated_tally_df.loc[
        insulation_mask,
        "clf_b_thickness_in",
    ] = (
        updated_tally_df["R_value"] / updated_tally_df["epd_r_per_in"]
    )

    updated_tally_df.loc[
        insulation_mask,
        "clf_b_mass",
    ] = (
        updated_tally_df["clf_b_thickness_in"]
        * 0.0254
        * updated_tally_df["Cumulative instance area (m2)"]
        * updated_tally_df["epd_density"]
    )

    updated_tally_df.loc[
        insulation_mask,
        "clf_b_gwp",
    ] = (
        updated_tally_df["EPD GWP/m2-R1"]
        * updated_tally_df["Cumulative instance area (m2)"]
        * updated_tally_df["R_value"]
    )
    updated_tally_df.loc[
        insulation_mask,
        "clf_b_gwp_insul_only",
    ] = (
        updated_tally_df["EPD GWP/m2-R1"]
        * updated_tally_df["Cumulative instance area (m2)"]
        * updated_tally_df["R_value"]
    )

    updated_tally_df.loc[
        (updated_tally_df["clf_b_gwp"].isna()),
        "clf_b_gwp",
    ] = updated_tally_df["Global Warming Potential_Ebio"]
    updated_tally_df.loc[
        (updated_tally_df["clf_b_gwp_insul_only"].isna()),
        "clf_b_gwp_insul_only",
    ] = updated_tally_df["Global Warming Potential_Ebio"]

    updated_tally_df.loc[insulation_mask, "modeled_geo_to_mass_ratio"] = (
        updated_tally_df["Thickness of material (m)"]
        * updated_tally_df["Cumulative instance area (m2)"]
        * updated_tally_df["tool_density"]
    ) / (updated_tally_df["Mass Total (kg)"])

    updated_tally_df.loc[
        insulation_mask,
        "insulation_name",
    ] = updated_tally_df["Cat_Mat_3"]

    return updated_tally_df


def baseline_insulation_oneclick(
    original_oneclick_df: pd.DataFrame, insulation_data: pd.DataFrame
) -> pd.DataFrame:
    """

    Args:
        original_oneclick_df (pd.DataFrame): raw dataframe of One Click LCA Models
    Returns:
        pd.DataFrame: baselined One Click LCA dataframes
    """
    baseline_logger.info("Begin adding CLF baselines to one click dataframe.")

    baseline_logger.info("Create CLF baseline insulation additional columns.")
    # make a copy to ensure we're not making changes in place
    updated_oneclick_df = original_oneclick_df.copy()
    # make a mask to only apply to insulation
    insulation_mask = (
        updated_oneclick_df["Cat_Mat_5"].isin(insulation_data["insulation_types"])
    ) & (updated_oneclick_df["Life Cycle Stage"] == "A1-A3")

    # add insulation data for tally
    updated_oneclick_df = updated_oneclick_df.merge(
        insulation_data, how="left", left_on="Cat_Mat_5", right_on="insulation_types"
    )
    # create new thickness column
    updated_oneclick_df["initial_thickness_in"] = updated_oneclick_df["Thickness in"]
    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["Thickness mm"] > 0.0), "initial_thickness_in"
    ] = (updated_oneclick_df["Thickness mm"] / 25.4)

    # address issue where thickness is not defined
    updated_oneclick_df.loc[
        (insulation_mask)
        & (updated_oneclick_df["initial_thickness_in"].isna())
        & (updated_oneclick_df["Unit"] == "m2"),
        "initial_thickness_in",
    ] = (
        updated_oneclick_df["Mass Total (kg)"]
        / updated_oneclick_df["tool_density"]
        / updated_oneclick_df["User input"]
        / 0.0254
    )

    # create new area column
    updated_oneclick_df["initial_area_m2"] = updated_oneclick_df["User input"]
    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["Unit"].isin(["lbs", "m3", "sq ft"])),
        "initial_area_m2",
    ] = (
        (updated_oneclick_df["Mass Total (kg)"])
        / (updated_oneclick_df["tool_density"])
        / (updated_oneclick_df["initial_thickness_in"] * 0.0254)
    )

    # create other columns
    updated_oneclick_df["R_value"] = 0.0
    updated_oneclick_df["clf_b_mass"] = updated_oneclick_df["Mass Total (kg)"]
    updated_oneclick_df["clf_b_gwp"] = updated_oneclick_df["Global Warming Potential_Ebio"]
    updated_oneclick_df["clf_b_gwp_insul_only"] = updated_oneclick_df[
        "Global Warming Potential_Ebio"
    ]
    updated_oneclick_df["insulation_name"] = "NA"
    updated_oneclick_df["modeled_geo_to_mass_ratio"] = 0.0

    updated_oneclick_df.loc[
        insulation_mask,
        "R_value",
    ] = (
        updated_oneclick_df["initial_thickness_in"] * updated_oneclick_df["tool_r_per_in"]
    )

    updated_oneclick_df.loc[
        insulation_mask,
        "clf_b_thickness_in",
    ] = (
        updated_oneclick_df["R_value"] / updated_oneclick_df["epd_r_per_in"]
    )

    updated_oneclick_df.loc[
        insulation_mask,
        "clf_b_mass",
    ] = (
        updated_oneclick_df["clf_b_thickness_in"]
        * 0.0254
        * updated_oneclick_df["initial_area_m2"]
        * updated_oneclick_df["epd_density"]
    )

    updated_oneclick_df.loc[
        insulation_mask,
        "clf_b_gwp",
    ] = (
        updated_oneclick_df["EPD GWP/m2-R1"]
        * updated_oneclick_df["initial_area_m2"]
        * updated_oneclick_df["R_value"]
    )
    updated_oneclick_df.loc[
        insulation_mask,
        "clf_b_gwp_insul_only",
    ] = (
        updated_oneclick_df["EPD GWP/m2-R1"]
        * updated_oneclick_df["initial_area_m2"]
        * updated_oneclick_df["R_value"]
    )
    updated_oneclick_df.loc[
        (updated_oneclick_df["clf_b_gwp"].isna()),
        "clf_b_gwp",
    ] = updated_oneclick_df["Global Warming Potential_Ebio"]
    updated_oneclick_df.loc[
        (updated_oneclick_df["clf_b_gwp_insul_only"].isna()),
        "clf_b_gwp_insul_only",
    ] = updated_oneclick_df["Global Warming Potential_Ebio"]

    # modeled geo ratio calcs
    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["Unit"] == "m2"), "modeled_geo_to_mass_ratio"
    ] = (
        updated_oneclick_df["initial_thickness_in"]
        * 0.0254
        * updated_oneclick_df["initial_area_m2"]
        * updated_oneclick_df["tool_density"]
    ) / (
        updated_oneclick_df["Mass Total (kg)"]
    )

    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["Unit"] == "m3"), "modeled_geo_to_mass_ratio"
    ] = (updated_oneclick_df["User input"] * updated_oneclick_df["tool_density"]) / (
        updated_oneclick_df["Mass Total (kg)"]
    )

    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["Unit"] == "lbs"), "modeled_geo_to_mass_ratio"
    ] = (updated_oneclick_df["User input"] * 0.453592) / (updated_oneclick_df["Mass Total (kg)"])

    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["Unit"] == "sq ft"), "modeled_geo_to_mass_ratio"
    ] = (
        updated_oneclick_df["User input"]
        * 0.092903
        * updated_oneclick_df["initial_thickness_in"]
        * 0.0254
        * updated_oneclick_df["tool_density"]
    ) / (
        updated_oneclick_df["Mass Total (kg)"]
    )

    updated_oneclick_df.loc[
        insulation_mask,
        "insulation_name",
    ] = updated_oneclick_df["Cat_Mat_3"]

    return updated_oneclick_df


def baseline_typ_materials(
    original_df: pd.DataFrame, baseline_material_yaml_config: dict
) -> pd.DataFrame:
    """Substitute tool-reported A1-A3 GWP with CLF baseline material values.

    Args:
        original_oneclick_df (pd.DataFrame): raw dataframe of One Click LCA or Tally Models
    Returns:
        pd.DataFrame: baselined dataframes
    """
    baseline_logger.info("Begin adding CLF baselines to dataframe.")

    # make a copy to ensure we're not making changes in place
    updated_original_df = original_df.copy()
    baseline_logger.info("Start normalize_materials function.")

    baseline_logger.info(
        "Apply CLF baseline ECC substitution to A1-A3 rows matching (mat_group, mat_type)."
    )
    updated_original_df["baseline_material_ecc"] = 0.0
    for baseline_material_config in baseline_material_yaml_config:
        updated_original_df.loc[
            (updated_original_df["Life Cycle Stage"] == "A1-A3")
            & (updated_original_df["MQ_1"] == baseline_material_config["mat_group"])
            & (updated_original_df["MQ_2"] == baseline_material_config["mat_type"]),
            "baseline_material_ecc",
        ] = baseline_material_config["ecc"]

    baseline_logger.info("Recalculate baseline_material_gwp for matched rows (ecc * inv_mass).")
    updated_original_df.loc[updated_original_df["baseline_material_ecc"] != 0.0, "clf_b_gwp"] = (
        updated_original_df["baseline_material_ecc"] * updated_original_df["Mass Total (kg)"]
    )

    return updated_original_df
