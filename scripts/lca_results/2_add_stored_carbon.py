# pylint: disable=C0103
"""Adds stored carbon to Tally models."""
from pathlib import Path
from logging import getLogger
import pandas as pd
from wblca_benchmark_v2_data_prep.utils.loggers import setup_logger
import wblca_benchmark_v2_data_prep.utils.general as gen


def add_stored_carbon():
    """
    Adds stored carbon to projects with biogenic carbon.

    This script does the following:

    - Reads tally files in cleaned directory
    - Reads stored carbon database
    - Merges database with tally file
    - Creates new Stored Biogenic Carbon column
    - Updates each A1-A3 value in Stored Biogenic Carbon column with mass * stored carbon factor
    - Writes file to csc directory
    """
    current_file_path = Path(__file__)
    main_directory = current_file_path.parents[2]
    cleaned_tally_directory = main_directory.joinpath("data/lca_results/ex_bio")
    csc_tally_directory = main_directory.joinpath("data/lca_results/csc")
    stored_bio_database_path = main_directory.joinpath("references/stored_carbon_database.xlsx")
    # instantiate logger
    setup_logger(
        log_file_path=main_directory.joinpath("data/logs/lca_results/csc_lca_results_tally.log"),
        level="info",
    )

    csc_logger = getLogger("2_add_stored_carbon_script")
    csc_logger.info("Logger has been set up.")

    csc_logger.info("Read stored carbon database.")
    full_stored_bio_database = pd.read_excel(stored_bio_database_path, sheet_name="csc")
    stored_bio_data_short = full_stored_bio_database[
        ["Name_Tally Material", "Stored Carbon (C02eq/kg)"]
    ]

    for tally_file in cleaned_tally_directory.glob("*.csv"):
        csc_logger.info("Begin adding stored carbon to %s", tally_file.name)
        tally_df = gen.read_csv(tally_file)

        csc_logger.info("Merge stored carbon database based on material name.")
        merged_tally_df = tally_df.merge(
            right=stored_bio_data_short,
            left_on="Material Name",
            right_on="Name_Tally Material",
            how="left",
        )

        merged_tally_df["Stored Biogenic Carbon"] = 0.0

        csc_logger.info("Calculate stored carbon for materials in A1-A3 stage")
        merged_tally_df.loc[
            (merged_tally_df["Life Cycle Stage"] == "[A1-A3] Product")
            | (merged_tally_df["Life Cycle Stage"] == "Product"),
            "Stored Biogenic Carbon",
        ] = (
            merged_tally_df["Mass Total (kg)"] * merged_tally_df["Stored Carbon (C02eq/kg)"]
        )

        gen.write_to_csv(merged_tally_df, csc_tally_directory, f"{tally_file.stem}_csc")
        csc_logger.info("Added stored carbon to %s", tally_file.name)


if __name__ == "__main__":

    add_stored_carbon()
