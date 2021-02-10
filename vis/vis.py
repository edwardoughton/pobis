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


def plot_median_per_user_cost(data):
    """

    """
    n = len(data)
    sns.set(font_scale=1.5)
    data['Population Density Decile (km^2)'] = data['Decile']
    plot = sns.catplot(
        x='Population Density Decile (km^2)', y='Cost Per User ($)', col="Scenario",
        col_order=['Low', 'Baseline', 'High'],
        row="Strategy", kind='bar', data=data, sharex=False
        )
    plot.fig.suptitle(
        'Median Per User Cost for Universal Broaband by Population Density Deciles (n={})'.format(n))
    plot.set_xticklabels(rotation=70)
    plt.tight_layout()
    plot.savefig(os.path.join(VIS, 'per_user_cost_numeric.png'), dpi=300)
    plt.close()

    return 'Complete'


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


def plot_regions_by_geotype(data, regions):
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
    fig.savefig(os.path.join(VIS, 'region_by_pop_density.png'))
    # fig.savefig(os.path.join(VIS, 'region_by_pop_density.pdf'))
    plt.close(fig)


def plot_sub_national_cost_per_square_km(data, regions):
    """

    """
    n = len(regions)
    data = data.loc[data['scenario'] == 'Baseline']
    data = data.loc[data['strategy'] == '4G(MW)']
    data = data.loc[data['confidence'] == 50]

    data['cost_per_km2'] = (data['total_cost'] / data['area_km2']) / 1e3
    data = data[['GID_id', 'cost_per_km2']]
    regions = regions[['GID_id', 'geometry']]#[:1000]

    regions = regions.merge(data, left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)

    metric = 'cost_per_km2'

    # bins = [-1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1e9]
    #[-1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 1e9]
    bins = [-1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 1e9]
    labels = [
        '<5k USD $\mathregular{km^2}$',
        '<10k USD $\mathregular{km^2}$',
        '<20k USD $\mathregular{km^2}$',
        '<30k USD $\mathregular{km^2}$',
        '<40k USD $\mathregular{km^2}$',
        '<50k USD $\mathregular{km^2}$',
        '<60k USD $\mathregular{km^2}$',
        '<70k USD $\mathregular{km^2}$',
        '<80k USD $\mathregular{km^2}$',
        '<90k USD $\mathregular{km^2}$',
        '>90k USD $\mathregular{km^2}$',
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

    regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.2, legend=True, edgecolor='grey')

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1]) #, title='Population Density (km^2)'

    #we probably need to fine tune the zoom level to bump up the resolution of the tiles
    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    # plt.subplots_adjust(top=1.5)
    fig.suptitle(
        'Square Kilometer Cost for 4G (Wireless) Universal Broadband (10 Mbps) (n={})'.format(n)) # fontsize=12

    fig.tight_layout()
    fig.savefig(os.path.join(VIS, 'sub_national_cost_per_square_km.png'))
    # fig.savefig(os.path.join(VIS, 'region_by_total_cost.pdf'))
    plt.close(fig)


def plot_sub_national_gross_cost(data, regions):
    """

    """
    n = len(regions)
    data = data.loc[data['scenario'] == 'Baseline']
    data = data.loc[data['strategy'] == '4G(MW)']
    data = data.loc[data['confidence'] == 50]

    data['total_cost'] = data['total_cost'] / 1e6
    data = data[['GID_id', 'total_cost']]
    regions = regions[['GID_id', 'geometry']]#[:1000]

    regions = regions.merge(data, left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)

    metric = 'total_cost'

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

    regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.2, legend=True, edgecolor='grey')

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1]) #, title='Population Density (km^2)'

    #we probably need to fine tune the zoom level to bump up the resolution of the tiles
    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    # plt.subplots_adjust(top=1.5)
    fig.suptitle('Total Cost for 4G (Wireless) Universal Broadband (10 Mbps) (n={})'.format(n))

    fig.tight_layout()
    fig.savefig(os.path.join(VIS, 'sub_national_gross_cost.png'))
    # fig.savefig(os.path.join(VIS, 'region_by_total_cost.pdf'))
    plt.close(fig)


