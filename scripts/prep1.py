"""
Read in available site data

Written by Ed Oughton

21st April 2020

"""
import os
import csv
import configparser
import pandas as pd
import geopandas as gpd
import openpyxl
import numpy as np
from shapely.geometry import MultiPolygon
from shapely.ops import transform, unary_union

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw', 'real_site_data')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_country_shape(country):
    """
    Creates a single national boundary for the desired country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']

    path = os.path.join(DATA_INTERMEDIATE, iso3)

    if os.path.exists(os.path.join(path, 'national_outline.shp')):
        return 'Completed national outline processing'

    if not os.path.exists(path):
        os.makedirs(path)

    shape_path = os.path.join(path, 'national_outline.shp')

    path = os.path.join(DATA_RAW, '..', 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    single_country = countries[countries.GID_0 == iso3]

    single_country['geometry'] = single_country.apply(
        exclude_small_shapes, axis=1)

    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")
    single_country = single_country.merge(
        load_glob_info,left_on='GID_0', right_on='ISO_3digit')

    single_country.to_file(shape_path, driver='ESRI Shapefile')

    return print('Processing country shape complete')


def process_regions(country):
    """
    Function for processing the lowest desired subnational regions for the
    chosen country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    regions = []

    iso3 = country['iso3']
    level = country['regional_level']

    for regional_level in range(1, level + 1):

        filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
        path_processed = os.path.join(folder, filename)

        if os.path.exists(path_processed):
            continue

        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = 'gadm36_{}.shp'.format(regional_level)
        path_regions = os.path.join(DATA_RAW, '..',  'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        regions = regions[regions.GID_0 == iso3]

        regions['geometry'] = regions.apply(exclude_small_shapes, axis=1)

        try:
            regions.to_file(path_processed, driver='ESRI Shapefile')
        except:
            print('Unable to write {}'.format(filename))
            pass

        print('Completed processing of regional shapes level {}'.format(level))

    return


def exclude_small_shapes(x):
    """
    Remove small multipolygon shapes.

    Parameters
    ---------
    x : polygon
        Feature to simplify.

    Returns
    -------
    MultiPolygon : MultiPolygon
        Shapely MultiPolygon geometry without tiny shapes.

    """
    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        return x.geometry

    # if its a multipolygon, we start trying to simplify
    # and remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        area1 = 0.01
        area2 = 50

        # dont remove shapes if total area is already very small
        if x.geometry.area < area1:
            return x.geometry
        # remove bigger shapes if country is really big

        if x['GID_0'] in ['CHL','IDN']:
            threshold = 0.01
        elif x['GID_0'] in ['RUS','GRL','CAN','USA']:
            threshold = 0.01

        elif x.geometry.area > area2:
            threshold = 0.1
        else:
            threshold = 0.001

        # save remaining polygons as new multipolygon for
        # the specific country
        new_geom = []
        for y in x.geometry:
            if y.area > threshold:
                new_geom.append(y)

        return MultiPolygon(new_geom)


def process_coverage_shapes(country):
    """
    Load in coverage maps, process and export for each country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']
    iso2 = country['iso2']

    technologies = [
        'GSM',
        '3G',
        '4G'
    ]

    for tech in technologies:

        folder_coverage = os.path.join(DATA_INTERMEDIATE, iso3, 'coverage')
        filename = 'coverage_{}.shp'.format(tech)
        path_output = os.path.join(folder_coverage, filename)

        if os.path.exists(path_output):
            continue

        print('----')
        print('Working on {} in {}'.format(tech, iso3))

        filename = 'Inclusions_201812_{}.shp'.format(tech)
        folder = os.path.join(DATA_RAW, '..', 'mobile_coverage_explorer',
            'Data_MCE')
        inclusions = gpd.read_file(os.path.join(folder, filename))

        if iso2 in inclusions['CNTRY_ISO2']:

            filename = 'MCE_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, '..', 'mobile_coverage_explorer',
                'Data_MCE')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

        else:

            filename = 'OCI_201812_{}.shp'.format(tech)
            folder = os.path.join(DATA_RAW, '..', 'mobile_coverage_explorer',
                'Data_OCI')
            coverage = gpd.read_file(os.path.join(folder, filename))

            coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

        if len(coverage) > 0:

            print('Dissolving polygons')
            coverage['dissolve'] = 1
            coverage = coverage.dissolve(by='dissolve', aggfunc='sum')

            coverage = coverage.to_crs({'init': 'epsg:3857'})

            print('Excluding small shapes')
            coverage['geometry'] = coverage.apply(clean_coverage,axis=1)

            print('Removing empty and null geometries')
            coverage = coverage[~(coverage['geometry'].is_empty)]
            coverage = coverage[coverage['geometry'].notnull()]

            print('Simplifying geometries')
            coverage['geometry'] = coverage.simplify(
                tolerance = 0.005,
                preserve_topology=True).buffer(0.0001).simplify(
                tolerance = 0.005,
                preserve_topology=True
            )

            coverage = coverage.to_crs({'init': 'epsg:4326'})

            if not os.path.exists(folder_coverage):
                os.makedirs(folder_coverage)

            coverage.to_file(path_output, driver='ESRI Shapefile')

    print('Processed coverage shapes')


def clean_coverage(x):
    """
    Cleans the coverage polygons by remove small multipolygon shapes.

    Parameters
    ---------
    x : polygon
        Feature to simplify.

    Returns
    -------
    MultiPolygon : MultiPolygon
        Shapely MultiPolygon geometry without tiny shapes.

    """
    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        if x.geometry.area > 1e7:
            return x.geometry

    # if its a multipolygon, we start trying to simplify and
    # remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        threshold = 1e7

        # save remaining polygons as new multipolygon for
        # the specific country
        new_geom = []
        for y in x.geometry:

            if y.area > threshold:
                new_geom.append(y)

        return MultiPolygon(new_geom)


def load_regions(path):
    """
    Load in regions.

    Parameters
    ---------
    path : string
        Path to regions .csv file.

    Returns
    -------
    regions : dataframe
        All regional data.

    """
    regions = gpd.read_file(path, crs='epsg:4326')

    return regions


def process_kenya():
    """
    Process all data for Kenya.

    """
    print('Processing Kenya data')
    folder = os.path.join(DATA_INTERMEDIATE, 'KEN', 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(DATA_INTERMEDIATE, 'KEN', 'regions', 'regions_2_KEN.shp')
    regions = load_regions(path)

    path = os.path.join(DATA_RAW, 'KEN', 'Operators_Mobile_Transmitters_Data.csv')
    df = pd.read_csv(path)

    df = df[['SiteID', 'LONGITUDE', 'LATITUDE']]
    df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.LONGITUDE, df.LATITUDE), crs='epsg:4326')
    df = df.loc[df['LONGITUDE'] < 100]

    df = df.dropna()
    print('Unique cells in Kenya: {}'.format(len(df)))

    df = df.drop_duplicates(['SiteID'])
    print('Unique cell sites in Kenya: {}'.format(len(df)))

    df.to_file(os.path.join(folder, 'sites.shp'), crs='epsg:4326')

    f = lambda x:np.sum(df.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    sites = regions[['GID_2', 'sites']].copy()
    sites['tech'] = '2G'

    sites.rename(columns = {'GID_2':'GID_id'}, inplace = True)
    sites['GID_level'] = 2

    sites = sites[['GID_id', 'sites']]
    sites = sites.groupby(['GID_id'], as_index=False).sum()

    sites.to_csv(os.path.join(folder, 'sites.csv'), index=False)


def process_senegal():
    """
    Process all data for Senegal.

    """
    print('Processing Senegal data')
    folder = os.path.join(DATA_INTERMEDIATE, 'SEN', 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(DATA_INTERMEDIATE, 'SEN', 'regions', 'regions_2_SEN.shp')
    regions = load_regions(path)

    filename = 'Bilan_Couverture_Orange_Dec2017.csv'
    path = os.path.join(DATA_RAW, 'SEN', filename)

    load_senegal(path, regions, folder)


def load_senegal(path, regions, folder):
    """
    Load all data for Senegal and process.

    The data are for Orange Sonatel, therefore are not a complete
    national dataset. In liaison with Sonatel, the company state
    they have:

    - Total sites: 2545
    - Total 2G cells: 11,626
    - Total 3G cells: 26,196
    - Total 4G cells: 7,069

    However, we don't have geographic data for these estimates.

    The data available here yields only 15,302 cells, equating to
    1,711 sites when dropping duplicates of the site name. Given
    Sonatel has a ~54% market share, the number of sites per region
    are increased to provide a national picture, based on the spatial
    distribution of this geospatial data. This results in approximately
    3,170 sites, which is very close to the 3,151 estimated by
    TowerXchange.

    Parameters
    ---------
    path : string
        Path to site data.
    regions : dataframe
        All regional data.
    folder : string
        Output folder.

    """
    print('Reading Senegal data')
    sites = pd.read_csv(path, encoding = "ISO-8859-1")
    sites = sites[['Cell_ID', 'Site_Name', 'LATITUDE', 'LONGITUDE']]
    sites = gpd.GeoDataFrame(
        sites, geometry=gpd.points_from_xy(sites.LONGITUDE, sites.LATITUDE))
    sites = sites.dropna()

    sites = sites.drop_duplicates(['Site_Name'])

    sites.crs = 'epsg:31028'
    sites = sites.to_crs('epsg:4326')

    sites.to_file(os.path.join(folder, 'sites.shp'), crs='epsg:4326')

    f = lambda x:np.sum(sites.intersects(x))
    regions['sites'] = regions['geometry'].apply(f)

    regions = regions[['GID_2', 'sites']]
    regions['tech'] = 'unknown'
    regions.rename(columns = {'GID_2':'GID_id'}, inplace = True)
    regions['GID_level'] = 2

    #Increase counts to obtain representive nation picture
    regions['sites'] = round(regions['sites'].copy() / 54 * 100)

    print('Writing Senegal csv data')
    folder = os.path.join(DATA_INTERMEDIATE, 'SEN', 'sites')
    regions.to_csv(os.path.join(folder, 'sites.csv'), index=False)

    return


if __name__ == "__main__":

    countries = [
        {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 2},
        {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2},
    ]

    for country in countries:

        print('Processing country boundary')
        process_country_shape(country)

        print('Processing regions')
        process_regions(country)

        print('Processing coverage shapes')
        process_coverage_shapes(country)

        if country['iso3'] == 'KEN':
            process_kenya()

        if country['iso3'] == 'SEN':
            process_senegal()
