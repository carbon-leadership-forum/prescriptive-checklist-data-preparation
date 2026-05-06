"""Utility functions for use in the harmonization workflow for src.lca_results.baseline."""

import numpy as np
from logging import getLogger
import pandas as pd

# pylint: disable=E1130, W0718, C0103, W0719

baseline_logger = getLogger("lca_results.baseline")

# Columns that get NaN-invalidated when the modeled geo-to-mass ratio falls outside [0.5, 2].
# Used by both Tally and One Click insulation baselining.
_GEO_RATIO_INVALIDATED_COLUMNS: list[str] = [
    "clf_b_gwp",
    "clf_b_gwp_insul_only",
    "clf_b_mass",
    "R_value",
]


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
    updated_tally_df["R_value_thickness_in"] = (
        updated_tally_df["Thickness of material (m)"] / 0.0254
    )
    updated_tally_df["R_value_untested"] = 0.0
    updated_tally_df["R_value"] = np.nan
    updated_tally_df["R_value_ok_bool"] = True
    updated_tally_df["clf_b_thickness_in"] = updated_tally_df["Thickness of material (m)"]
    updated_tally_df["clf_b_mass"] = updated_tally_df["Mass Total (kg)"]
    updated_tally_df["clf_b_gwp"] = updated_tally_df["Global Warming Potential_Ebio"]
    updated_tally_df["clf_b_gwp_insul_only"] = updated_tally_df["Global Warming Potential_Ebio"]
    updated_tally_df["insulation_name"] = "NA"
    updated_tally_df["modeled_geo_to_mass_ratio"] = 0.0
    updated_tally_df["modeled_geo_to_mass_ratio_ok_bool"] = True

    # make targeted changes to insulation only
    updated_tally_df.loc[
        (insulation_mask) & (updated_tally_df["Thickness of material (m)"] == 0),
        "R_value_thickness_in",
    ] = (
        updated_tally_df["Mass Total (kg)"]
        / updated_tally_df["Cumulative instance area (m2)"]
        / updated_tally_df["tool_density"]
        / 0.0254
    ).replace(
        np.inf, 0
    )

    updated_tally_df.loc[
        insulation_mask,
        "R_value_untested",
    ] = (
        updated_tally_df["R_value_thickness_in"] * updated_tally_df["tool_r_per_in"]
    )

    updated_tally_df.loc[
        (insulation_mask) & (updated_tally_df["R_value_untested"] > 75),
        "R_value_ok_bool",
    ] = False

    updated_tally_df.loc[
        (insulation_mask) & (updated_tally_df["R_value_untested"] <= 75),
        "R_value",
    ] = updated_tally_df["R_value_untested"]

    updated_tally_df.loc[
        (insulation_mask) & (~updated_tally_df["R_value"].isna()),
        "clf_b_thickness_in",
    ] = (
        updated_tally_df["R_value"] / updated_tally_df["epd_r_per_in"]
    )

    updated_tally_df.loc[
        (insulation_mask) & (~updated_tally_df["R_value"].isna()),
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

    updated_tally_df.loc[insulation_mask, "modeled_geo_to_mass_ratio"] = (
        updated_tally_df["R_value_thickness_in"]
        * 0.0254
        * updated_tally_df["Cumulative instance area (m2)"]
        * updated_tally_df["tool_density"]
    ) / (updated_tally_df["Mass Total (kg)"])

    _flag_geo_ratio_failures(updated_tally_df, insulation_mask)
    _invalidate_failed_geo_rows(updated_tally_df, insulation_mask, _GEO_RATIO_INVALIDATED_COLUMNS)
    _apply_post_validation_fallback(updated_tally_df, insulation_mask, mat_col="Cat_Mat_3")

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
    updated_oneclick_df["R_value_untested"] = 0.0
    updated_oneclick_df["R_value"] = np.nan
    updated_oneclick_df["R_value_ok_bool"] = True
    updated_oneclick_df["clf_b_mass"] = updated_oneclick_df["Mass Total (kg)"]
    updated_oneclick_df["clf_b_gwp"] = updated_oneclick_df["Global Warming Potential_Ebio"]
    updated_oneclick_df["clf_b_gwp_insul_only"] = updated_oneclick_df[
        "Global Warming Potential_Ebio"
    ]
    updated_oneclick_df["insulation_name"] = "NA"
    updated_oneclick_df["modeled_geo_to_mass_ratio"] = 0.0
    updated_oneclick_df["modeled_geo_to_mass_ratio_ok_bool"] = True

    updated_oneclick_df.loc[
        insulation_mask,
        "R_value_untested",
    ] = (
        updated_oneclick_df["initial_thickness_in"] * updated_oneclick_df["tool_r_per_in"]
    )

    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["R_value_untested"] > 75),
        "R_value_ok_bool",
    ] = False

    updated_oneclick_df.loc[
        (insulation_mask) & (updated_oneclick_df["R_value_untested"] <= 75),
        "R_value",
    ] = updated_oneclick_df["R_value_untested"]

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

    _flag_geo_ratio_failures(updated_oneclick_df, insulation_mask)
    _invalidate_failed_geo_rows(
        updated_oneclick_df, insulation_mask, _GEO_RATIO_INVALIDATED_COLUMNS
    )
    _apply_post_validation_fallback(updated_oneclick_df, insulation_mask, mat_col="Cat_Mat_5")

    return updated_oneclick_df


