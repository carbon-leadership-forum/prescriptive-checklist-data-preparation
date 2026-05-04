# pylint: disable=C0103, R0801, R0914, R0915
"""Complete process of harmonizing tally and one click files."""
from pathlib import Path
from logging import getLogger
import pandas as pd
import wblca_benchmark_v2_data_prep.utils.general as utils
from wblca_benchmark_v2_data_prep.utils.loggers import setup_logger


def complete():
    """ """
    # set file path locations
    current_file_path = Path(__file__)
    main_directory = current_file_path.parents[2]
    setup_logger(
        log_file_path=main_directory.joinpath("data/logs/lca_results/baseline_lca_results.log"),
        level="info",
    )

    main_complete_logger = getLogger("9_complete_script")
    main_complete_logger.info("Logger has been set up.")

    main_complete_logger.info("Begin configuration.")
    complete_write_path = main_directory.joinpath("data/lca_results/complete")
    data_record_write_path = main_directory.joinpath("data/data_record/raw")
    tally_baselined_path = main_directory.joinpath(
        "data/lca_results/baselined/tally_baselined.csv"
    )
    oneclick_baselined_path = main_directory.joinpath(
        "data/lca_results/baselined/oneclick_baselined.csv"
    )
    main_complete_logger.info("End configuration.")

    # read combined files
    main_complete_logger.info("Read combined lca_results files.")
    baselined_tally = utils.read_csv(tally_baselined_path)
    baselined_oneclick = utils.read_csv(oneclick_baselined_path)

    # combine the wblca output files
    main_complete_logger.info("Concatenate tally and oneclick files.")
    combined_raw_wblca_output = pd.concat([baselined_tally, baselined_oneclick], join="outer")

    # write to csv
    utils.write_to_csv(combined_raw_wblca_output, complete_write_path, "lca_results_completed")
    utils.write_to_csv(combined_raw_wblca_output, data_record_write_path, "lca_results_completed")


if __name__ == "__main__":
    complete()
