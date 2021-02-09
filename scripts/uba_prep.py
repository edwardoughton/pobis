"""
Preprocessing scripts.

Written by Ed Oughton.

Winter 2020

"""
import os
import configparser
import json
import csv
import geopandas as gpd
import pandas as pd
import pyproj
from shapely.geometry import Polygon, MultiPolygon, mapping, shape, MultiLineString, LineString
from shapely.ops import transform, unary_union, nearest_points
import fiona
from fiona.crs import from_epsg
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
import random
# import networkx as nx
# from rtree import index
# import numpy as np
import math

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def find_country_list(continent_list):
    """
    This function produces country information by continent.

    Parameters
    ----------
    continent_list : list
        Contains the name of the desired continent, e.g. ['Africa']

    Returns
    -------
    countries : list of dicts
        Contains all desired country information for countries in
        the stated continent.

    """
    # print('Loading all countries')
    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    # print('Adding continent information to country shapes')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1",keep_default_na=False)
    countries = countries.merge(load_glob_info, left_on='GID_0',
        right_on='ISO_3digit')

    subset = countries.loc[countries['continent'].isin(continent_list)]

    countries = []

    for index, country in subset.iterrows():

        if country['GID_0'] in ['COM','CPV','ESH','LBY','LSO','MUS','MYT','SYC'] :
            regional_level =  1
        else:
            regional_level = 2

        countries.append({
            'country_name': country['country'],
            'iso3': country['GID_0'],
            'iso2': country['ISO_2digit'],
            'regional_level': regional_level,
            'region': country['continent']
        })

    return countries