def baseline_typ_materials(
    original_df: pd.DataFrame, baseline_material_yaml_config: dict
) -> pd.DataFrame:
    """Substitute tool-reported A1-A3 GWP with CLF baseline material values.

    Args:
        original_df (pd.DataFrame): raw dataframe of One Click LCA or Tally Models
        baseline_material_yaml_config (list[dict]): list of {mat_group, mat_type, ecc}
            entries from `references/baseline_material_ecc.yml`
    Returns:
        pd.DataFrame: baselined dataframe with `baseline_material_ecc` populated for
            A1-A3 rows matching the config and `clf_b_gwp` recomputed accordingly.
    """
    baseline_logger.info("Begin adding CLF baselines to dataframe.")

    # make a copy to ensure we're not making changes in place
    updated_original_df = original_df.copy()
    baseline_logger.info("Start normalize_materials function.")

    baseline_logger.info(
        "Apply CLF baseline ECC substitution to A1-A3 rows matching (mat_group, mat_type)."
    )
    # Build a lookup DataFrame from the YAML config keyed on (MQ_1, MQ_2).
    # drop_duplicates(keep="last") mirrors the original loop's overwrite-on-collision semantics.
    lookup = (
        pd.DataFrame(baseline_material_yaml_config)
        .rename(columns={"mat_group": "MQ_1", "mat_type": "MQ_2", "ecc": "baseline_material_ecc"})
        .drop_duplicates(subset=["MQ_1", "MQ_2"], keep="last")
    )
    updated_original_df = updated_original_df.merge(lookup, how="left", on=["MQ_1", "MQ_2"])
    # Restrict substitution to A1-A3 rows; non-A1-A3 matches reset to the 0.0 sentinel.
    updated_original_df.loc[
        updated_original_df["Life Cycle Stage"] != "A1-A3", "baseline_material_ecc"
    ] = 0.0
    updated_original_df["baseline_material_ecc"] = updated_original_df[
        "baseline_material_ecc"
    ].fillna(0.0)

    baseline_logger.info("Recalculate baseline_material_gwp for matched rows (ecc * inv_mass).")
    updated_original_df.loc[updated_original_df["baseline_material_ecc"] != 0.0, "clf_b_gwp"] = (
        updated_original_df["baseline_material_ecc"] * updated_original_df["Mass Total (kg)"]
    )

    return updated_original_df


def _invalidate_failed_geo_rows(
    df: pd.DataFrame, insulation_mask: pd.Series, columns: list[str]
) -> None:
    """Set ``columns`` to NaN on insulation rows whose geo-to-mass ratio fails [0.5, 2].

    - Mutates ``df`` in place.
    - A row is "failed" if ``insulation_mask`` is True AND
      ``modeled_geo_to_mass_ratio`` is either > 2 or < 0.5.

    Args:
        df (pd.DataFrame): dataframe carrying ``modeled_geo_to_mass_ratio`` and ``columns``.
        insulation_mask (pd.Series): boolean mask of rows to consider.
        columns (list[str]): column names to overwrite with NaN on failed rows.
    """
    failed = insulation_mask & (
        (df["modeled_geo_to_mass_ratio"] > 2) | (df["modeled_geo_to_mass_ratio"] < 0.5)
    )
    df.loc[failed, columns] = np.nan


def _flag_geo_ratio_failures(df: pd.DataFrame, insulation_mask: pd.Series) -> None:
    """Set ``modeled_geo_to_mass_ratio_ok_bool = False`` for rows outside [0.5, 2].

    - Mutates ``df`` in place.
    - Pairs with ``_invalidate_failed_geo_rows`` — this one writes the QA flag,
      that one writes NaNs into the output columns.
    """
    failed = insulation_mask & (
        (df["modeled_geo_to_mass_ratio"] > 2) | (df["modeled_geo_to_mass_ratio"] < 0.5)
    )
    df.loc[failed, "modeled_geo_to_mass_ratio_ok_bool"] = False


def _apply_post_validation_fallback(
    df: pd.DataFrame, insulation_mask: pd.Series, mat_col: str
) -> None:
    """Fall back invalidated rows to original GWP/mass and label rows with their material name.

    - Mutates ``df`` in place.
    - Identical Tally/OneClick logic; only the source ``mat_col`` differs.

    Args:
        df (pd.DataFrame): dataframe being baselined.
        insulation_mask (pd.Series): boolean mask of insulation A1-A3 rows.
        mat_col (str): source column copied into ``insulation_name`` for masked rows
            (``Cat_Mat_3`` for Tally, ``Cat_Mat_5`` for One Click).
    """
    df.loc[df["clf_b_gwp"].isna(), "clf_b_gwp"] = df["Global Warming Potential_Ebio"]
    df.loc[df["clf_b_gwp_insul_only"].isna(), "clf_b_gwp_insul_only"] = df[
        "Global Warming Potential_Ebio"
    ]
    df.loc[df["clf_b_mass"].isna(), "clf_b_mass"] = df["Mass Total (kg)"]
    df.loc[insulation_mask, "insulation_name"] = df[mat_col]
