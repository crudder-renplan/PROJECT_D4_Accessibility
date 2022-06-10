"""
Configuration file to handle all the data path setting and various combinations of tables needed for
summarization work.
"""
from pathlib import Path

data_dir = (
    r"D:\OneDrive_RP\Renaissance Planning Group\District 4 - Accessibillity_KDRIVE"
)

# TAZ data geometry
TAZS = Path(data_dir, "TAZs")
SERPM8_SHP = Path(TAZS, "SERPM8TAZ.shp")
FLSWM_SHP = Path(TAZS, "2015_TAZs_Final.shp")

# Zip Code Geometry
ZIPS = Path(data_dir, "ZIPS")
ZCTA_SHP = Path(ZIPS, "tl_2020_us_zcta510_FL.shp")

# gtfs summaries
GTFS = Path(data_dir, "gtfs")
GTFS_ZONES = Path(GTFS, "gtfs_feeds", "summarized_results", "results_fixed.gdb")

# tables
ACCESS_DIR = Path(data_dir, "access_scores")
TRIPS_DIR = Path(data_dir, "trip_tables")

SUMMARY_DICT = {
    "serpm_jhb": {
        "zones": SERPM8_SHP,
        "tables": [
            Path(ACCESS_DIR, "SERPM_FF_15_TTD_Un_15_30_60.csv"),
            Path(ACCESS_DIR, "SERPM_FF_45_TTD_Un_15_30_60.csv"),
        ],
        "zone_on": "TAZ_REG",
        "table_on": "index",
        "fields": [
            "EMP_Max_15_Min_CG",
            "EMP_Max_15_Min_FF",
            "EMP_Max_30_Min_CG",
            "EMP_Max_30_Min_FF",
            "EMP_Max_60_Min_CG",
            "EMP_Max_60_Min_FF",
        ],
        "calc": "divide",
    },
    "flswm_jhb": {
        "zones": FLSWM_SHP,
        "tables": [
            Path(ACCESS_DIR, "FLSWM_FF_18_TTD_Un_15_30_60.csv"),
            Path(ACCESS_DIR, "FLSWM_FF_45_TTD_Un_15_30_60.csv"),
        ],
        "zone_on": "NEWTAZ",
        "table_on": "index",
        "fields": [
            ("EMP_Max_15_Min_CG", "DU_Max_15_Min_CG"),
            ("EMP_Max_15_Min_FF", "DU_Max_15_Min_FF"),
            ("EMP_Max_30_Min_CG", "DU_Max_30_Min_CG"),
            ("EMP_Max_30_Min_FF", "DU_Max_30_Min_FF"),
            ("EMP_Max_60_Min_CG", "DU_Max_60_Min_CG"),
            ("EMP_Max_60_Min_FF", "DU_Max_60_Min_FF"),
        ],
        "calc": "divide",
    },
    "serpm_cumm_opps_dec": {
        "zones": SERPM8_SHP,
        "tables": [
            Path(ACCESS_DIR, "SERPM_FF_15_TTD_15_30_60.csv"),
            Path(ACCESS_DIR, "SERPM_FF_45_TTD_15_30_60.csv"),
        ],
        "zone_on": "TAZ_REG",
        "table_on": "index",
        "fields": [
            "EMP_Max_15_Min_CG",
            "EMP_Max_15_Min_FF",
            "EMP_Max_30_Min_CG",
            "EMP_Max_30_Min_FF",
            "EMP_Max_60_Min_CG",
            "EMP_Max_60_Min_FF",
        ],
        "calc": None,
    },
    "serpm_cumm_opps_un": {
        "zones": SERPM8_SHP,
        "tables": [
            Path(ACCESS_DIR, "SERPM_FF_15_TTT_15_30_60.csv"),
            Path(ACCESS_DIR, "SERPM_FF_45_TTT_15_30_60.csv"),
        ],
        "zone_on": "TAZ_REG",
        "table_on": "index",
        "fields": [
            "EMP_Max_15_Min_CG",
            "EMP_Max_15_Min_FF",
            "EMP_Max_30_Min_CG",
            "EMP_Max_30_Min_FF",
            "EMP_Max_60_Min_CG",
            "EMP_Max_60_Min_FF",
        ],
        "calc": None,
    },
    "flswm_cumm_opps_dec": {
        "zones": FLSWM_SHP,
        "tables": [
            Path(ACCESS_DIR, "FLSWM_FF_15_TTD_15_30_60.csv"),
            Path(ACCESS_DIR, "FLSWM_FF_45_TTD_15_30_60.csv"),
        ],
        "zone_on": "NEWTAZ",
        "table_on": "index",
        "fields": [
            "EMP_Max_15_Min_CG",
            "EMP_Max_15_Min_FF",
            "EMP_Max_30_Min_CG",
            "EMP_Max_30_Min_FF",
            "EMP_Max_60_Min_CG",
            "EMP_Max_60_Min_FF",
        ],
        "calc": None,
    },
    "flswm_cumm_opps_un": {
        "zones": FLSWM_SHP,
        "tables": {
            "loop": (
                Path(ACCESS_DIR, "FLSWM_FF_15_TTT_15_30_60.csv"),
                Path(ACCESS_DIR, "FLSWM_FF_45_TTT_15_30_60.csv"),
            ),
            "join": None,
        },
        "zone_on": "NEWTAZ",
        "table_on": "index",
        "fields": [
            "EMP_Max_15_Min_CG",
            "EMP_Max_15_Min_FF",
            "EMP_Max_30_Min_CG",
            "EMP_Max_30_Min_FF",
            "EMP_Max_60_Min_CG",
            "EMP_Max_60_Min_FF",
        ],
        "calc": None,
    },
    "serpm_msp": {
        "zones": SERPM8_SHP,
        "tables": [
            (
                Path(TRIPS_DIR, "SERPM_MSP_CG_15.csv"),
                Path(TRIPS_DIR, "SERPM_Trips_CG.csv"),
            ),  # msp, trip
            (
                Path(TRIPS_DIR, "SERPM_MSP_FF_15.csv"),
                Path(TRIPS_DIR, "SERPM_Trips_FF.csv"),
            ),
        ],
        "zone_on": "TAZ_REG",
        "table_on": "TAZ",
        "fields": [("From_MSP", "To_Trips")],
        "calc": "divide",
    },
    "flswm_msp": {
        "zones": FLSWM_SHP,
        "tables": [
            Path(TRIPS_DIR, "FLWSM_Trips_CG_18.csv"),
            Path(TRIPS_DIR, "FLWSM_Trips_FF_18.csv"),
        ],
        "zone_on": "NEWTAZ",
        "table_on": "TAZ",
        "fields": [("From_MSP", "To_Trips")],
        "calc": "divide",
    },
    "transit_prox": {
        "zones": GTFS_ZONES,
        "zone_on": None,
        "table_on": None,
        "tables": None,
        "fields": ["m1_weekday", "m5"],
        "calc": None,
    },
}
