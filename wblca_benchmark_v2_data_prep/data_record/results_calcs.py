"""utils for calculating public dataset values"""

from datetime import datetime
from pathlib import Path
from logging import getLogger
import pandas as pd
from wblca_benchmark_v2_data_prep.data_record.output_format import format_lca_full_results

lca_full_results_logger = getLogger("data_record.metadata_calcs")


def prep_internal_data_for_area_calcs(internal_data: pd.DataFrame) -> pd.DataFrame:
    """Selects area columns from internal_data for lca_full_results.

    Args:
        internal_data (pd.DataFrame): internal data created from metadata.

    Returns:
        pd.DataFrame: Subset of internal data area columns.
    """
    lca_full_results_logger.info("Begin prepping internal data for area calcs.")
    internal_data_for_area = (
        internal_data[
            [
                "bldg_cfa",
                "bldg_gfa",
                "bldg_park_gfa",
                "bldg_added_gfa",
                "bldg_renovated_gfa",
                "bldg_proj_type",
                "clf_model_id",
                "project_index",
            ]
        ]
        .rename(columns={"clf_model_id": "CLF Model ID"})
        .set_index("CLF Model ID")
    )
    lca_full_results_logger.info(
        "Created subset of internal data for area calcs in full_lca_results."
    )

    return internal_data_for_area


def prep_internal_wblca_output(
    internal_data_for_area: pd.DataFrame, wblca_output: pd.DataFrame, scope_type: list
) -> pd.DataFrame:
    """Selects lca_results based on scope and index criteria.

    This function does the following:
    - Filters projects not in internal_data
    - Filters impacts not in the selected scope types.

    Args:
        internal_data_for_area (pd.DataFrame): Internal data with area columns.
        wblca_output (pd.DataFrame): lca results from lca_results script.
        scope_type (list): list of acceptable scopes in data record.

    Returns:
        pd.DataFrame: lca_results with proper projects and scopes.
    """
    lca_full_results_logger.info(
        "Exclude projects not in internal data and scopes that are not in %s.", scope_type
    )
    prepped_wblca_output = wblca_output.loc[
        wblca_output["CLF Model ID"].isin(internal_data_for_area.index)
    ].loc[wblca_output["Cat_Ele_1"].isin(scope_type)]

    return prepped_wblca_output


def create_tool_specific_columns(
    original_wblca_output: pd.DataFrame, merged_wblca_output: pd.DataFrame
) -> pd.DataFrame:
    """Creates columns based on tally or oneclick tool usage.

    Args:
        original_wblca_output (pd.DataFrame): lca_results that contain "Cat_Mat_2" and "Cat_Ele_2"
        merged_wblca_output (pd.DataFrame): lca_results that have been
        processed by prep_internal_wblca_output

    Returns:
        pd.DataFrame: lca_results with tally and oneclick specific columns
    """
    # creates new columns based on Cat_Ele_2 and Cat_Mat_2
    lca_full_results_logger.info("Create tool specific columns based on Cat_Ele_2 and Cat_Mat_2.")
    output_w_new_cols = (
        merged_wblca_output.assign(tally_revit_building_element=original_wblca_output["Cat_Ele_2"])
        .assign(tally_material_group=original_wblca_output["Cat_Mat_2"])
        .assign(oneclick_omniclass=original_wblca_output["Cat_Ele_2"])
        .assign(oneclick_resource_type=original_wblca_output["Cat_Mat_2"])
    )

    # Creates NA values based on tool column in lca_results.
    lca_full_results_logger.info("Create NA values based on tool column in lca_results.")
    output_w_new_cols["tally_revit_building_element"] = output_w_new_cols[
        "tally_revit_building_element"
    ].mask(output_w_new_cols["Tool"] == "One Click LCA", "NA")
    output_w_new_cols["tally_material_group"] = output_w_new_cols["tally_material_group"].mask(
        output_w_new_cols["Tool"] == "One Click LCA", "NA"
    )
    output_w_new_cols["oneclick_omniclass"] = output_w_new_cols["oneclick_omniclass"].mask(
        output_w_new_cols["Tool"] == "TallyLCA", "NA"
    )
    output_w_new_cols["oneclick_resource_type"] = output_w_new_cols["oneclick_resource_type"].mask(
        output_w_new_cols["Tool"] == "TallyLCA", "NA"
    )
    lca_full_results_logger.info("Created tool specific columns.")

    return output_w_new_cols


