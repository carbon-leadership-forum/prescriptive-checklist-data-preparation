from pathlib import Path
import pandas as pd
from wblca_benchmark_v2_data_prep.utils.loggers import setup_logger
from logging import getLogger


def exclude_biogenic_carbon():

    current_file_path = Path(__file__)
    main_directory = current_file_path.parents[2]
    export_path = main_directory.joinpath("data/lca_results/ex_bio")
    exBio_TallyGabi_path = main_directory.joinpath("references/expanded_TallyGaBi_biogenic.xlsx")

    # instantiate logger
    setup_logger(
        log_file_path=main_directory.joinpath(
            "data/logs/lca_results/ex_bio_lca_results_tally.log"
        ),
        level="info",
    )

    exbio_logger = getLogger("2_add_stored_carbon_script")
    exbio_logger.info("Logger has been set up.")

    exbio_logger.info("Read excluding biogenic carbon values.")
    df_exBio_TallyGabi = pd.read_excel(exBio_TallyGabi_path, sheet_name="ex_bio")
    df_exBio_TallyGabi = df_exBio_TallyGabi.set_index("name")
    gwe_mfg = df_exBio_TallyGabi["gwe_mfg"]
    gwe_eol = df_exBio_TallyGabi["gwe_eol"]

    cleaned_tally_path = main_directory.joinpath("data/lca_results/cleaned/tally")

    exbio_logger.info("Create list of tally files.")
    tally_csv_files = [file for file in cleaned_tally_path.glob("*.csv")]

    ## inconsistent material name tuple
    INCONSISTENT_MATERIAL_NAMES = (
        "Lightweight concrete, 2501-3000 psi, 0-19% fly ash and/or slag",
        "Lightweight concrete, 2501-3000 psi, 20-29% fly ash",
        "Lightweight concrete, 3001-4000 psi, 0-19% fly ash and/or slag",
        "Lightweight concrete, 3001-4000 psi, 20-29% fly ash",
        "Lightweight concrete, 4001-5000 psi, 0-19% fly ash and/or slag",
        "Lightweight concrete, 4001-5000 psi, 20-29% fly ash",
        "Lightweight concrete; 2501-3000 psi; 0-19% fly ash and/or slag",
        "Lightweight concrete; 4001-5000 psi; 0-19% fly ash and/or slag",
        "Lightweight concrete; 4001-5000 psi; 20-29% fly ash",
        "Polyamide, nylon 6.6",
        "Polystyrene board (XPS), Pentane foaming agent",
        "Polystyrene board (XPS); Pentane foaming agent",
        "Structural concrete, 0-2500 psi, 20-29% fly ash",
        "Structural concrete, 0-2500 psi, 30-39% fly ash",
        "Structural concrete, 0-2500 psi, 30-39% slag",
        "Structural concrete, 0-2500 psi, 30-39% slag",
        "Structural concrete, 2501-3000 psi, >20% fly ash and >30% slag",
        "Structural concrete, 2501-3000 psi, 0-19% fly ash and/or slag",
        "Structural concrete, 2501-3000 psi, 20-29% fly ash",
        "Structural concrete, 2501-3000 psi, 30-39% fly ash",
        "Structural concrete, 3001-4000 psi, >20% fly ash and >30% slag",
        "Structural concrete, 3001-4000 psi, >50% slag",
        "Structural concrete, 3001-4000 psi, 0-19% fly ash and/or slag",
        "Structural concrete, 3001-4000 psi, 20-29% fly ash",
        "Structural concrete, 3001-4000 psi, 30-39% fly ash",
        "Structural concrete, 3001-4000 psi, 30-39% slag",
        "Structural concrete, 3001-4000 psi, 40-49% fly ash",
        "Structural concrete, 3001-4000 psi, 40-49% slag",
        "Structural concrete, 4001-5000 psi, >20% fly ash and >30% slag",
        "Structural concrete, 4001-5000 psi, 0-19% fly ash and/or slag",
        "Structural concrete, 4001-5000 psi, 20-29% fly ash",
        "Structural concrete, 4001-5000 psi, 30-39% fly ash",
        "Structural concrete, 4001-5000 psi, 30-39% slag",
        "Structural concrete, 4001-5000 psi, 40-49% fly ash",
        "Structural concrete, 4001-5000 psi, 40-49% slag",
        "Structural concrete, 5001-6000 psi, 0-19% fly ash and/or slag",
        "Structural concrete, 5001-6000 psi, 20-29% fly ash",
        "Structural concrete, 5001-6000 psi, 30-39% fly ash",
        "Structural concrete, 6001-8000 psi, 0-19% fly ash and/or slag",
        "Structural concrete, 6001-8000 psi, 20-29% fly ash",
        "Structural concrete, 6001-8000 psi, 40-49% fly ash",
        "Structural concrete; 2501-3000 psi; 0-19% fly ash and/or slag",
        "Structural concrete; 3001-4000 psi; 0-19% fly ash and/or slag",
        "Structural concrete; 4001-5000 psi; 0-19% fly ash and/or slag",
        "Structural concrete; 4001-5000 psi; 20-29% fly ash",
    )
    for current_tally_file in tally_csv_files:

        tally_file_stem = current_tally_file.stem
        exbio_logger.info(f"Begin excluding biogenic carbon from {tally_file_stem}.")
        tally_file_df = pd.read_csv(current_tally_file).reset_index(names="original_index")

        exbio_logger.info("Create life cycle stage specific dataframes")
        tally_file_df_a1_a3 = tally_file_df.iloc[::5].reset_index(drop=True)
        tally_file_df_a1_a3.index = "element_" + tally_file_df_a1_a3.index.astype(str)
        tally_file_df_a4 = tally_file_df.iloc[1::5].reset_index(drop=True)
        tally_file_df_a4.index = "element_" + tally_file_df_a4.index.astype(str)
        tally_file_df_b2_b5 = tally_file_df.iloc[2::5].reset_index(drop=True)
        tally_file_df_b2_b5.index = "element_" + tally_file_df_b2_b5.index.astype(str)
        tally_file_df_c2_c4 = tally_file_df.iloc[3::5].reset_index(drop=True)
        tally_file_df_c2_c4.index = "element_" + tally_file_df_c2_c4.index.astype(str)
        tally_file_df_d = tally_file_df.iloc[4::5].reset_index(drop=True)
        tally_file_df_d.index = "element_" + tally_file_df_d.index.astype(str)

        tally_file_df_a1_a3_ex_bio = tally_file_df_a1_a3.copy()
        tally_file_df_b2_b5_ex_bio = tally_file_df_b2_b5.copy()
        tally_file_df_c2_c4_ex_bio = tally_file_df_c2_c4.copy()
        tally_file_df_a1_a3_ex_bio_for_replacement_impacts = tally_file_df_a1_a3.copy()
        tally_file_df_a4_ex_bio_for_replacement_impacts = tally_file_df_a4.copy()
        tally_file_df_c2_c4_ex_bio_for_replacement_impacts = tally_file_df_c2_c4.copy()

        exbio_logger.info("Exclude biogenic carbon from A1-A3")
        tally_file_df_a1_a3_ex_bio["Global Warming Potential Total (kgCO2eq)"] = (
            tally_file_df_a1_a3_ex_bio["Material Name"].map(df_exBio_TallyGabi["gwe_mfg"])
            * tally_file_df_a1_a3_ex_bio["Mass Total (kg)"]
        )
        # cover inconsistent material name case, make A1-A3 same as in original model
        tally_file_df_a1_a3_ex_bio.loc[
            tally_file_df_a1_a3_ex_bio["Material Name"].isin(INCONSISTENT_MATERIAL_NAMES),
            "Global Warming Potential Total (kgCO2eq)",
        ] = tally_file_df_a1_a3["Global Warming Potential Total (kgCO2eq)"]

        exbio_logger.info("Exclude biogenic carbon from C2-C4")
        tally_file_df_c2_c4_ex_bio["Global Warming Potential Total (kgCO2eq)"] = (
            tally_file_df_c2_c4_ex_bio["Material Name"].map(df_exBio_TallyGabi["gwe_eol"])
            * tally_file_df_a1_a3_ex_bio["Mass Total (kg)"]
        )
        # cover inconsistent material name case, make C2-C4 same as in original model
        tally_file_df_c2_c4_ex_bio.loc[
            tally_file_df_c2_c4_ex_bio["Material Name"].isin(INCONSISTENT_MATERIAL_NAMES),
            "Global Warming Potential Total (kgCO2eq)",
        ] = tally_file_df_c2_c4["Global Warming Potential Total (kgCO2eq)"]

        exbio_logger.info("Exclude biogenic carbon from B2-B5")
        tally_file_df_a1_a3_ex_bio_for_replacement_impacts[
            "Global Warming Potential Total (kgCO2eq)"
        ] = (
            tally_file_df_a1_a3_ex_bio_for_replacement_impacts["Material Name"].map(gwe_mfg)
            * tally_file_df_b2_b5_ex_bio["Mass Total (kg)"]
        )
        tally_file_df_a4_ex_bio_for_replacement_impacts[
            "Global Warming Potential Total (kgCO2eq)"
        ] = (
            tally_file_df_a4_ex_bio_for_replacement_impacts[
                "Global Warming Potential Total (kgCO2eq)"
            ]
            * tally_file_df_b2_b5_ex_bio["Mass Total (kg)"]
            / tally_file_df_a1_a3_ex_bio_for_replacement_impacts["Mass Total (kg)"]
        )
        tally_file_df_c2_c4_ex_bio_for_replacement_impacts[
            "Global Warming Potential Total (kgCO2eq)"
        ] = (
            tally_file_df_c2_c4_ex_bio_for_replacement_impacts["Material Name"].map(gwe_eol)
            * tally_file_df_b2_b5_ex_bio["Mass Total (kg)"]
        )
        tally_file_df_b2_b5_ex_bio["Global Warming Potential Total (kgCO2eq)"] = (
            tally_file_df_a1_a3_ex_bio_for_replacement_impacts[
                "Global Warming Potential Total (kgCO2eq)"
            ]
            + tally_file_df_a4_ex_bio_for_replacement_impacts[
                "Global Warming Potential Total (kgCO2eq)"
            ]
            + tally_file_df_c2_c4_ex_bio_for_replacement_impacts[
                "Global Warming Potential Total (kgCO2eq)"
            ]
        )
        # cover inconsistent material name case, make B2-B5 same as in original model
        tally_file_df_b2_b5_ex_bio.loc[
            tally_file_df_b2_b5_ex_bio["Material Name"].isin(INCONSISTENT_MATERIAL_NAMES),
            "Global Warming Potential Total (kgCO2eq)",
        ] = tally_file_df_b2_b5["Global Warming Potential Total (kgCO2eq)"]

        (
            pd.concat(
                [
                    tally_file_df_a1_a3_ex_bio,
                    tally_file_df_a4,
                    tally_file_df_b2_b5_ex_bio,
                    tally_file_df_c2_c4_ex_bio,
                    tally_file_df_d,
                ]
            )
            .set_index("original_index")
            .sort_index()
            .to_csv(export_path.joinpath(f"{tally_file_stem}_ex_bio.csv"), index=False)
        )
        exbio_logger.info(f"Finish excluding biogenic carbon from {tally_file_stem}.")


if __name__ == "__main__":
    exclude_biogenic_carbon()
