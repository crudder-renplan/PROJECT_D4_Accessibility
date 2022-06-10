import os
import re
import importlib.util
import string
import random
from pathlib import Path, PurePath
import shutil
from functools import reduce
from typing import Union
import appdirs
import yaml

import fiona
import pandas as pd

# from dotenv import find_dotenv, load_dotenv   #TODO: determine the need for this
# # load the .env into the namespace
# load_dotenv(find_dotenv())    #TODO: determine the need for this

# check for arcgis to accommodate projects not needing arcgis
if importlib.util.find_spec("arcgis") is not None:
    from arcgis.gis import GIS, Group
    from arcgis.env import active_gis
    has_arcgis = True
else:
    has_arcgis = False
    GIS = None
    Group = None

# see if arcpy available to accommodate non-windows environments
if importlib.util.find_spec('arcpy') is not None:
    import arcpy
    has_arcpy = True
else:
    has_arcpy = False


def _not_none_and_len(string: str) -> bool:
    """helper to figure out if not none and string is populated"""
    is_str = isinstance(string, str)
    has_len = False if re.match(r'\S{5,}', '') is None else True
    status = True if has_len and is_str else False
    return status


def get_gis():
    """Try to get a GIS object first from an active_gis and then trying to create from the .env file."""
    # if there is an active_gis, just use it
    if isinstance(active_gis, GIS):
        gis = active_gis

    # if not an active_gis, see what may be available in the .env file
    else:
        url = os.getenv('ESRI_GIS_URL')
        usr = os.getenv('ESRI_GIS_USERNAME')
        pswd = os.getenv('ESRI_GIS_PASSWORD')

        # if credentials are found, use them to create a gis (url is not needed since defaults to AGOL)
        if url is not None and usr is not None and pswd is not None:
            gis = GIS(url, username=usr, password=pswd)
        elif usr is not None and pswd is not None:
            gis = GIS(username=usr, password=pswd)
        else:
            gis = None

    return gis


def add_group(gis: GIS = None, group_name: str = None) -> Group:
    """
    Add a group to the GIS for the project for saving resources.
    Args:
        gis: Optional
            arcgis.gis.GIS object instance.
        group_name: Optional
            Group to be added to the cloud GIS for storing project resources. Default
            is to load from the .env file. If a group name is not provided, and one is
            not located in the .env file, an exception will be raised.

    Returns: Group
    """
    if not has_arcgis:
        raise ImportError(
            "attempting to use 'arcgis' python api, but package is not installed"
        )
    else:
        # if no group name provided
        if group_name is None:
            # load the group name
            group_name = os.getenv('ESRI_GIS_GROUP')

            err_msg = 'A group name must either be defined in the .env file or explicitly provided.'
            assert isinstance(group_name, str), err_msg
            assert len(group_name), err_msg

        # create an instance of the group manager
        gmgr = gis.groups

        # determine if group exists
        grp_srch = [g for g in gmgr.search() if g.title.lower() == group_name.lower()]

        # if the group does not exist
        if len(grp_srch) == 0:

            # create the group
            grp = gmgr.create(group_name)

            # ensure the group was successfully created
            assert isinstance(grp, Group), 'Failed to create the group in the Cloud GIS.'

        # if the group already exists, just get it
        else:
            grp = grp_srch[0]

        return grp


def add_directory_to_gis(dir_name: str = None, gis: GIS = None):
    """Add a directory in a GIS user's content."""
    # get the directory from the .env file using the project name
    if dir_name is None:
        dir_name = os.getenv('PROJECT_NAME')

    assert isinstance(dir_name, str), 'A name for the directory must be provided explicitly in the "dir_name" ' \
                                      'parameter if there is not a PROJECT_NAME specified in the .env file.'

    if not has_arcgis:
        raise ImportError(
            "attempting to use 'arcgis' python api, but package is not installed"
        )
    else:
        # try to figure out what GIS to use
        if gis is None:
            gis = get_gis()

        assert isinstance(gis, GIS), 'A GIS instance, either an active_gis in the session, credentials in the .env file, ' \
                                     'or an active GIS instance explicitly passed into the "gis" parameter.'

        # create the directory
        res = gis.content.create_folder(dir_name)

        # if the response is None, the folder already exists, so don't worry about it
        if res is None:
            status = True

        # otherwise, set status based on if the title is in the response
        else:
            status = 'title' in res.keys()

        return status