def handle_nulls(output_w_new_cols: pd.DataFrame) -> pd.DataFrame:
    """Handles null situations in the dataset.

    Args:
        output_w_new_cols (pd.DataFrame): full lca results output.

    Returns:
        pd.DataFrame: full lca results output with nulls filled.
    """
    output_w_new_cols["Stored Biogenic Carbon"] = output_w_new_cols[
        "Stored Biogenic Carbon"
    ].fillna(0)

    output_w_new_cols["Cat_Mat_1"] = output_w_new_cols["Cat_Mat_1"].fillna("NULL")

    output_w_new_cols["tally_revit_building_element"] = output_w_new_cols[
        "tally_revit_building_element"
    ].fillna("NULL")

    output_w_new_cols["oneclick_resource_type"] = output_w_new_cols[
        "oneclick_resource_type"
    ].fillna("NULL")
    lca_full_results_logger.info(
        "Handed null situations for: Stored Biogenic Carbon, Cat_Mat_1,\
            tally_revit_building_element, oneclick_resource_type."
    )

    return output_w_new_cols


def create_mui(output_w_new_cols: pd.DataFrame) -> pd.DataFrame:
    """Creates material use intensity columns normalized by cfa and gfa.

    Args:
        output_w_new_cols (pd.DataFrame): lca_results with area columns included

    Returns:
        pd.DataFrame: lca_results with muis.
    """
    lca_full_results_logger.info("Begin creating mui normalized by gfa and cfa.")
    reno_projects = ["Minor Renovation", "Major Renovation", "Tenant Improvement"]
    # create muis
    output_w_new_cols["mui_gfa"] = (
        output_w_new_cols["Mass Total (kg)"] / output_w_new_cols["bldg_gfa"]
    )
    output_w_new_cols["mui_cfa"] = (
        output_w_new_cols["Mass Total (kg)"] / output_w_new_cols["bldg_cfa"]
    )

    # handle minor, major, and ti projects with different areas
    reno_mask = output_w_new_cols["bldg_proj_type"].isin(reno_projects)
    output_w_new_cols.loc[reno_mask, "mui_gfa"] = output_w_new_cols["Mass Total (kg)"].div(
        output_w_new_cols["bldg_added_gfa"].astype(float).fillna(0)
        + output_w_new_cols["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    output_w_new_cols.loc[reno_mask, "mui_cfa"] = output_w_new_cols["Mass Total (kg)"].div(
        output_w_new_cols["bldg_added_gfa"].astype(float).fillna(0)
        + output_w_new_cols["bldg_renovated_gfa"].astype(float).fillna(0)
    )
    lca_full_results_logger.info("Created mui normalized by gfa and cfa.")

    return output_w_new_cols


def write_full_lca_results_to_excel(
    final_output: pd.DataFrame, public_dataset_directory: Path
) -> None:
    """Writes full_lca_results to excel.
    Name of file is fixed to full_lca_results_{Date}.xlsx.

    Args:
        output_w_intensity_cols (pd.DataFrame): full_lca_results of data record
        public_dataset_directory (Path): Target path of full_lca_results.
    """

    date_suffix = datetime.today().strftime("%m-%d-%Y")
    with pd.ExcelWriter(
        public_dataset_directory.joinpath(f"full_lca_results_{date_suffix}.xlsx"),
        engine="xlsxwriter",
    ) as writer:

        final_output.to_excel(writer, sheet_name="lca_full_results", index=False)

        format_lca_full_results(writer=writer)
        lca_full_results_logger.info(
            "lca_full_results has beeen saved to %s", public_dataset_directory
        )
