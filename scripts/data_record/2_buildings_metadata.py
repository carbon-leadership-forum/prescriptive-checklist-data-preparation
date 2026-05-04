# pylint: disable=C0103
"""Create buildings metadata."""

from pathlib import Path
from logging import getLogger
import pandas as pd
import wblca_benchmark_v2_data_prep.utils.general as gen
import wblca_benchmark_v2_data_prep.data_record.metadata_calcs as calc
from wblca_benchmark_v2_data_prep.utils.loggers import setup_logger


def create_buildings_metadata():
    """
    Writes a buildings metadata file from raw Data Entry Template and WBLCA output.

    This script does the following:

    - Reads data entry templates and harmonized lca results.
    - Excludes module D and scopes outside of str, enc, int from all analyses.
    - Creates total impacts for all impact categories.
    - Rounds building areas.
    - Creates intensities for all impact categories and properly renames all impacts.
    - Creates null and NA values across the data record based on conditional rules.
    - Writes data to public directory.
    """
    main_directory = Path(__file__).parents[2]
    wblca_output_path = main_directory.joinpath("data/data_record/raw/lca_results_completed.csv")
    internal_data_path = main_directory.joinpath("data/data_record/internal/internal_data.xlsx")
    config_path = main_directory.joinpath("references/config_data_record.yml")
    public_dataset_directory = main_directory.joinpath("data/data_record/public")

    wblca_output = gen.read_csv(wblca_output_path)
    internal_data = pd.read_excel(internal_data_path, index_col=False).set_index("project_index")

    # instantiate logger
    setup_logger(
        log_file_path=main_directory.joinpath("data/logs/data_record/buildings_metadata.log"),
        level="info",
    )

    buildings_metadata_logger = getLogger("2_buildings_metadata_script")
    buildings_metadata_logger.info("Logger has been set up.")

    buildings_metadata_logger.info("Begin configuration.")
    config = gen.read_yaml(config_path)
    assert config is not None, "The config dictionary could not be set"

    impact_type_list = config.get("impact_type")
    assert impact_type_list is not None, "The list for impact types could not be set"

    scope_type = config.get("scope_type")
    assert scope_type is not None, "The list for scope types could not be set"

    impact_renaming = config.get("buildings_metadata_impact_renaming")
    assert impact_renaming is not None, "The dict for impact renaming could not be set"
    buildings_metadata_logger.info("End configuration.")

    # remove module d and site, mep and ffe scopes
    buildings_metadata_logger.info("Exclude Module D and scopes that are not in %s.", scope_type)
    excluding_d_wblca_output = wblca_output.loc[
        wblca_output["Life Cycle Stage"].str.contains("A|B|C")
    ].loc[wblca_output["Cat_Ele_1"].isin(scope_type)]

    buildings_metadata_logger.info("Begin buildings_metadata creation.")
    project_metadata = calc.create_total_impact_columns(
        excluding_d_wblca_output=excluding_d_wblca_output,
        impact_type_list=impact_type_list,
        internal_data=internal_data,
    )

    project_metadata = calc.round_bldg_areas(project_metadata=project_metadata)

    project_metadata = calc.create_intensity_columns(project_metadata=project_metadata)

    # reindex based on internal data
    buildings_metadata_logger.info("Reindex buildings_metadata based on internal data.")
    project_metadata = (
        project_metadata.merge(
            internal_data.reset_index()[["project_index", "clf_model_id"]],
            right_on="clf_model_id",
            left_on="clf_model_id",
        )
        .set_index("project_index")
        .sort_index()
    )

    buildings_metadata_logger.info("Delete clf id columns")
    project_metadata = project_metadata.drop(
        columns=[
            "clf_proj_id",
            "clf_model_id",
            "clf_firm_id",
        ]
    )

    # rename impact columns
    buildings_metadata_logger.info("Rename columns based on impact_renaming.")
    project_metadata = project_metadata.rename(columns=impact_renaming)

    project_metadata = calc.null_override_project_metadata(project_metadata)

    calc.write_buildings_metadata_to_excel(
        project_metadata=project_metadata,
        public_dataset_directory=public_dataset_directory,
    )
    buildings_metadata_logger.info("Buildings_metadata created.")


if __name__ == "__main__":
    create_buildings_metadata()