def create_local_data_resources(data_pth: Path = None, mobile_geodatabases=False) -> Path:
    """create all the data resources for the available environment"""
    # default to the expected project structure
    if data_pth is None:
        data_pth = Path(__file__).parent.parent.parent / 'data'

    # cover if a string is inadvertently passed in as the path
    data_pth = Path(data_pth) if isinstance(data_pth, str) else data_pth

    # iterate the data subdirectories
    for data_name in ['INTERIM', 'RAW', 'PRODUCTION', 'REF']:

        # ensure the data subdirectory exists
        dir_pth = data_pth / data_name
        if not dir_pth.exists():
            dir_pth.mkdir(parents=True)

        # if working in an arcpy environment
        if has_arcpy:
            # remove the file geodatabase if it exists and recreate it to make sure compatible with version of Pro
            fgdb_pth = dir_pth / f'{data_name}.gdb'
            if fgdb_pth.exists():
                shutil.rmtree(fgdb_pth)
            arcpy.management.CreateFileGDB(str(dir_pth), f'{data_name}.gdb')

            # do the same thing for a mobile geodatabase, a sqlite database
            if mobile_geodatabases:
                gdb_pth = dir_pth / f'{data_name}.geodatabase'
                if gdb_pth.exists():
                    gdb_pth.unlink()
                arcpy.management.CreateMobileGDB(str(dir_pth), f'{data_name}.geodatabase')

    return data_pth


def create_aoi_mask_layer(paths, aoi_feature_layer, output_feature_class, style_layer=None):
    """Create a visibility mask to focus on an Area of Interest in a map."""
    assert has_arcpy, 'ArcPy is required (environment with arcpy referencing ArcGIS Pro functionality) to create an AOI mask.'

    # get the style layer if one is not provided
    styl_lyr = paths.dir_arcgis_lyrs / 'aoi_mask.lyrx' if style_layer is None else style_layer

    # ensure aoi is polygon
    geom_typ = arcpy.Describe(aoi_feature_layer).shapeType
    assert geom_typ == 'Polygon', 'The area of interest must be a polygon.'

    # if multiple polygons, dissolve into one
    if int(arcpy.management.GetCount(aoi_feature_layer)[0]) > 1:
        aoi_feature_layer = arcpy.analysis.PairwiseDissolve(aoi_feature_layer, arcpy.Geometry())

    # simplify the geometry for rendering efficiency later
    desc = arcpy.Describe(aoi_feature_layer)
    tol_val = (desc.extent.width + desc.extent.height) / 2 * 0.01
    smpl_feat = arcpy.cartography.SimplifyPolygon(aoi_feature_layer, out_feature_class=arcpy.Geometry(),
                                                  algorithm='POINT_REMOVE', tolerance=tol_val,
                                                  collapsed_point_option='NO_KEEP').split(';')[0]

    # create polygon covering the entire globe to cut out from
    coord_lst = [[-180.0, -90.0], [-180.0, 90.0], [180.0, 90.0], [180.0, -90.0], [-180.0, -90.0]]
    coord_arr = arcpy.Array((arcpy.Point(x, y) for x, y in coord_lst))
    mask_geom = [arcpy.Polygon(coord_arr, arcpy.SpatialReference(4326))]

    # erase the simplified area of interest from the global extent polygon
    mask_fc = arcpy.analysis.Erase(mask_geom, smpl_feat, output_feature_class)

    # create a layer and make it pretty
    strt_lyr = arcpy.management.MakeFeatureLayer(mask_fc)[0]
    styl_lyr = str(styl_lyr) if isinstance(styl_lyr, Path) else styl_lyr
    lyr = arcpy.management.ApplySymbologyFromLayer(strt_lyr, styl_lyr)[0]

    return lyr


