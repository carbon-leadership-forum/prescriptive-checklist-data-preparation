# pylint: disable=C0103, R0801, R0914, W0703, W1203
"""Finalize the combined data entry template."""
from pathlib import Path
from logging import getLogger
from wblca_benchmark_v2_data_prep.utils.loggers import setup_logger
import wblca_benchmark_v2_data_prep.metadata.general as utils
import wblca_benchmark_v2_data_prep.metadata.finalize as fi_utils


def finalize_det():
    """
    Adjust the combined data entry template.

    This function does the following:

    - Reads yaml files with key column information
    - Reads combined data entry templates
    - Removes and renames columns based on config file
    - Calculates new columns for analysis
    - Creates new bins for analysis
    - Runs through another set of removing and renaming columns
    - writes file to finalized directory
    """
    current_file_path = Path(__file__)
    main_directory = current_file_path.parents[2]
    config_path = main_directory.joinpath("references/config_metadata.yml")

    # instantiate logger
    setup_logger(
        log_file_path=main_directory.joinpath("data/logs/metadata/finalize_det.log"), level="info"
    )

    main_finalize_logger = getLogger("6_finalize_script")
    main_finalize_logger.info("Logger has been set up.")

    main_finalize_logger.info("Begin configuration.")
    config = utils.read_yaml(config_path)
    config_dict = config.get(current_file_path.stem)
    assert config_dict is not None, "The config dictionary could not be set"

    # set module level local variables from config
    read_data_directory_path = config_dict.get("read_data_directory_path")
    col_finalize_yaml = config_dict.get("col_finalize")
    write_data_directory = config_dict.get("write_data_directory")
    write_data_record_directory = config_dict.get("write_data_record_directory")
    file_suffix = config_dict.get("file_suffix")

    # set paths
    read_data_file_path = main_directory.joinpath(read_data_directory_path)
    col_finalize_path = main_directory.joinpath(col_finalize_yaml)
    write_data_directory_path = main_directory.joinpath(write_data_directory)
    write_data_record_path = main_directory.joinpath(write_data_record_directory)

    # read yaml
    col_finalize = utils.read_yaml(col_finalize_path)
    column_removal_list = col_finalize.get("column_removal")
    assert (
        column_removal_list is not None
    ), "The function was not able to read\
the column removal list"
    column_bin_list = col_finalize.get("columns_to_bin")
    assert column_bin_list is not None, "The list for column binning could not be set"
    column_rename_dict = col_finalize.get("column_renaming")
    assert column_rename_dict is not None, "The dict for column renaming could not be set"
    column_finalize_dict = col_finalize.get("column_finalizing")
    assert column_finalize_dict is not None, "The dict for column finalizing could not be set"
    main_finalize_logger.info("End configuration.")
    excluded_proj_list = col_finalize.get("excluded_projects")
    assert excluded_proj_list is not None, "The list for excluded projects could not be set"

    # read combined csv
    combined_det = utils.read_csv(read_data_file_path)
    combined_det.attrs = {"name": "Project_Data_Finalized"}

    # remove columns
    combined_det = combined_det.drop(columns=column_removal_list)
    main_finalize_logger.info("removed the following columns: \n%s", column_removal_list)

    # rename columns
    combined_det = combined_det.rename(columns=column_rename_dict)
    main_finalize_logger.info("renamed the following columns: \n%s", column_rename_dict)

    combined_det = fi_utils.calculate_new_columns(combined_det, col_finalize)

    combined_det = fi_utils.calculate_bins(
        combined_det,
    )

    # rename columns to lower case names with "_"
    combined_det = combined_det.rename(columns=column_finalize_dict)
    main_finalize_logger.info("renamed the following columns: \n%s", column_finalize_dict)

    combined_det = combined_det.drop(excluded_proj_list)

    # rename index
    combined_det = combined_det.rename_axis("clf_model_id").reset_index()

    # write to csv
    main_finalize_logger.info("Writing csv to finalized directory")
    utils.write_to_csv(combined_det, write_data_directory_path, file_suffix, "finalized")
    main_finalize_logger.info("Writing csv to data record directory")
    utils.write_to_csv(combined_det, write_data_record_path, file_suffix, "finalized")


if __name__ == "__main__":
    finalize_det()
