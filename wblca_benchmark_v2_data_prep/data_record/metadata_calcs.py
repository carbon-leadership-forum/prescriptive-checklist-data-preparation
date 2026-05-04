"""utils for calculating public dataset values"""

from datetime import datetime
from pathlib import Path
from logging import getLogger
import pandas as pd
from numpy import inf
from wblca_benchmark_v2_data_prep.data_record.output_format import format_buildings_metadata

metadata_logger = getLogger("data_record.metadata_calcs")


def create_total_impact_columns(
    excluding_d_wblca_output: pd.DataFrame, impact_type_list: list, internal_data: pd.DataFrame
) -> pd.DataFrame:
    """Creates total TRACI impacts and mass values for each project.

    Args:
        excluding_d_wblca_output (pd.DataFrame): WBLCA output for each project excluding module\
            D impacts and masses.
        impact_type_list (list): List of impacts and mass to be calculated.
        internal_data (pd.DataFrame): Internal dataframe created from metadata.

    Returns:
        pd.DataFrame: Columns of total impacts merged with internal data.
    """
    metadata_logger.info("Begin creating total impact columns.")
    total_impacts = calc_total_impacts(excluding_d_wblca_output, impact_type_list)

    project_metadata = internal_data.merge(
        total_impacts, how="inner", left_on="clf_model_id", right_on="CLF Model ID"
    )

    metadata_logger.info("Total impact columns created.")
    return project_metadata


def calc_total_impacts(wblca_output: pd.DataFrame, impact_type: list) -> pd.DataFrame:
    """Calculate total carbon impacts.

    This function does the following:
    - Loops over each type of impact.
    - Groups lca results by CLF Model ID.
    - Sums the impact of each model, then combines them into a dataframe.

    Args:
        wblca_output (pd.DataFrame): raw wblca output

    Returns:
        pd.DataFrame: dataframe of impacts by life cycle stage
    """
    metadata_logger.info("Begin calculating total impacts and masses for each project.")
    list_of_dfs = []
    for impact in impact_type:
        one_env_impact = (
            wblca_output.groupby(["CLF Model ID"], as_index=False)[impact]
            .sum()
            .set_index("CLF Model ID")
        )
        list_of_dfs.append(one_env_impact)
        metadata_logger.info("Calculate total impact per project for %s", impact)
    total_impacts_exc_d = pd.concat(list_of_dfs, axis=1)
    metadata_logger.info("Calculated total impacts and masses for each project.")

    return total_impacts_exc_d


def round_bldg_areas(project_metadata: pd.DataFrame) -> pd.DataFrame:
    """Rounds building areas based on criteria described in data descriptor paper.

    Args:
        project_metadata (pd.DataFrame): Project metadata of data record

    Returns:
        pd.DataFrame: Project metadata with rounded areas.
    """
    # areas to round
    metadata_logger.info("Begin rounding floor areas for each project.")
    project_areas_to_round = [
        "bldg_cfa",
        "bldg_gfa",
        "bldg_park_gfa",
        "bldg_added_gfa",
        "bldg_renovated_gfa",
    ]

    for area in project_areas_to_round:
        project_metadata[area] = project_metadata[area].mask(
            project_metadata[area] <= 2000,
            project_metadata[area].astype(float).div(10).round().mul(10).fillna(""),
        )
        project_metadata[area] = project_metadata[area].mask(
            (project_metadata[area] > 2000) & (project_metadata[area] <= 10000),
            project_metadata[area].astype(float).div(50).round().mul(50).fillna(""),
        )
        project_metadata[area] = project_metadata[area].mask(
            (project_metadata[area] > 10000) & (project_metadata[area] <= 20000),
            project_metadata[area].astype(float).div(100).round().mul(100).fillna(""),
        )
        project_metadata[area] = project_metadata[area].mask(
            (project_metadata[area] > 20000) & (project_metadata[area] <= 50000),
            project_metadata[area].astype(float).div(250).round().mul(250).fillna(""),
        )
        project_metadata[area] = project_metadata[area].mask(
            (project_metadata[area] > 50000) & (project_metadata[area] <= 100000),
            project_metadata[area].astype(float).div(500).round().mul(500).fillna(""),
        )
        project_metadata[area] = project_metadata[area].mask(
            (project_metadata[area] > 100000),
            project_metadata[area].astype(float).div(1000).round().mul(1000).fillna(""),
        )

    project_metadata["bldg_gfa"] = project_metadata["bldg_cfa"] - project_metadata[
        "bldg_park_gfa"
    ].astype(float).fillna(0)

    metadata_logger.info("Rounded floor areas for each project.")
    return project_metadata


