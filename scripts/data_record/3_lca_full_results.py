# pylint: disable=C0103
"""Create lca results"""

from pathlib import Path
from logging import getLogger
import pandas as pd
import wblca_benchmark_v2_data_prep.utils.general as gen
import wblca_benchmark_v2_data_prep.data_record.results_calcs as calc
import wblca_benchmark_v2_data_prep.data_record.metadata_calcs as meta
from wblca_benchmark_v2_data_prep.utils.loggers import setup_logger


def create_lca_full_results():
    """
    Writes a full lca results file from raw Data Entry Template and WBLCA output.

    This script does the following:

    - Reads internal data generated earlier and harmonized lca results.
    - Selects the internal data areas for analysis.
    - Excludes module D and scopes outside of str, enc, int from all analyses.
    - Merges the lca output with the internal data areas.
    - Creates tool specific columns and adds NA where appropriate.
    - Rounds the building areas and creates mui values
    - Renames columns and sorts based on:
        'project_index', 'omniclass_element', 'life_cycle_stage', 'service_life'
    - Writes final result to public directory.
    """
    main_directory = Path(__file__).parents[2]
    wblca_output_path = main_directory.joinpath("data/data_record/raw/lca_results_completed.csv")
    internal_data_path = main_directory.joinpath("data/data_record/internal/internal_data.xlsx")
    config_path = main_directory.joinpath("references/config_data_record.yml")
    public_dataset_directory = main_directory.joinpath("data/data_record/public")

    # instantiate logger
    setup_logger(
        log_file_path=main_directory.joinpath("data/logs/data_record/lca_full_results.log"),
        level="info",
    )

    lca_full_results_logger = getLogger("3_lca_full_results_script")
    lca_full_results_logger.info("Logger has been set up.")

    lca_full_results_logger.info("Begin configuration.")
    wblca_output = gen.read_csv(wblca_output_path)
    internal_data = pd.read_excel(internal_data_path, index_col=False)

    config = gen.read_yaml(config_path)
    assert config is not None, "The config dictionary could not be set"

    full_results_column_renaming = config.get("full_results_column_renaming")
    assert full_results_column_renaming is not None, "The list for col renaming could not be set"

    full_results_col_list = config.get("full_results_column_list")
    assert full_results_col_list is not None, "The list for cols in full results could not be set"

    scope_type = config.get("scope_type")
    assert scope_type is not None, "The list for scope types could not be set"

    full_results_column_renaming = config.get("full_results_column_renaming")
    assert full_results_column_renaming is not None, "The dict of col renaming could not be set"
    lca_full_results_logger.info("End configuration.")

    lca_full_results_logger.info("Begin lca_full_results creation.")
    internal_data_for_area = calc.prep_internal_data_for_area_calcs(internal_data)
    prepped_wblca_output = calc.prep_internal_wblca_output(
        internal_data_for_area=internal_data_for_area,
        wblca_output=wblca_output,
        scope_type=scope_type,
    )

    lca_full_results_logger.info("Merge lca_results with internal data for areas.")
    merged_wblca_output = prepped_wblca_output.merge(
        internal_data_for_area, left_on="CLF Model ID", right_index=True
    )

    output_w_new_cols = calc.create_tool_specific_columns(
        original_wblca_output=wblca_output, merged_wblca_output=merged_wblca_output
    )

    output_w_new_cols = meta.round_bldg_areas(project_metadata=output_w_new_cols)

    output_w_new_cols = calc.handle_nulls(output_w_new_cols=output_w_new_cols)

    output_w_mui = calc.create_mui(output_w_new_cols=output_w_new_cols)

    lca_full_results_logger.info("Rename columns based on full_results_column_renaming.")
    final_output = output_w_mui.rename(columns=full_results_column_renaming)[full_results_col_list]

    lca_full_results_logger.info(
        "Sort values based on: project_index, omniclass_element, life_cycle_stage,\
        service_life."
    )
    final_output = final_output.sort_values(
        ["project_index", "omniclass_element", "life_cycle_stage", "service_life"],
        ascending=[True, False, True, True],
    )

    calc.write_full_lca_results_to_excel(
        final_output=final_output,
        public_dataset_directory=public_dataset_directory,
    )
    lca_full_results_logger.info("Lca_full_results created.")


if __name__ == "__main__":
    create_lca_full_results()
