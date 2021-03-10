"""
Visualize data

"""
import os
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')


def get_regional_shapes():
    """

    """
    output = []

    for item in os.listdir(DATA_INTERMEDIATE):#[:15]:
        if len(item) == 3: # we only want iso3 code named folders

            filename_gid2 = 'regions_2_{}.shp'.format(item)
            path_gid2 = os.path.join(DATA_INTERMEDIATE, item, 'regions', filename_gid2)

            filename_gid1 = 'regions_1_{}.shp'.format(item)
            path_gid1 = os.path.join(DATA_INTERMEDIATE, item, 'regions', filename_gid1)

            if os.path.exists(path_gid2):
                data = gpd.read_file(path_gid2)
                data['GID_id'] = data['GID_2']
                data = data.to_dict('records')

            elif os.path.exists(path_gid1):
                data = gpd.read_file(path_gid1)
                data['GID_id'] = data['GID_1']
                data = data.to_dict('records')
            else:
               print('No shapefiles for {}'.format(item))
               continue

            for datum in data:
                output.append({
                    'geometry': datum['geometry'],
                    'properties': {
                        'GID_id': datum['GID_id'],
                    },
                })

    output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')

    return output


def plot_regions_by_geotype(data, regions, path):
    """

    """
    n = len(regions)
    data['population_km2'] = round(data['population_km2'])
    data = data[['GID_id', 'population_km2']]
    regions = regions[['GID_id', 'geometry']]#[:1000]
    regions = regions.copy()

    regions = regions.merge(data, left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)

    metric = 'population_km2'

    bins = [-1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 111607]
    labels = [
        '<20 $\mathregular{km^2}$',
        '20-43 $\mathregular{km^2}$',
        '43-69 $\mathregular{km^2}$',
        '69-109 $\mathregular{km^2}$',
        '109-171 $\mathregular{km^2}$',
        '171-257 $\mathregular{km^2}$',
        '257-367 $\mathregular{km^2}$',
        '367-541 $\mathregular{km^2}$',
        '541-1104 $\mathregular{km^2}$',
        '>1104 $\mathregular{km^2}$']

    regions['bin'] = pd.cut(
        regions[metric],
        bins=bins,
        labels=labels
    )#.fillna('<20')

    sns.set(font_scale=0.9)
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    minx, miny, maxx, maxy = regions.total_bounds
    ax.set_xlim(minx+7, maxx-12)
    ax.set_ylim(miny+5, maxy)

    regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.2, legend=True, edgecolor='grey')

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1]) #, title='Population Density (km^2)'

    #we probably need to fine tune the zoom level to bump up the resolution of the tiles
    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    # plt.subplots_adjust(top=1.5)
    fig.suptitle('Population Density Deciles for Sub-National Regions (n={})'.format(n))

    fig.tight_layout()
    fig.savefig(path)
    # fig.savefig(os.path.join(VIS, 'region_by_pop_density.pdf'))
    plt.close(fig)


def plot_sub_national_cost_per_square_km(data, regions, capacity, cost_type):
    """

    """
    n = len(regions)
    data = data.loc[data['scenario'] == 'Baseline']
    data = data.loc[data['strategy'] == '4G(W)']
    data = data.loc[data['confidence'] == 50]

    data['cost_per_km2'] = (data[cost_type[1]] / data['area_km2']) / 1e3
    data = data[['GID_id', 'cost_per_km2']]
    regions = regions[['GID_id', 'geometry']]#[:1000]

    regions = regions.merge(data, left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)

    metric = 'cost_per_km2'

    bins = [-1e9, 0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 1e9]

    if cost_type[1] == 'total_government_cost':
        bottom_label = '0 (Viable)'
    else:
        bottom_label = '0 '

    labels = [
        bottom_label,
        '<5k USD $\mathregular{km^2}$',
        '<10k USD $\mathregular{km^2}$',
        '<20k USD $\mathregular{km^2}$',
        '<30k USD $\mathregular{km^2}$',
        '<40k USD $\mathregular{km^2}$',
        '<50k USD $\mathregular{km^2}$',
        '<60k USD $\mathregular{km^2}$',
        '<70k USD $\mathregular{km^2}$',
        '<80k USD $\mathregular{km^2}$',
        '>80k USD $\mathregular{km^2}$',
    ]
    regions['bin'] = pd.cut(
        regions[metric],
        bins=bins,
        labels=labels
    )#.fillna('<20')


    fig, ax = plt.subplots(1, 1, figsize=(10,10))

    minx, miny, maxx, maxy = regions.total_bounds

    ax.set_xlim(minx+7, maxx-12)
    ax.set_ylim(miny+5, maxy)

    plt.figure()

    regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.1,
        legend=True, edgecolor='grey')

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1]) #, title='Population Density (km^2)'

    #we probably need to fine tune the zoom level to bump up the resolution of the tiles
    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    # plt.subplots_adjust(top=1.5)
    fig.suptitle(
        '{} Cost for 4G (Wireless) Universal Broadband ({} Mbps) (n={})'.format(
            cost_type[0].split(' ')[0], capacity, n))

    fig.tight_layout()
    filename = 'sub_national_{}_cost_per_square_km_{}_mbps.png'.format(
        cost_type[0].split(' ')[0], capacity)
    fig.savefig(os.path.join(VIS, filename))

    plt.close(fig)