def process_country_shapes(country):
    """
    Creates a single national boundary for the desired country.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    # print('----')

    iso3 = country['iso3']

    path = os.path.join(DATA_INTERMEDIATE, iso3)

    if os.path.exists(os.path.join(path, 'national_outline.shp')):
        return 'Completed national outline processing'

    if not os.path.exists(path):
        # print('Creating directory {}'.format(path))
        os.makedirs(path)
    shape_path = os.path.join(path, 'national_outline.shp')

    # print('Loading all country shapes')
    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    # print('Getting specific country shape for {}'.format(iso3))
    single_country = countries[countries.GID_0 == iso3]

    # print('Excluding small shapes')
    single_country['geometry'] = single_country.apply(
        exclude_small_shapes, axis=1)

    # print('Simplifying geometries')
    # single_country['geometry'] = single_country.simplify(
    #     tolerance = 0.0005,
    #     preserve_topology=True).buffer(0.0001).simplify(
    #     tolerance = 0.0005,
    #     preserve_topology=True
    # )

    # print('Adding ISO country code and other global information')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1", keep_default_na=False)
    single_country = single_country.merge(
        load_glob_info,left_on='GID_0', right_on='ISO_3digit')

    # print('Exporting processed country shape')
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

        print('Working on {} level {}'.format(iso3, regional_level))

        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = 'gadm36_{}.shp'.format(regional_level)
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        print('Subsetting {} level {}'.format(iso3, regional_level))
        regions = regions[regions.GID_0 == iso3]

        print('Excluding small shapes')
        regions['geometry'] = regions.apply(exclude_small_shapes, axis=1)

        # print('Simplifying geometries')
        # regions['geometry'] = regions.simplify(
        #     tolerance = 0.0005,
        #     preserve_topology=True).buffer(0.0001).simplify(
        #         tolerance = 0.0005,
        #         preserve_topology=True
        #     )
        try:
            print('Writing global_regions.shp to file')
            regions.to_file(path_processed, driver='ESRI Shapefile')
        except:
            print('Unable to write {}'.format(filename))
            pass

    print('Completed processing of regional shapes level {}'.format(level))

    return print('Completed processing of regions')


def process_settlement_layer(country):
    """
    Clip the settlement layer to the chosen country boundary and place in
    desired country folder.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']

    path_settlements = os.path.join(DATA_RAW,'settlement_layer',
        'ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    iso3 = country['iso3']
    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    if os.path.exists(path_country):
        country = gpd.read_file(path_country)
    else:
        print('Must generate national_outline.shp first' )

    path_country = os.path.join(DATA_INTERMEDIATE, iso3)
    shape_path = os.path.join(path_country, 'settlements.tif')

    if os.path.exists(shape_path):
        return print('Completed settlement layer processing')

    print('Working on {} level {}'.format(iso3, regional_level))

    bbox = country.envelope
    geo = gpd.GeoDataFrame()

    geo = gpd.GeoDataFrame({'geometry': bbox})

    coords = [json.loads(geo.to_json())['features'][0]['geometry']]

    #chop on coords
    out_img, out_transform = mask(settlements, coords, crop=True)

    # Copy the metadata
    out_meta = settlements.meta.copy()

    out_meta.update({"driver": "GTiff",
                    "height": out_img.shape[1],
                    "width": out_img.shape[2],
                    "transform": out_transform,
                    "crs": 'epsg:4326'})

    with rasterio.open(shape_path, "w", **out_meta) as dest:
            dest.write(out_img)

    return print('Completed processing of settlement layer')


# def process_night_lights(country):
#     """
#     Clip the nightlights layer to the chosen country boundary and place in
#     desired country folder.

#     Parameters
#     ----------
#     country : string
#         Three digit ISO country code.

#     """
#     iso3 = country['iso3']

#     folder = os.path.join(DATA_INTERMEDIATE, iso3)
#     path_output = os.path.join(folder,'night_lights.tif')

#     if os.path.exists(path_output):
#         return print('Completed processing of nightlight layer')

#     path_country = os.path.join(folder, 'national_outline.shp')

#     filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
#     path_night_lights = os.path.join(DATA_RAW, 'nightlights', '2013',
#         filename)

#     country = gpd.read_file(path_country)

#     bbox = country.envelope

#     geo = gpd.GeoDataFrame()
#     geo = gpd.GeoDataFrame({'geometry': bbox}, crs=from_epsg('4326'))

#     coords = [json.loads(geo.to_json())['features'][0]['geometry']]

#     night_lights = rasterio.open(path_night_lights, "r+")
#     night_lights.nodata = 0

#     out_img, out_transform = mask(night_lights, coords, crop=True)

#     out_meta = night_lights.meta.copy()

#     out_meta.update({"driver": "GTiff",
#                     "height": out_img.shape[1],
#                     "width": out_img.shape[2],
#                     "transform": out_transform,
#                     "crs": 'epsg:4326'})

#     with rasterio.open(path_output, "w", **out_meta) as dest:
#             dest.write(out_img)

#     return print('Completed processing of night lights layer')


# def process_coverage_shapes(country):
#     """
#     Load in coverage maps, process and export for each country.

#     Parameters
#     ----------
#     country : string
#         Three digit ISO country code.

#     """
#     iso3 = country['iso3']
#     iso2 = country['iso2']

#     technologies = [
#         'GSM',
#         '3G',
#         '4G'
#     ]

#     for tech in technologies:

#         folder_coverage = os.path.join(DATA_INTERMEDIATE, iso3, 'coverage')
#         filename = 'coverage_{}.shp'.format(tech)
#         path_output = os.path.join(folder_coverage, filename)

#         if os.path.exists(path_output):
#             continue

#         print('Working on {} in {}'.format(tech, iso3))

#         filename = 'Inclusions_201812_{}.shp'.format(tech)
#         folder = os.path.join(DATA_RAW, 'mobile_coverage_explorer',
#             'Data_MCE')
#         inclusions = gpd.read_file(os.path.join(folder, filename))

#         if iso2 in inclusions['CNTRY_ISO2']:

#             filename = 'MCE_201812_{}.shp'.format(tech)
#             folder = os.path.join(DATA_RAW, 'mobile_coverage_explorer',
#                 'Data_MCE')
#             coverage = gpd.read_file(os.path.join(folder, filename))

#             coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

#         else:

#             filename = 'OCI_201812_{}.shp'.format(tech)
#             folder = os.path.join(DATA_RAW, 'mobile_coverage_explorer',
#                 'Data_OCI')
#             coverage = gpd.read_file(os.path.join(folder, filename))

#             coverage = coverage.loc[coverage['CNTRY_ISO3'] == iso3]

#         if len(coverage) > 0:

#             print('Dissolving polygons')
#             coverage['dissolve'] = 1
#             coverage = coverage.dissolve(by='dissolve', aggfunc='sum')

#             coverage = coverage.to_crs({'init': 'epsg:3857'})

#             print('Excluding small shapes')
#             coverage['geometry'] = coverage.apply(clean_coverage,axis=1)

#             print('Removing empty and null geometries')
#             coverage = coverage[~(coverage['geometry'].is_empty)]
#             coverage = coverage[coverage['geometry'].notnull()]

#             print('Simplifying geometries')
#             coverage['geometry'] = coverage.simplify(
#                 tolerance = 0.005,
#                 preserve_topology=True).buffer(0.0001).simplify(
#                 tolerance = 0.005,
#                 preserve_topology=True
#             )

#             coverage = coverage.to_crs({'init': 'epsg:4326'})

#             if not os.path.exists(folder_coverage):
#                 os.makedirs(folder_coverage)

#             coverage.to_file(path_output, driver='ESRI Shapefile')

#     print('Completed processing of coverage shapes')


# def process_regional_coverage(country):
#     """
#     This functions estimates the area covered by each cellular
#     technology.

#     Parameters
#     ----------
#     country : dict
#         Contains specific country parameters.

#     Returns
#     -------
#     output : dict
#         Results for cellular coverage by each technology for
#         each region.

#     """
#     level = country['regional_level']
#     iso3 = country['iso3']
#     gid_level = 'GID_{}'.format(level)

#     filename = 'regions_{}_{}.shp'.format(level, iso3)
#     folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
#     path = os.path.join(folder, filename)
#     regions = gpd.read_file(path)

#     technologies = [
#         'GSM',
#         '3G',
#         '4G'
#     ]

#     output = {}

#     for tech in technologies:

#         folder = os.path.join(DATA_INTERMEDIATE, iso3, 'coverage')
#         path =  os.path.join(folder, 'coverage_{}.shp'.format(tech))

#         if os.path.exists(path):

#             coverage = gpd.read_file(path)

#             segments = gpd.overlay(regions, coverage, how='intersection')

#             tech_coverage = {}

#             for idx, region in segments.iterrows():

#                 area_km2 = round(area_of_polygon(region['geometry']) / 1e6)

#                 tech_coverage[region[gid_level]] = area_km2

#             output[tech] = tech_coverage

#     return output


def get_regional_data(country):
    """
    Extract regional data including luminosity and population.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    iso3 = country['iso3']
    level = country['regional_level']
    gid_level = 'GID_{}'.format(level)

    path_output = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_data.csv')

    # if os.path.exists(path_output):
    #     return print('Regional data already exists')

    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    coverage = process_regional_coverage(country)

    single_country = gpd.read_file(path_country)

    # path_night_lights = os.path.join(DATA_INTERMEDIATE, iso3,
    #     'night_lights.tif')
    path_settlements = os.path.join(DATA_INTERMEDIATE, iso3,
        'settlements.tif')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)

    regions = gpd.read_file(path)

    results = []

    for index, region in regions.iterrows():

        # with rasterio.open(path_night_lights) as src:

        #     affine = src.transform
        #     array = src.read(1)
        #     array[array <= 0] = 0

        #     luminosity_summation = [d['sum'] for d in zonal_stats(
        #         region['geometry'],
        #         array,
        #         stats=['sum'],
        #         affine=affine)][0]

        with rasterio.open(path_settlements) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            population_summation = [d['sum'] for d in zonal_stats(
                region['geometry'], array, stats=['sum'], affine=affine)][0]

        area_km2 = round(area_of_polygon(region['geometry']) / 1e6)

        if area_km2 == 0:
            continue

        # if luminosity_summation == None:
        #     luminosity_summation = 0

        # if 'GSM' in [c for c in coverage.keys()]:
        #     if region[gid_level] in coverage['GSM']:
        #         coverage_GSM_km2 = coverage['GSM'][region[gid_level]]
        #     else:
        #         coverage_GSM_km2 = 0
        # else:
        #     coverage_GSM_km2 = 0

        # if '3G' in [c for c in coverage.keys()]:
        #     if region[gid_level] in coverage['3G']:
        #         coverage_3G_km2 = coverage['3G'][region[gid_level]]
        #     else:
        #         coverage_3G_km2 = 0
        # else:
        #     coverage_3G_km2 = 0

        # if '4G' in [c for c in coverage.keys()]:
        #     if region[gid_level] in coverage['4G']:
        #         coverage_4G_km2 = coverage['4G'][region[gid_level]]
        #     else:
        #         coverage_4G_km2 = 0
        # else:
        #     coverage_4G_km2 = 0

        results.append({
            # 'country_name': region['country_name'],
            'GID_0': region['GID_0'],
            'GID_id': region[gid_level],
            'GID_level': gid_level,
            # 'mean_luminosity_km2': luminosity_summation / area_km2 if luminosity_summation else 0,
            'population': population_summation,
            'area_km2': area_km2,
            'population_km2': population_summation / area_km2 if population_summation else 0,
            # 'coverage_GSM_percent': round(coverage_GSM_km2 / area_km2 * 100 if coverage_GSM_km2 else 0, 1),
            # 'coverage_3G_percent': round(coverage_3G_km2 / area_km2 * 100 if coverage_3G_km2 else 0, 1),
            # 'coverage_4G_percent': round(coverage_4G_km2 / area_km2 * 100 if coverage_4G_km2 else 0, 1),
        })

    # print('Working on backhaul')
    # backhaul_lut = estimate_backhaul(iso3, country['region'], '2025')

    # print('Working on estimating sites')
    # results = estimate_sites(results, iso3, backhaul_lut)

    results_df = pd.DataFrame(results)

    results_df.to_csv(path_output, index=False)

    print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed night lights data querying')


def estimate_sites(data, iso3, backhaul_lut):
    """

    """
    output = []

    existing_site_data_path = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'sites.csv')

    existing_site_data = {}
    if os.path.exists(existing_site_data_path):
        site_data = pd.read_csv(existing_site_data_path)
        site_data = site_data.to_dict('records')
        for item in site_data:
            existing_site_data[item['GID_id']] = item['sites']

    population = 0

    for region in data:

        if region['population'] == None:
            continue

        population += int(region['population'])

    path = os.path.join(DATA_RAW, 'wb_mobile_coverage', 'wb_population_coverage.csv')
    coverage = 0
    coverage_data = pd.read_csv(path, keep_default_na=False)
    coverage_data = coverage_data.loc[coverage_data['Country ISO3'] == iso3]
    if len(coverage_data) > 0:
        coverage = coverage_data['2016'].values[0]

    population_covered = population * (coverage / 100)

    path = os.path.join(DATA_RAW, 'real_site_data', 'tower_counts', 'tower_counts.csv')
    towers = 0
    tower_data = pd.read_csv(path, encoding = "ISO-8859-1", keep_default_na=False)
    tower_data = tower_data.loc[tower_data['ISO_3digit'] == iso3]

    if tower_data['count'].values[0] > 0:
        towers = tower_data['count'].values[0]

    try:
        towers_per_pop = float(towers) / float(population_covered)
    except:
        towers_per_pop = 0

    tower_backhaul_lut = estimate_backhaul_type(backhaul_lut)

    data = sorted(data, key=lambda k: k['population_km2'], reverse=True)

    covered_pop_so_far = 0

    for region in data:

        #first try to use actual data
        if len(existing_site_data) > 0:
            sites_estimated_total = existing_site_data[region['GID_id']]
            if region['area_km2'] > 0:
                sites_estimated_km2 = sites_estimated_total / region['area_km2']
            else:
                sites_estimated_km2 = 0

        #or if we don't have data estimate sites per area
        else:
            if covered_pop_so_far < population_covered:

                sites_estimated_total = region['population'] * towers_per_pop
                sites_estimated_km2 = region['population_km2'] * towers_per_pop

                if math.isnan(sites_estimated_total):
                    sites_estimated_total = 0
                if math.isnan(sites_estimated_km2):
                    sites_estimated_km2 = 0

            else:
                sites_estimated_total = 0
                sites_estimated_km2 = 0

        backhaul_fiber = 0
        backhaul_copper = 0
        backhaul_microwave = 0
        backhaul_satellite = 0

        for i in range(1, int(round(sites_estimated_total)) + 1):

            num = random.uniform(0, 1)

            if num <= tower_backhaul_lut['fiber']:
                backhaul_fiber += 1
            elif tower_backhaul_lut['fiber'] < num <= tower_backhaul_lut['copper']:
                backhaul_copper += 1
            elif tower_backhaul_lut['copper'] < num <= tower_backhaul_lut['microwave']:
                backhaul_microwave += 1
            elif tower_backhaul_lut['microwave'] < num:
                backhaul_satellite += 1

        output.append({
                # 'country_name': region['country_name'],
                'GID_0': region['GID_0'],
                'GID_id': region['GID_id'],
                'GID_level': region['GID_level'],
                'mean_luminosity_km2': region['mean_luminosity_km2'],
                'population': region['population'],
                'area_km2': region['area_km2'],
                'population_km2': region['population_km2'],
                'coverage_GSM_percent': region['coverage_GSM_percent'],
                'coverage_3G_percent': region['coverage_3G_percent'],
                'coverage_4G_percent': region['coverage_4G_percent'],
                'sites_estimated_total': sites_estimated_total,
                'sites_estimated_km2': sites_estimated_km2,
                'sites_3G': sites_estimated_total * (region['coverage_3G_percent'] /100),
                'sites_4G': sites_estimated_total * (region['coverage_4G_percent'] /100),
                'backhaul_fiber': backhaul_fiber,
                'backhaul_copper': backhaul_copper,
                'backhaul_microwave': backhaul_microwave,
                'backhaul_satellite': backhaul_satellite,
            })

        if region['population'] == None:
            continue

        covered_pop_so_far += region['population']

    return output


def estimate_backhaul(iso3, region, year):
    """

    """
    output = []

    path = os.path.join(BASE_PATH, 'raw', 'gsma', 'backhaul.csv')
    backhaul_lut = pd.read_csv(path)
    backhaul_lut = backhaul_lut.to_dict('records')

    for item in backhaul_lut:
        if region == item['Region'] and int(item['Year']) == int(year):
            output.append({
                'tech': item['Technology'],
                'percentage': int(item['Value']),
            })

    return output


def estimate_backhaul_type(backhaul_lut):
    """
    Estimate backhaul type.

    """
    output = {}

    preference = [
        'fiber',
        'copper',
        'microwave',
        'satellite'
    ]

    perc_so_far = 0

    for tech in preference:
        for item in backhaul_lut:
            if tech == item['tech'].lower():
                perc = item['percentage']
                output[tech] = (perc + perc_so_far) / 100
                perc_so_far += perc

    return output


def area_of_polygon(geom):
    """
    Returns the area of a polygon. Assume WGS84 as crs.

    """
    geod = pyproj.Geod(ellps="WGS84")

    poly_area, poly_perimeter = geod.geometry_area_perimeter(
        geom
    )

    return abs(poly_area)


def length_of_line(geom):
    """
    Returns the length of a linestring. Assume WGS84 as crs.

    """
    geod = pyproj.Geod(ellps="WGS84")

    total_length = geod.line_length(*geom.xy)

    return abs(total_length)


def estimate_numers_of_sites(linear_regressor, x_value):
    """
    Function to predict the y value from the stated x value.

    Parameters
    ----------
    linear_regressor : object
        Linear regression object.
    x_value : float
        The stated x value we want to use to predict y.

    Returns
    -------
    result : float
        The predicted y value.

    """
    if not x_value == 0:
        result = linear_regressor.predict(x_value)
        result = result[0,0]
    else:
        result = 0

    return result


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


def estimate_core_nodes(iso3, pop_density_km2, settlement_size):
    """
    This function identifies settlements which exceed a desired settlement
    size. It is assumed fiber exists at settlements over, for example,
    20,000 inhabitants.
    Parameters
    ----------
    iso3 : string
        ISO 3 digit country code.
    pop_density_km2 : int
        Population density threshold for identifying built up areas.
    settlement_size : int
        Overall sittelement size assumption, e.g. 20,000 inhabitants.
    Returns
    -------
    output : list of dicts
        Identified major settlements as Geojson objects.
    """
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements.tif')

    with rasterio.open(path) as src:
        data = src.read()
        threshold = pop_density_km2
        data[data < threshold] = 0
        data[data >= threshold] = 1
        polygons = rasterio.features.shapes(data, transform=src.transform)
        shapes_df = gpd.GeoDataFrame.from_features(
            [
                {'geometry': poly, 'properties':{'value':value}}
                for poly, value in polygons
                if value > 0
            ],
            crs='epsg:4326'
        )

    stats = zonal_stats(shapes_df['geometry'], path, stats=['count', 'sum'])

    stats_df = pd.DataFrame(stats)

    nodes = pd.concat([shapes_df, stats_df], axis=1).drop(columns='value')

    nodes = nodes[nodes['sum'] >= settlement_size]

    nodes['geometry'] = nodes['geometry'].centroid

    nodes = get_points_inside_country(nodes, iso3)

    output = []

    for index, item in enumerate(nodes.to_dict('records')):
        output.append({

            'type': 'Feature',
            'geometry': mapping(item['geometry']),
            'properties': {
                'network_layer': 'core',
                'id': 'core_{}'.format(index),
                'node_number': index,
            }
        })

    return output


def get_points_inside_country(nodes, iso3):
    """
    Check settlement locations lie inside target country.
    Parameters
    ----------
    nodes : dataframe
        A geopandas dataframe containing settlement nodes.
    iso3 : string
        ISO 3 digit country code.
    Returns
    -------
    nodes : dataframe
        A geopandas dataframe containing settlement nodes.
    """
    filename = 'national_outline.shp'
    path = os.path.join(DATA_INTERMEDIATE, iso3, filename)

    national_outline = gpd.read_file(path)

    bool_list = nodes.intersects(national_outline.unary_union)

    nodes = pd.concat([nodes, bool_list], axis=1)

    nodes = nodes[nodes[0] == True].drop(columns=0)

    return nodes


def generate_agglomeration_lut(country):
    """
    Generate a lookup table of agglomerations.
    """
    iso3 = country['iso3']
    regional_level = country['regional_level']
    GID_level = 'GID_{}'.format(regional_level)

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations')
    if not os.path.exists(folder):
        os.makedirs(folder)
    path_output = os.path.join(folder, 'agglomerations.shp')

    if os.path.exists(path_output):
        return print('Agglomeration processing has already completed')

    print('Working on {} agglomeration lookup table'.format(iso3))

    filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs="epsg:4326")

    path_settlements = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements.tif')
    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    folder_tifs = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations', 'tifs')
    if not os.path.exists(folder_tifs):
        os.makedirs(folder_tifs)

    for idx, region in regions.iterrows():

        bbox = region['geometry'].envelope
        geo = gpd.GeoDataFrame()
        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[idx])
        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        #chop on coords
        out_img, out_transform = mask(settlements, coords, crop=True)

        # Copy the metadata
        out_meta = settlements.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": 'epsg:4326'})

        path_output = os.path.join(folder_tifs, region[GID_level] + '.tif')

        with rasterio.open(path_output, "w", **out_meta) as dest:
                dest.write(out_img)

    print('Completed settlement.tif regional segmentation')

    nodes, missing_nodes = find_nodes(country, regions)

    missing_nodes = get_missing_nodes(country, regions, missing_nodes, 10, 10)

    nodes = nodes + missing_nodes

    nodes = gpd.GeoDataFrame.from_features(nodes, crs='epsg:4326')

    bool_list = nodes.intersects(regions['geometry'].unary_union)
    nodes = pd.concat([nodes, bool_list], axis=1)
    nodes = nodes[nodes[0] == True].drop(columns=0)

    agglomerations = []

    print('Identifying agglomerations')
    for idx1, region in regions.iterrows():
        seen = set()
        for idx2, node in nodes.iterrows():
            if node['geometry'].intersects(region['geometry']):
                agglomerations.append({
                    'type': 'Feature',
                    'geometry': mapping(node['geometry']),
                    'properties': {
                        'id': idx1,
                        'GID_0': region['GID_0'],
                        GID_level: region[GID_level],
                        'population': node['sum'],
                    }
                })
                seen.add(region[GID_level])
        if len(seen) == 0:
            agglomerations.append({
                    'type': 'Feature',
                    'geometry': mapping(region['geometry'].centroid),
                    'properties': {
                        'id': 'regional_node',
                        'GID_0': region['GID_0'],
                        GID_level: region[GID_level],
                        'population': 1,
                    }
                })

    agglomerations = gpd.GeoDataFrame.from_features(
            [
                {
                    'geometry': item['geometry'],
                    'properties': {
                        'id': item['properties']['id'],
                        'GID_0':item['properties']['GID_0'],
                        GID_level: item['properties'][GID_level],
                        'population': item['properties']['population'],
                    }
                }
                for item in agglomerations
            ],
            crs='epsg:4326'
        )

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations')
    path_output = os.path.join(folder, 'agglomerations' + '.shp')

    agglomerations.to_file(path_output)

    agglomerations['lon'] = agglomerations['geometry'].x
    agglomerations['lat'] = agglomerations['geometry'].y
    agglomerations = agglomerations[['lon', 'lat', GID_level, 'population']]
    agglomerations.to_csv(os.path.join(folder, 'agglomerations.csv'), index=False)

    return print('Agglomerations layer complete')


def process_existing_fiber(country):
    """
    Load and process existing fiber data.
    """
    iso3 = country['iso3']
    iso2 = country['iso2'].lower()

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'network_existing')
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = 'core_edges_existing.shp'
    path_output = os.path.join(folder, filename)

    if os.path.exists(path_output):
        return print('Existing fiber already processed')

    path = os.path.join(DATA_RAW, 'afterfiber', 'afterfiber.shp')

    shape = fiona.open(path)

    data = []

    for item in shape:
        if item['properties']['iso2'].lower() == iso2.lower():

            if item['geometry']['type'] == 'LineString':
                if int(item['properties']['live']) == 1:

                    data.append({
                        'type': 'Feature',
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': item['geometry']['coordinates'],
                        },
                        'properties': {
                            'operators': item['properties']['operator'],
                            'source': 'existing'
                        }
                    })

            if item['geometry']['type'] == 'MultiLineString':
                if int(item['properties']['live']) == 1:
                    try:
                        geom = MultiLineString(item['geometry']['coordinates'])
                        for line in geom:
                            data.append({
                                'type': 'Feature',
                                'geometry': mapping(line),
                                'properties': {
                                    'operators': item['properties']['operator'],
                                    'source': 'existing'
                                }
                            })
                    except:
                        # some geometries are incorrect from data source
                        # exclude to avoid issues
                        pass

    if len(data) == 0:
        return print('No existing infrastructure')

    data = gpd.GeoDataFrame.from_features(data)
    data.to_file(path_output, crs='epsg:4326')

    return print('Existing fiber processed')


def find_nodes_on_existing_infrastructure(country):
    """
    Find those agglomerations which are within a buffered zone of
    existing fiber links.
    """
    iso3 = country['iso3']

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'network_existing')
    filename = 'core_nodes_existing.shp'
    path_output = os.path.join(folder, filename)

    if os.path.exists(path_output):
        return print('Already found nodes on existing infrastructure')
    else:
        if not os.path.dirname(path_output):
            os.makedirs(os.path.dirname(path_output))

    path = os.path.join(folder, 'core_edges_existing.shp')
    if not os.path.exists(path):
        return print('No existing infrastructure')

    existing_infra = gpd.read_file(path, crs='epsg:4326')

    existing_infra = existing_infra.to_crs(epsg=3857)
    existing_infra['geometry'] = existing_infra['geometry'].buffer(5000)
    existing_infra = existing_infra.to_crs(epsg=4326)

    # shape_output = os.path.join(DATA_INTERMEDIATE, iso3, 'network', 'core_edges_buffered.shp')
    # existing_infra.to_file(shape_output, crs='epsg:4326')

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'agglomerations', 'agglomerations.shp')
    agglomerations = gpd.read_file(path, crs='epsg:4326')

    bool_list = agglomerations.intersects(existing_infra.unary_union)

    agglomerations = pd.concat([agglomerations, bool_list], axis=1)

    agglomerations = agglomerations[agglomerations[0] == True].drop(columns=0)

    agglomerations['source'] = 'existing'

    agglomerations.to_file(path_output, crs='epsg:4326')

    return print('Found nodes on existing infrastructure')


if __name__ == '__main__':

    countries = find_country_list(['Africa'])
    countries = countries#[::-1]

    for country in countries:#[:1]:

        print('----')
        print('-- Working on {}'.format(country['country_name']))

        print('Processing country boundary')
        process_country_shapes(country)

        print('Processing regions')
        process_regions(country)

        print('Processing settlement layer')
        process_settlement_layer(country)

        # print('Processing night lights')
        # process_night_lights(country)

        # print('Processing coverage shapes')
        # process_coverage_shapes(country)

        print('Getting regional data')
        get_regional_data(country)

    all_regional_data = []

    for country in countries:

        print('----')
        print('-- Working on {}'.format(country['country_name']))

        path = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'regional_data.csv')
        data = pd.read_csv(path, keep_default_na=False)
        data = data.to_dict('records')
        all_regional_data = all_regional_data + data

    all_regional_data = pd.DataFrame(all_regional_data)

    path = os.path.join(DATA_INTERMEDIATE, 'all_regional_data.csv')
    all_regional_data.to_csv(path, index=False)