# CLASSES
class Paths:
    """Object to easily reference project resources"""

    def __init__(self, data_dir=None):
        # set defaults for project and data directories
        self.dir_prj = dir_prj = Path(__file__).parent.parent.parent

        if data_dir is None:
            self.dir_data = Path(self.dir_prj, 'data')
        else:
            self.dir_data = Path(data_dir)

        # set internal project paths
        self.dir_app = Path(self.dir_prj, 'app')
        self.dir_conf = Path(self.dir_app, 'config')
        self.dir_arcgis = Path(self.dir_prj, 'arcgis')
        self.dir_arcgis_lyrs = Path(self.dir_arcgis, 'layer_files')
        # set data folders
        self.dir_raw = Path(self.dir_data, 'RAW')
        self.dir_int = Path(self.dir_data, 'INTERIM')
        self.dir_out = Path(self.dir_data, 'PROCESSED')
        # reference folder
        self.dir_ref = Path(self.dir_data, 'REF')
        # set geodatabase paths
        self.gdb_raw = str(Path(self.dir_raw, 'raw.gdb'))
        self.gdb_int = str(Path(self.dir_int, 'interim.gdb'))
        self.gdb_out = str(Path(self.dir_out, 'processed.gdb'))

    # TODO: flush this out more cleanly
    def add_dir(self, dir_name, dir_path):
        """
        allows Paths object to be extended to include more paths if needed in
        procedural code
        """
        new_path = Path(dir_path, dir_name)
        if not new_path.exists():
            new_path.mkdir()
        setattr(self, dir_name, new_path)
        return new_path

    @staticmethod
    def _create_resource(pth: Path) -> Path:
        """Internal function to create resources."""

        # see if we're working with a file geodatabase
        is_gdb = (pth.suffix == '.gdb' or pth.suffix == '.geodatabase')

        # if a geodatabase, the path dir is one level up
        pth_dir = pth.parent if is_gdb else pth

        # ensure the file directory exists including parents as necessary
        if not pth_dir.exists():
            pth_dir.mkdir(parents=True)

        # now if a geodatabase, create it
        if is_gdb:

            # flag if-exists so only run function once
            gdb_exists = arcpy.Exists(str(pth))

            # if a file geodatabase, create it
            if pth.suffix == '.gdb' and not gdb_exists:
                arcpy.management.CreateFileGDB(pth_dir, pth.stem)

            # if a mobile geodatabase, create it
            if pth.suffix == '.geodatabase' and not gdb_exists:
                arcpy.management.CreateMobileGDB(pth_dir, pth.stem)

        return pth

    def create_resources(self):
        """Create data storage resources if they do not already exist."""
        # get the data resources from the object properties
        pth_lst = [p for p in dir(self) if isinstance(p, Path)]

        # iterate the paths and create any necessary resources
        for pth in pth_lst:
            self._create_resource(pth)

        return


class DotDict(dict):
    def __getattr__(self, k):
        try:
            v = self[k]
        except KeyError:
            return super().__getattr__(k)
        if isinstance(v, dict):
            return DotDict(v)
        return v

    def __getitem__(self, k):
        if isinstance(k, str) and "." in k:
            k = k.split(".")
        if isinstance(k, (list, tuple)):
            return reduce(lambda d, kk: d[kk], k, self)
        return super().__getitem__(k)

    def get(self, k, default=None):
        if isinstance(k, str) and "." in k:
            try:
                return self[k]
            except KeyError:
                return default
        return super().get(k, default=default)


class Configuration(object):
    def __init__(self, config_file):
        self.config_file = config_file

    @property
    def settings(self):
        with open(self.config_file) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    @property
    def dot_settings(self):
        return DotDict(self.settings)


def os_cache(project: object):
    return Path(appdirs.user_cache_dir(project))


def random_prefix(len):
    """add random prefix to a string"""
    return "".join(
        random.choice(string.ascii_lowercase + string.digits) for _ in range(len)
    )