def plot_sub_national_gross_cost(data, regions, capacity, cost_type):
    """

    """
    n = len(regions)
    data = data.loc[data['scenario'] == 'Baseline']
    data = data.loc[data['strategy'] == '4G(W)']
    data = data.loc[data['confidence'] == 50]

    metric = cost_type[1]

    data[cost_type] = data[metric] / 1e6
    data = data[['GID_id', metric]]
    regions = regions[['GID_id', 'geometry']]#[:1000]

    regions = regions.merge(data, left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)

    # bins = [-1, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 100000]
    bins = [-1,100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 100000]
    labels = [
        '<0.1 Bn USD',
        '<0.2 Bn USD',
        '<0.3 Bn USD',
        '<0.4 Bn USD',
        '<0.5 Bn USD',
        '<0.6 Bn USD',
        '<0.7 Bn USD',
        '<0.8 Bn USD',
        '<0.9 Bn USD',
        '<1 Bn USD',
        '>1 Bn USD',
        ]
    regions['bin'] = pd.cut(
        regions[metric],
        bins=bins,
        labels=labels
    )#.fillna('<20')

    fig, ax = plt.subplots(1, 1, figsize=(10,10))

    minx, miny, maxx, maxy = regions.total_bounds
    ax.set_xlim(minx+7, maxx-12)
    ax.set_ylim(miny+5, maxy)

    regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.2,
        legend=True, edgecolor='grey')

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1]) #, title='Population Density (km^2)'

    #we probably need to fine tune the zoom level to bump up the resolution of the tiles
    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    fig.suptitle(
        'Total {} Cost for 4G (Wireless) Universal Broadband ({} Mbps) (n={})'.format(
            cost_type[0].split(' ')[0], capacity, n))

    fig.tight_layout()
    filename = 'sub_national_{}_total_cost_per_square_km_{}_mbps.png'.format(
        cost_type[0].split(' ')[0], capacity)
    fig.savefig(os.path.join(VIS, filename))

    plt.close(fig)


if __name__ == '__main__':

    capacities = [
        10,
        2
    ]

    cost_types = [
        ('Private Cost Per User ($USD)', 'total_private_cost'),
        ('Government Cost Per User ($USD)', 'total_government_cost'),
        ('Social Cost Per User ($USD)', 'total_social_cost'),
    ]

    for capacity in capacities:

        for cost_type in cost_types:

            print('Working on {} ({} Mbps)'.format(cost_type[0], capacity))

            #Loading regional data by pop density geotype
            path = os.path.join(DATA_INTERMEDIATE, 'all_regional_data.csv')
            data = pd.read_csv(path)

            #Loading shapes
            path = os.path.join(DATA_INTERMEDIATE, 'all_regional_shapes.shp')
            if not os.path.exists(path):
                shapes = get_regional_shapes()
                shapes.to_file(path)
            else:
                shapes = gpd.read_file(path, crs='epsg:4326')

            #Plotting regions by geotype
            path = os.path.join(VIS, 'region_by_pop_density.png')
            if not os.path.exists(path):
                plot_regions_by_geotype(data, shapes, path)

            #Loading regional results data
            filename = 'regional_cost_estimates_{}.csv'.format(capacity)
            path = os.path.join(BASE_PATH, '..', 'results', filename)
            regional_costs = pd.read_csv(path)

            #Plotting sub-national regions by cost per km^2
            plot_sub_national_cost_per_square_km(regional_costs, shapes,
                capacity, cost_type)

    print('Complete')