def create_intensity_columns(project_metadata: pd.DataFrame) -> pd.DataFrame:
    """Calculates intensity columns of project metadata as follows:
    - mui_total_gfa = Mass Total (kg) / bldg_gfa
    - eci_a_to_c_gfa = Global Warming Potential_Ebio / bldg_gfa
    - epi_a_to_c_gfa = Eutrophication Potential / bldg_gfa
    - api_a_to_c_gfa = Acidification Potential / bldg_gfa
    - sfpi_a_to_c_gfa = Smog Formation Potential / bldg_gfa
    - odpi_a_to_c_gfa = Ozone Depletion Potential / bldg_gfa
    - nredi_a_to_c_gfa = Non-renewable Energy Depletion / bldg_gfa
    - mui_total_cfa = Mass Total (kg) / bldg_cfa
    - eci_a_to_c_cfa = Global Warming Potential_Ebio / bldg_cfa
    - epi_a_to_c_cfa = Eutrophication Potential / bldg_cfa
    - api_a_to_c_cfa = Acidification Potential / bldg_cfa
    - sfpi_a_to_c_cfa = Smog Formation Potential / bldg_cfa
    - odpi_a_to_c_cfa = Ozone Depletion Potential / bldg_cfa
    - nredi_a_to_c_cfa = Non-renewable Energy Depletion / bldg_cfa
    - ec_per_occupant_a_to_c = Global Warming Potential_Ebio / bldg_occupants
    - ec_per_res_unit_a_to_c = Global Warming Potential_Ebio / bldg_res_units

    The function then calculates renovation intensities using area of:
    - (bldg_added_gfa + bldg_renovated_gfa)

    Finally, it captures some error scenarios.

    Args:
        project_metadata (pd.DataFrame): dataframe of project metadata.

    Returns:
        pd.DataFrame: Project metadata including intensity columns.
    """
    metadata_logger.info("Begin creating intensity columns for each project.")
    reno_projects = ["Minor Renovation", "Major Renovation", "Tenant Improvement"]
    project_metadata["mui_total_gfa"] = (
        project_metadata["Mass Total (kg)"] / project_metadata["bldg_gfa"]
    )
    project_metadata["eci_a_to_c_gfa"] = (
        project_metadata["Global Warming Potential_Ebio"] / project_metadata["bldg_gfa"]
    )
    project_metadata["epi_a_to_c_gfa"] = (
        project_metadata["Eutrophication Potential"] / project_metadata["bldg_gfa"]
    )
    project_metadata["api_a_to_c_gfa"] = (
        project_metadata["Acidification Potential"] / project_metadata["bldg_gfa"]
    )
    project_metadata["sfpi_a_to_c_gfa"] = (
        project_metadata["Smog Formation Potential"] / project_metadata["bldg_gfa"]
    )
    project_metadata["odpi_a_to_c_gfa"] = (
        project_metadata["Ozone Depletion Potential"] / project_metadata["bldg_gfa"]
    )
    project_metadata["nredi_a_to_c_gfa"] = (
        project_metadata["Non-renewable Energy Depletion"] / project_metadata["bldg_gfa"]
    )
    project_metadata["mui_total_cfa"] = (
        project_metadata["Mass Total (kg)"] / project_metadata["bldg_cfa"]
    )
    project_metadata["eci_a_to_c_cfa"] = (
        project_metadata["Global Warming Potential_Ebio"] / project_metadata["bldg_cfa"]
    )
    project_metadata["epi_a_to_c_cfa"] = (
        project_metadata["Eutrophication Potential"] / project_metadata["bldg_cfa"]
    )
    project_metadata["api_a_to_c_cfa"] = (
        project_metadata["Acidification Potential"] / project_metadata["bldg_cfa"]
    )
    project_metadata["sfpi_a_to_c_cfa"] = (
        project_metadata["Smog Formation Potential"] / project_metadata["bldg_cfa"]
    )
    project_metadata["odpi_a_to_c_cfa"] = (
        project_metadata["Ozone Depletion Potential"] / project_metadata["bldg_cfa"]
    )
    project_metadata["nredi_a_to_c_cfa"] = (
        project_metadata["Non-renewable Energy Depletion"] / project_metadata["bldg_cfa"]
    )
    project_metadata["ec_per_occupant_a_to_c"] = (
        (project_metadata["Global Warming Potential_Ebio"] / project_metadata["bldg_occupants"])
        .astype(float)
        .fillna("NULL")
    )
    project_metadata["ec_per_res_unit_a_to_c"] = (
        (project_metadata["Global Warming Potential_Ebio"] / project_metadata["bldg_res_units"])
        .astype(float)
        .fillna("NULL")
    )

    # handle minor, major, and ti projects with different areas
    reno_mask = project_metadata["bldg_proj_type"].isin(reno_projects)
    project_metadata.loc[reno_mask, "eci_a_to_c_cfa"] = project_metadata[
        "Global Warming Potential_Ebio"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "epi_a_to_c_cfa"] = project_metadata[
        "Eutrophication Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "api_a_to_c_cfa"] = project_metadata[
        "Acidification Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "sfpi_a_to_c_cfa"] = project_metadata[
        "Smog Formation Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "odpi_a_to_c_cfa"] = project_metadata[
        "Ozone Depletion Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "nredi_a_to_c_cfa"] = project_metadata[
        "Ozone Depletion Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "mui_total_cfa"] = project_metadata["Mass Total (kg)"].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "eci_a_to_c_gfa"] = project_metadata[
        "Global Warming Potential_Ebio"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "epi_a_to_c_gfa"] = project_metadata[
        "Eutrophication Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "api_a_to_c_gfa"] = project_metadata[
        "Acidification Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "sfpi_a_to_c_gfa"] = project_metadata[
        "Smog Formation Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "odpi_a_to_c_gfa"] = project_metadata[
        "Ozone Depletion Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "nredi_a_to_c_gfa"] = project_metadata[
        "Ozone Depletion Potential"
    ].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    project_metadata.loc[reno_mask, "mui_total_gfa"] = project_metadata["Mass Total (kg)"].div(
        project_metadata["bldg_added_gfa"].astype(float).fillna(0)
        + project_metadata["bldg_renovated_gfa"].astype(float).fillna(0)
    )

    # handle infinity values
    project_metadata.loc[
        project_metadata["ec_per_res_unit_a_to_c"].isin([inf]), "ec_per_res_unit_a_to_c"
    ] = 0

    metadata_logger.info("Created intensity columns for each project.")
    return project_metadata