def plot_national_costs(national_costs):
    """

    """
    countries = [
        'NGA',
        'COD',
        'ETH',
        'SDN',
        'ZAF',
        'TZA',
        'EGY',
        'AGO',
        'KEN',
        'DZA',
        'MOZ',
        'ZMB',
        'MLI',
        'TCD',
        'MDG',
        'CMR',
        'MAR',
        'SSD',
        'UGA',
        'NER',
    ]
    national_costs['Strategy'] = national_costs['Strategy'].replace(['3G(FB)'], '3G (FB)')
    national_costs['Strategy'] = national_costs['Strategy'].replace(['3G(MW)'], '3G (MW)')
    national_costs['Strategy'] = national_costs['Strategy'].replace(['4G(FB)'], '4G (FB)')
    national_costs['Strategy'] = national_costs['Strategy'].replace(['4G(MW)'], '4G (MW)')

    national_costs = national_costs[national_costs['Country'].isin(countries)]
    sns.set(font_scale=0.9)
    plot = sns.FacetGrid(
        national_costs, row="Strategy", col="Scenario", sharex=False,
        row_order=['3G (FB)', '3G (MW)', '4G (FB)', '4G (MW)'],
        col_order=['Low', 'Baseline', 'High'])
    plot.map(sns.barplot, 'Country', "Cost ($Bn)", order=countries)
    plt.subplots_adjust(top=0.9)
    plot.fig.suptitle('Total Cost for Universal Broadband of 10 Mbps Per User')
    plot.set_xticklabels(rotation=70)#, fontsize=8)
    plot.set(xlabel=None)
    plt.tight_layout()
    plot.savefig(os.path.join(VIS, 'national_cost_estimates.png')) #, dpi=300


def plot_total_costs(total_costs):
    """

    """
    total_costs['Strategy'] = total_costs['Strategy'].replace(['3G(FB)'], '3G (FB)')
    total_costs['Strategy'] = total_costs['Strategy'].replace(['3G(MW)'], '3G (MW)')
    total_costs['Strategy'] = total_costs['Strategy'].replace(['4G(FB)'], '4G (FB)')
    total_costs['Strategy'] = total_costs['Strategy'].replace(['4G(MW)'], '4G (MW)')

    plot = sns.FacetGrid(
        total_costs, col="Scenario", height=4, aspect=.5,
        col_order=['Low', 'Baseline', 'High'])
    plot.map(sns.barplot, "Strategy", "Cost ($Bn)")
    plt.subplots_adjust(top=0.9)
    plot.fig.suptitle('Total Cost for Universal Broadband of 10 Mbps Per User')
    plot.set_xticklabels(rotation=30)
    plot.set(xlabel=None)
    plt.tight_layout()
    plot.savefig(os.path.join(VIS, 'total_cost_estimates.png')) #, dpi=300


if __name__ == '__main__':

    print('Loading median cost by pop density geotype')
    path = os.path.join(DATA_INTERMEDIATE, 'median_per_user_cost_by_pop_density.csv')
    data = pd.read_csv(path)

    print('Plotting using numerically labelled geotypes')
    plot_median_per_user_cost(data)

    print('Loading regional data by pop density geotype')
    path = os.path.join(DATA_INTERMEDIATE, 'all_regional_data.csv')
    data = pd.read_csv(path)

    print('Loading shapes')
    path = os.path.join(DATA_INTERMEDIATE, 'all_regional_shapes.shp')
    if not os.path.exists(path):
        shapes = get_regional_shapes()
        shapes.to_file(path)
    else:
        shapes = gpd.read_file(path, crs='epsg:4326')

    print('Plotting regions by geotype')
    plot_regions_by_geotype(data, shapes)

    print('Loading regional results data')
    path = os.path.join(BASE_PATH, '..', 'results', 'regional_cost_estimates.csv')
    regional_costs = pd.read_csv(path)

    print('Plotting sub-national regions by cost per km^2')
    plot_sub_national_cost_per_square_km(regional_costs, shapes)

    print('Plotting sub-national regions by gross cost')
    plot_sub_national_gross_cost(regional_costs, shapes)

    print('Loading national results data')
    path = os.path.join(BASE_PATH, '..', 'results', 'national_cost_estimates.csv')
    national_costs = pd.read_csv(path)

    print('Plotting cost estimates')
    plot_national_costs(national_costs)

    print('Loading total results data')
    path = os.path.join(BASE_PATH, '..', 'results', 'total_cost_estimates.csv')
    total_costs = pd.read_csv(path)

    print('Plotting cost estimates')
    plot_total_costs(total_costs)

    print('Complete')