def check_overwrite_path(output, overwrite=True):
    """Non-arcpy version of check_overwrite_output"""
    output = Path(output)
    if output.exists():
        if overwrite:
            if output.is_file():
                print(f"--- --- deleting existing file {output.name}")
                output.unlink()
            if output.is_dir():
                print(f"--- --- deleting existing folder {output.name}")
                shutil.rmtree(output)
        else:
            print(f"Output file/folder {output} already exists")


def shp_to_df(shp_path, use_cols=None):
    """Read a shapefile into a Pandas dataframe dropping geometry"""
    import shapefile

    if isinstance(shp_path, PurePath):
        shp_path = str(shp_path)
    if isinstance(use_cols, str):
        use_cols = [use_cols]

    # read file, parse out the records
    sf = shapefile.Reader(shp_path)
    fields = [x[0] for x in sf.fields if x != "geometry"][1:]
    records = [list(i) for i in sf.records()]

    # make pd.DataFrame
    shape_df = pd.DataFrame(columns=fields, data=records)
    if use_cols:
        return shape_df[use_cols]
    else:
        return shape_df


def copy_shapefiles(in_file, out_folder):
    """Consistent method for copying shapefile data"""
    name = in_file.name
    with fiona.open(in_file, "r") as src:
        meta = src.meta
        out_file = Path(out_folder, name)
        if out_file.exists():
            prefix = in_file.parent.name
            out_file = Path(out_folder, f"{prefix}_{name}")
            print(f"...{in_file.name} already exists, makeing new copy with {prefix}")
        with fiona.open(out_file, "w", **meta) as dst:
            for feature in src:
                dst.write(feature)


class Registry(object):
    def __init__(self, registry_file, data_dir=None):
        if data_dir is None:
            self.data_dir = os_cache("rp_cache")
            if not self.data_dir.exists():
                os.makedirs(self.data_dir)
        else:
            self.data_dir = data_dir
        if isinstance(data_dir, str):
            self.data_dir = Path(data_dir)
        if isinstance(registry_file, str):
            self.path = Path(registry_file)
            if not self.path.exists():
                raise Exception("registry path must be to a file on your system")

    @property
    def reg_df(self):
        return pd.read_csv(self.path)

    @property
    def abspath(self):
        """Absolute path to the local storage"""
        return self.path.absolute()

    @property
    def registry_files(self):
        """List of file names in the registry cache"""
        return [f for f in self.data_dir.glob("**/*") if f.is_file()]

    @property
    def filenames(self):
        file_data = self.reg_df[["tag", "name", "store"]]
        return file_data.to_dict(orient="records")

    @property
    def local_file_paths(self):
        """List of file paths for registry items based on tag"""
        # TODO: add tag validation
        local_paths = {}
        for record in self.filenames:
            local_paths[record["tag"]] = Path(self.data_dir, record["name"])
        return local_paths

    @property
    def tags(self):
        """List of tags in registry file"""
        return self.reg_df.tag.unique().tolist()

    def copy_file(self, in_file, out_dir=None):
        """Copies data from on location to another"""
        # TODO: validation input and outputs are valid and exist
        if isinstance(in_file, str):
            in_file = Path(in_file)
        if out_dir is None:
            out_dir = self.data_dir
        # handle shapefile copies (multiple files)
        if os.path.splitext(in_file) == ".shp":
            copy_shapefiles(in_file, out_dir)
        else:
            name = in_file.name
            out_file = Path(out_dir, name)
            if out_file.exists():
                prefix = random_prefix(7)
                out_file = Path(out_dir, f"{prefix}_{name}")
            shutil.copyfile(src=in_file, dst=out_file)
        return out_file

    def get_external_files(self, source, file_name, out_folder=None):
        file_path = Path(source, file_name)
        return self.copy_file(in_file=file_path, out_dir=out_folder)


if __name__ == "__main__":
    import os
    from d4_accessiblity import utilities

    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())

    # data pathing setup
    DATA_PATH = os.getenv("DATA_DIR")  # the .env file will have this defined
    PATHS = utilities.Paths(data_dir=DATA_PATH)
    test = PATHS.add_dir(dir_name="test", dir_path=PATHS.dir_int)
    print()