def null_override_project_metadata(project_metadata: pd.DataFrame) -> pd.DataFrame:
    """Creates all null and NA overrides for the data record.
    This function's overrides are described in the comments within the function.

    Args:
        project_metadata (pd.DataFrame): project metadata of the data record.

    Returns:
        _type_: project metadata with null and na overrides implemented.
    """
    metadata_logger.info("Begin creating null and NA overrides for each project.")
    zero_or_missing_float_columns = [
        "bldg_compl_year",
        "bldg_added_gfa",
        "bldg_renovated_gfa",
        "bldg_park_gfa",
        "bldg_occupants",
        "bldg_res_units",
        "bldg_therm_env_area",
        "bldg_wwr",
        "bldg_rval_walls",
        "bldg_rval_roofs",
        "str_wind_speed",
        "str_grid_long",
        "str_grid_short",
        "lca_ec_reduction_percent",
        "lca_assessment_year",
    ]
    for col in zero_or_missing_float_columns:
        metadata_logger.info("Filling missing float null and zero values for %s", col)
        zero_or_missing_float_loc(project_metadata, col)

    missing_str_columns = [
        "site_state_province",
        "bldg_ibc_type",
        "bldg_stories_above",
        "bldg_stories_below",
        "bldg_height",
        "str_seis_site_cls",
        "str_sdc",
        "str_prim_horiz_sys",
        "str_prim_vert_sys",
        "str_lat_sys",
        "str_podium",
        "str_sec_horiz_sys",
        "str_sec_vert_sys",
        "str_fdn_type",
        "str_sys_summary",
        "lca_design_phase",
        "lca_purp_of_assessment",
    ]
    for col in missing_str_columns:
        metadata_logger.info("Filling missing string null values for %s", col)
        missing_str_loc(project_metadata, col)

    metadata_logger.info("Begin other types of null overrides.")
    # sec_bldg_use: if missing then NA
    project_metadata.loc[(project_metadata["bldg_sec_use"].isna()), "bldg_sec_use"] = "NA"

    # str_sec_horiz_sys: if podium is "not a podium building" then NA
    project_metadata.loc[
        (project_metadata["str_podium"] == "Not a podium building"), "str_sec_horiz_sys"
    ] = "NA"

    # str_sec_vert_sys: if podium is "not a podium building" then NA
    project_metadata.loc[
        (project_metadata["str_podium"] == "Not a podium building"), "str_sec_vert_sys"
    ] = "NA"

    # bldg_added_gfa: if proj_type is "New Construction", then NA
    project_metadata.loc[
        (project_metadata["bldg_proj_type"] == "New Construction"), "bldg_added_gfa"
    ] = "NA"

    # bldg_renovated_gfa: if proj_type is "New Construction", then NA
    project_metadata.loc[
        (project_metadata["bldg_proj_type"] == "New Construction"), "bldg_renovated_gfa"
    ] = "NA"

    # bldg_park_gfa: if parking is "No Parking", then NA
    project_metadata["bldg_park_gfa"] = project_metadata["bldg_park_gfa"].astype(object)
    project_metadata.loc[(project_metadata["bldg_park_type"] == "No Parking"), "bldg_park_gfa"] = (
        "NA"
    )

    # NA cfa and gfa for renovation/TI projects
    reno_mask = project_metadata["bldg_proj_type"].isin(
        ["Minor Renovation", "Major Renovation", "Tenant Improvement"]
    )
    project_metadata["bldg_cfa"] = project_metadata["bldg_cfa"].astype(object)
    project_metadata["bldg_gfa"] = project_metadata["bldg_gfa"].astype(object)
    project_metadata.loc[reno_mask, "bldg_cfa"] = "NA"
    project_metadata.loc[reno_mask, "bldg_gfa"] = "NA"

    # res_units: complex, see below
    # if prim or sec use = residential, and res units is missing, the NULL
    # If prim or sec use = anything other than residential, and res units is missing, then “NA”
    prim_res_mask = project_metadata["bldg_prim_use"].isin(
        ["Residential: Multifamily (5 or more units)", "Residential: Multifamily (2-4 units)"]
    )
    sec_res_mask = project_metadata["bldg_sec_use"].isin(
        ["Residential: Multifamily (5 or more units)", "Residential: Multifamily (2-4 units)"]
    )
    empty_res_mask = project_metadata["bldg_res_units"].isna()

    res_units_null_mask = (prim_res_mask | sec_res_mask) & empty_res_mask

    project_metadata.loc[empty_res_mask, "bldg_res_units"] = "NA"
    project_metadata.loc[~(prim_res_mask | sec_res_mask), "bldg_res_units"] = "NA"
    project_metadata.loc[res_units_null_mask, "bldg_res_units"] = "NULL"

    # ec_reduction_percent: complex, see below
    # if EC reduction = No, then reduction % = NA
    # If EC reduction = yes, and reduction % missing then NULL
    # (secon case covered with zero or missing loc)
    project_metadata.loc[
        project_metadata["lca_ec_reductions"] == "No", "lca_ec_reduction_percent"
    ] = "NA"

    # ec_per_res_unit_A_to_C: if res_unit_bins NA, then NA
    project_metadata.loc[project_metadata["bldg_res_units"] == "NA", "ec_per_res_unit_a_to_c"] = (
        "NA"
    )

    # site_state: if less than 5 states exist in the dataset, then redacted
    state_count_map = project_metadata["site_state_province"].map(
        project_metadata.value_counts("site_state_province")
    )
    project_metadata.loc[state_count_map < 8, "site_state_province"] = "NULL"

    # intensities: if primary use type is parking, then intensity for gfa is NA
    project_metadata["eci_a_to_c_gfa"] = project_metadata["eci_a_to_c_gfa"].astype(object)
    project_metadata.loc[project_metadata["bldg_prim_use"] == "Parking", "eci_a_to_c_gfa"] = "NA"
    project_metadata["epi_a_to_c_gfa"] = project_metadata["epi_a_to_c_gfa"].astype(object)
    project_metadata.loc[project_metadata["bldg_prim_use"] == "Parking", "epi_a_to_c_gfa"] = "NA"
    project_metadata["api_a_to_c_gfa"] = project_metadata["api_a_to_c_gfa"].astype(object)
    project_metadata.loc[project_metadata["bldg_prim_use"] == "Parking", "api_a_to_c_gfa"] = "NA"
    project_metadata["sfpi_a_to_c_gfa"] = project_metadata["sfpi_a_to_c_gfa"].astype(object)
    project_metadata.loc[project_metadata["bldg_prim_use"] == "Parking", "sfpi_a_to_c_gfa"] = "NA"
    project_metadata["odpi_a_to_c_gfa"] = project_metadata["odpi_a_to_c_gfa"].astype(object)
    project_metadata.loc[project_metadata["bldg_prim_use"] == "Parking", "odpi_a_to_c_gfa"] = "NA"
    project_metadata["nredi_a_to_c_gfa"] = project_metadata["nredi_a_to_c_gfa"].astype(object)
    project_metadata.loc[project_metadata["bldg_prim_use"] == "Parking", "nredi_a_to_c_gfa"] = "NA"
    project_metadata["mui_total_gfa"] = project_metadata["mui_total_gfa"].astype(object)
    project_metadata.loc[project_metadata["bldg_prim_use"] == "Parking", "mui_total_gfa"] = "NA"

    metadata_logger.info("Created null and NA overrides for each project.")
    return project_metadata


