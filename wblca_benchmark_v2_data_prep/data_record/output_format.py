import pandas as pd


def format_internal_data(writer: pd.ExcelWriter) -> None:
    """Excel formatting for internal data.

    Args:
        writer (pd.ExcelWriter): Excel Writer from Pandas.
    """
    workbook = writer.book
    metadata = writer.sheets["project metadata"]

    zero_dec_format = workbook.add_format({"num_format": "#,##0"})
    one_dec_format = workbook.add_format({"num_format": "0.0"})
    two_dec_format = workbook.add_format({"num_format": "0.00"})
    three_dec_format = workbook.add_format({"num_format": "0.000"})

    # gfa_park_ratio, gfa_prim_percent, gfa_sec_percent
    metadata.set_column(14, 16, None, three_dec_format)
    # therm_env_area
    metadata.set_column(20, 20, None, zero_dec_format)
    # r_value_walls, r_value_roofs
    metadata.set_column(22, 23, None, one_dec_format)
    # col_grid_long, col_grid_short
    metadata.set_column(36, 37, None, one_dec_format)
    # ec_reduction_percent
    metadata.set_column(45, 45, None, two_dec_format)


def format_buildings_metadata(writer: pd.ExcelWriter) -> None:
    """Excel formatting for buildings_metadata.

    Args:
        writer (pd.ExcelWriter): Excel Writer from Pandas.
    """
    workbook = writer.book
    metadata = writer.sheets["project metadata"]

    zero_dec_format = workbook.add_format({"num_format": "#,##0"})
    one_dec_format = workbook.add_format({"num_format": "0.0"})
    two_dec_format = workbook.add_format({"num_format": "0.00"})
    three_dec_format = workbook.add_format({"num_format": "0.000"})
    five_dec_format = workbook.add_format({"num_format": "0.00000"})

    # bldg_CFA, bldg_GFA, bldg_park_GFA, bldg_added_GFA, bldg_renovated_GFA
    metadata.set_column(9, 11, None, one_dec_format)
    # bldg_occupants, bldg_res_units
    metadata.set_column(16, 17, None, zero_dec_format)
    # bldg_therm_env_area
    metadata.set_column(21, 21, None, zero_dec_format)
    # bldg_wwr
    metadata.set_column(22, 22, None, two_dec_format)
    # bldg_rval_walls, bldg_rval_roofs
    metadata.set_column(23, 24, None, one_dec_format)
    # str_wind_speed
    metadata.set_column(27, 27, None, zero_dec_format)
    # str_grid_long, str_grid_short
    metadata.set_column(34, 35, None, one_dec_format)
    # ec_reduction_percent
    metadata.set_column(45, 45, None, two_dec_format)
    # mass_total, stored_carbon total, gwp_a_to_c,
    # ep_a_to_c, ap_a_to_c, sfp_a_to_c
    metadata.set_column(46, 51, None, zero_dec_format)
    # odp_a_to_c
    metadata.set_column(52, 52, None, three_dec_format)
    # nred_a_to_c
    metadata.set_column(53, 53, None, zero_dec_format)
    # mui_gfa
    metadata.set_column(54, 54, None, two_dec_format)
    # eci_A_to_C_gfa
    metadata.set_column(55, 55, None, two_dec_format)
    # epi_A_to_C_gfa
    metadata.set_column(56, 56, None, five_dec_format)
    # api_A_to_C_gfa
    metadata.set_column(57, 57, None, three_dec_format)
    # sfpi_A_to_C_gfa
    metadata.set_column(58, 58, None, two_dec_format)
    # nredi_A_to_C_gfa
    metadata.set_column(60, 60, None, two_dec_format)
    # mui_cfa
    metadata.set_column(61, 61, None, two_dec_format)
    # eci_A_to_C_cfa
    metadata.set_column(62, 62, None, two_dec_format)
    # epi_A_to_C_cfa
    metadata.set_column(63, 63, None, five_dec_format)
    # api_A_to_C_cfa
    metadata.set_column(64, 64, None, three_dec_format)
    # sfpi_A_to_C_cfa
    metadata.set_column(65, 65, None, two_dec_format)
    # nredi_A_to_C_cfa
    metadata.set_column(67, 67, None, two_dec_format)
    # ec_per_occupant_A_to_C, ec_per_res_unit_A_to_C
    metadata.set_column(68, 69, None, zero_dec_format)


def format_lca_full_results(writer: pd.ExcelWriter) -> None:
    """Excel formatting for lca_full_results.

    Args:
        writer (pd.ExcelWriter): Excel Writer from Pandas.
    """
    workbook = writer.book
    lca_full_results = writer.sheets["lca_full_results"]

    # zero_dec_format = workbook.add_format({'num_format': '#,##0'})
    one_dec_format = workbook.add_format({"num_format": "0.0"})
    two_dec_format = workbook.add_format({"num_format": "0.00"})
    three_dec_format = workbook.add_format({"num_format": "0.000"})
    # five_dec_format = workbook.add_format({'num_format': '0.00000'})

    # inv_mass
    lca_full_results.set_column(11, 11, None, one_dec_format)
    # inv_stored_carbon
    lca_full_results.set_column(12, 12, None, one_dec_format)
    # gwp
    lca_full_results.set_column(13, 13, None, one_dec_format)
    # ep
    lca_full_results.set_column(14, 14, None, two_dec_format)
    # ap
    lca_full_results.set_column(15, 15, None, two_dec_format)
    # sfp
    lca_full_results.set_column(16, 16, None, three_dec_format)
    # nred
    lca_full_results.set_column(18, 18, None, one_dec_format)
    # mui_gfa
    lca_full_results.set_column(19, 19, None, three_dec_format)
    # mui_cfa
    lca_full_results.set_column(20, 20, None, three_dec_format)
