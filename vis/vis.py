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


def plot_cost_per_user(data, capacity):
    """

    """
    print(data)
    n = len(data)
    sns.set(font_scale=1.5)
    data['Population Density Decile (km^2)'] = data['Decile']

    data = data[[
        'Scenario', 'Strategy', 'Confidence', 'Population Density Decile (km^2)',
        'Private Cost Per User ($USD)', 'Government Cost Per User ($USD)',
    ]]

    data = pd.melt(data,
        id_vars=['Scenario', 'Strategy', 'Confidence', 'Population Density Decile (km^2)'],
        var_name='Cost Type', value_name='Cost')

    # plot = sns.histplot(data, x='Population Density Decile (km^2)',
    #     hue='Cost Type', weights='percentage',
    #         multiple='stack', palette='tab20c', shrink=0.8)

    g = sns.FacetGrid(data, col="Scenario")
    g.map(sns.histplot, "tip")

    # plot = sns.catplot(
    #     x='Population Density Decile (km^2)', y=cost_type, col="Scenario",
    #     col_order=['Low', 'Baseline', 'High'],
    #     row="Strategy", kind='bar', data=data, sharex=False
    # )

    # title = 'Cost Per User by Universal Broadband Technology Strategy ({} Mbps) (n={})'.format(
    #     capacity, n)
    # plot.fig.suptitle(title)
    # plot.set_xticklabels(rotation=70)
    # plt.tight_layout()
    # filename = 'per_user_{}_cost_{}.png'.format(cost_type.split(' ')[0], capacity)
    # plot.savefig(os.path.join(VIS, filename), dpi=300)
    # plt.close()
    # sns.set(font_scale=1)

    return 'Complete'


def plot_median_per_user_cost(data, capacity, cost_type):
    """

    """
    n = len(data)
    sns.set(font_scale=1.5)
    data['Population Density Decile (km^2)'] = data['Decile']
    plot = sns.catplot(
        x='Population Density Decile (km^2)', y=cost_type, col="Scenario",
        col_order=['Low', 'Baseline', 'High'],
        row="Strategy", kind='bar', data=data, sharex=False
    )
    title = 'Median {} by Universal Broadband Technology Strategy ({} Mbps) (n={})'.format(
        cost_type, capacity, n)
    plot.fig.suptitle(title)
    plot.set_xticklabels(rotation=70)
    plt.tight_layout()
    filename = 'per_user_{}_cost_{}.png'.format(cost_type.split(' ')[0], capacity)
    plot.savefig(os.path.join(VIS, filename), dpi=300)
    plt.close()
    sns.set(font_scale=1)

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
    labels = [
        '0 (Viable)',
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


# def plot_national_costs(national_costs):
#     """

#     """
#     countries = [
#         'NGA',
#         'COD',
#         'ETH',
#         'SDN',
#         'ZAF',
#         'TZA',
#         'EGY',
#         'AGO',
#         'KEN',
#         'DZA',
#         'MOZ',
#         'ZMB',
#         'MLI',
#         'TCD',
#         'MDG',
#         'CMR',
#         'MAR',
#         'SSD',
#         'UGA',
#         'NER',
#     ]
#     national_costs['Strategy'] = national_costs['Strategy'].replace(['3G(FB)'], '3G (FB)')
#     national_costs['Strategy'] = national_costs['Strategy'].replace(['3G(W)'], '3G (W)')
#     national_costs['Strategy'] = national_costs['Strategy'].replace(['4G(FB)'], '4G (FB)')
#     national_costs['Strategy'] = national_costs['Strategy'].replace(['4G(W)'], '4G (W)')

#     national_costs = national_costs[national_costs['Country'].isin(countries)]
#     sns.set(font_scale=0.9)
#     plot = sns.FacetGrid(
#         national_costs, row="Strategy", col="Scenario", sharex=False,
#         row_order=['3G (FB)', '3G (W)', '4G (FB)', '4G (W)'],
#         col_order=['Low', 'Baseline', 'High'])
#     plot.map(sns.barplot, 'Country', "Cost ($Bn)", order=countries)
#     plt.subplots_adjust(top=0.9)
#     plot.fig.suptitle('Total Cost for Universal Broadband of 10 Mbps Per User')
#     plot.set_xticklabels(rotation=70)#, fontsize=8)
#     plot.set(xlabel=None)
#     plt.tight_layout()
#     plot.savefig(os.path.join(VIS, 'national_cost_estimates.png')) #, dpi=300


# def plot_total_costs(total_costs):
#     """

#     """
#     total_costs['Strategy'] = total_costs['Strategy'].replace(['3G(FB)'], '3G (FB)')
#     total_costs['Strategy'] = total_costs['Strategy'].replace(['3G(W)'], '3G (W)')
#     total_costs['Strategy'] = total_costs['Strategy'].replace(['4G(FB)'], '4G (FB)')
#     total_costs['Strategy'] = total_costs['Strategy'].replace(['4G(W)'], '4G (W)')

#     plot = sns.FacetGrid(
#         total_costs, col="Scenario", height=4, aspect=.5,
#         col_order=['Low', 'Baseline', 'High'])
#     plot.map(sns.barplot, "Strategy", "Cost ($Bn)")
#     plt.subplots_adjust(top=0.9)
#     plot.fig.suptitle('Total Cost for Universal Broadband of 10 Mbps Per User')
#     plot.set_xticklabels(rotation=30)
#     plot.set(xlabel=None)
#     plt.tight_layout()
#     plot.savefig(os.path.join(VIS, 'total_cost_estimates.png')) #, dpi=300


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

        # #Loading median cost by pop density geotype
        # filename = 'median_per_user_cost_by_pop_density_{}.csv'.format(capacity)
        # path = os.path.join(DATA_INTERMEDIATE, filename)
        # data = pd.read_csv(path)

        # #Plotting using numerically labelled geotypes
        # plot_cost_per_user(data, capacity)

        for cost_type in cost_types:

            print('Working on {} ({} Mbps)'.format(cost_type[0], capacity))

            #Loading median cost by pop density geotype
            filename = 'median_per_user_cost_by_pop_density_{}.csv'.format(capacity)
            path = os.path.join(DATA_INTERMEDIATE, filename)
            data = pd.read_csv(path)

            #Plotting using numerically labelled geotypes
            plot_median_per_user_cost(data, capacity, cost_type[0])

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
            plot_sub_national_cost_per_square_km(regional_costs, shapes, capacity, cost_type)

            # #Plotting sub-national regions by gross cost
            # plot_sub_national_gross_cost(regional_costs, shapes, capacity, cost_type)

            # #Loading national results data
            # filename = 'national_cost_estimates_{}.csv'.format(capacity)
            # path = os.path.join(BASE_PATH, '..', 'results', filename)
            # national_costs = pd.read_csv(path)

            # #Plotting cost estimates
            # plot_national_costs(national_costs)

            # #Loading total results data
            # filename = 'total_cost_estimates_{}.csv'.format(capacity)
            # path = os.path.join(BASE_PATH, '..', 'results', filename)
            # total_costs = pd.read_csv(path)

            # #Plotting cost estimates
            # plot_total_costs(total_costs)

    print('Complete')