def zero_or_missing_float_loc(project_metadata: pd.DataFrame, column_name: str) -> None:
    """Assigns null values for zero or missing float values in a given column.

    Args:
        project_metadata (pd.DataFrame): project metadata for data record.
        column_name (str): name of column to assign null value.
    """
    try:
        project_metadata[column_name] = project_metadata[column_name].astype(object)
    except TypeError as te:
        metadata_logger.exception("cannot cast column to object type")
        raise TypeError("cannot cast column to object type") from te
    try:
        project_metadata.loc[(project_metadata[column_name] == 0), column_name] = "NULL"
        project_metadata.loc[(project_metadata[column_name].isna()), column_name] = "NULL"
    except ValueError as ve:
        metadata_logger.exception("loc function for zero or missing floats cannot be assigned")
        raise ValueError("loc function for zero or missing floats cannot be assigned") from ve


def missing_str_loc(project_metadata: pd.DataFrame, column_name: str) -> None:
    """Assigns null value to missing string values in a given column.

    Args:
        project_metadata (pd.DataFrame): project metadata of data record
        column_name (str): name of column to assign null values to.
    """
    try:
        project_metadata.loc[(project_metadata[column_name].isna()), column_name] = "NULL"
    except ValueError as ve:
        metadata_logger.exception("loc function for missing strings cannot be assigned")
        raise ValueError("loc function for missing strings cannot be assigned") from ve


def write_buildings_metadata_to_excel(
    project_metadata: pd.DataFrame, public_dataset_directory: Path
) -> None:
    """Writes buildings metadata to excel.
    Name of file is fixed to buildings_metadata_{Date}.xlsx.

    Args:
        project_metadata (pd.DataFrame): project metadata of the data record.
        public_dataset_directory (Path): Target path of buildings_metadata
    """

    date_suffix = datetime.today().strftime("%m-%d-%Y")
    with pd.ExcelWriter(
        public_dataset_directory.joinpath(f"buildings_metadata_{date_suffix}.xlsx")
    ) as writer:

        project_metadata.to_excel(writer, sheet_name="project metadata", index=True)

        format_buildings_metadata(writer=writer)
        metadata_logger.info("Buildings_metadata has beeen saved to %s", public_dataset_directory)
