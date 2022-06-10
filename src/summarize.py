# -*- coding: utf-8 -*-
import fiona
import geopandas as gpd
import pandas as pd
from pathlib import Path
import data_config as data


# FUNCTIONS

def overlay_geoms(agg_gdf, summ_gdf,):
    """
    union zcta with zones
    calculate area for all polygons
    agg_gdf: zcta polygons
    summ_gdf: zones with data for summarization
    @return:
    """
    agg_gdf["agg_area"] = agg_gdf.geometry.area
    summ_gdf["summ_area"] = summ_gdf.geometry.area
    intersection = gpd.overlay(df1=agg_gdf, df2=summ_gdf, how="intersection")
    intersection["int_area"] = intersection.geometry.area
    intersection["agg_ar_pct"] = intersection.int_area / intersection.agg_area
    intersection["summ_ar_pct"] = intersection.int_area / intersection.summ_area
    return intersection


def _check_fields(fields_list):
    """
    check if fields are tuples
    """
    for field in fields_list:
        if isinstance(field, tuple):
            return True


def flatten_fields(fields_list):
    """
    flatten list of fields
    @param fields_list:
    @return:
    """
    if _check_fields(fields_list):
        fields = [item for tup in fields_list for item in tup]
    else:
        fields = fields_list
    return fields


ZIP_CODES = gpd.read_file(data.ZCTA_SHP)
ZIP_CODES = ZIP_CODES[["ZCTA5CE10", "GEOID10", "geometry"]]
TAZ = gpd.read_file(data.SERPM8_SHP)
TAZ = TAZ[["TAZ_REG", "geometry"]]
GTFS_BLOCKS = gpd.read_file(data.GTFS_ZONES, layer="block_results_v4")
GTFS_BLOCKS = GTFS_BLOCKS[["GEOID10", "m1_weekday", "m5", "geometry"]]
FLSWM = gpd.read_file(data.FLSWM_SHP)
FLSWM = FLSWM[["NEWTAZ", "geometry"]]

SUMMARY_CONFIG = data.SUMMARY_DICT

crs = FLSWM.crs
zips = ZIP_CODES.to_crs(crs)
tazs = TAZ.to_crs(crs)
gtfs_blocks = GTFS_BLOCKS.to_crs(crs)
flswm_gdf = FLSWM.to_crs(crs)

# procedural code
for summary, conf in SUMMARY_CONFIG.items():
    zones = gpd.read_file(conf["zones"])
    zone_on = conf["zone_on"]
    table_dict = conf["tables"]
    table_on = conf["table_on"]
    fields = conf["fields"]
    calc = conf["calc"]
    for join_type, tables in table_dict.items():
        if join_type == "loop" and tables is not None:
            for table in tables:
                df = pd.read_csv(table, usecols=flatten_fields(fields))
                # join table to zones
                join_gdf = zones.merge(right=table, left_on=zone_on, right_on=table_on)
                # overly and calculate area overlaps
                overlay = overlay_geoms(agg_gdf=zips, summ_gdf=join_gdf)
                # reallocate fields based on area overlap
                overlay[fields].multiply(overlay["summ_ar_pct"], axis="index")
                # if fields is a tuple, this implies a calculation
                if _check_fields(fields):
                    for field in fields:
                        overlay[]
        # manage double joins (e.g. msp and trips tables)
        else:
            join_gdf = zones
            for tbls in tables:
                for tbl in tbls:
                    df = pd.read_csv(tbl, usecols=flatten_fields(fields))
                    # perform join
                    join_gdf = join_gdf.merge(
                        right=table, left_on=zone_on, right_on=table_on
                    )
                # overly and calculate area overlaps
                overlay = overlay_geoms(agg_gdf=zips, summ_gdf=join_gdf)
