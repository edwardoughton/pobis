"""
Visualize data for the whole of the African continent.

Written by Ed Oughton

September 2020

"""
import os
import configparser
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx
from pylab import * #is this needed

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
USER_COSTS = os.path.join(BASE_PATH, '..', 'results', 'user_costs')
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')


def get_regional_shapes():
    """
    Load regional shapes.

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


def plot_regions_by_geotype(data, regions, path, disputed_areas):
    """
    Plot regions by geotype.

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
    )

    sns.set(font_scale=0.9)
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    minx, miny, maxx, maxy = regions.total_bounds
    ax.set_xlim(minx+7, maxx-12)
    ax.set_ylim(miny+5, maxy)

    base = regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.2,
        legend=True, edgecolor='grey')

    replacement_dict = [('<', ''), ('\\mathregular{km^2}', ''), ('>', ''), ('$', ''), (' ', '')]
    cmap = cm.get_cmap('inferno_r', len(bins)) # PiYG
    blended_hex = get_blended_hex(regions, cmap, bins, replacement_dict)
    abyei = disputed_areas[disputed_areas['WB_NAME'] == 'Abyei']
    abyei.plot(ax=base, color=blended_hex[0], edgecolor='grey', linewidth=0.2)
    western_sahara = disputed_areas[disputed_areas['WB_NAME'] == 'Western Sahara']
    western_sahara.plot(ax=base, color='lightgrey', edgecolor='grey', linewidth=0.2)

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    name = 'Population Density Deciles for Sub-National Regions (n={})'.format(n)
    fig.suptitle(name)

    fig.tight_layout()
    fig.savefig(path)

    plt.close(fig)


def plot_sub_national_cost_per_user(data, regions, capacity, cost_type, disputed_areas):
    """
    Plot sub national cost per user.

    """
    n = len(regions)
    handle = 'baseline_{}_{}_{}'.format(capacity, capacity, capacity)
    data = data.loc[data['scenario'] == handle]
    data = data.loc[data['strategy'] == '4G_epc_wireless_baseline_baseline_baseline_baseline']
    data = data.loc[data['confidence'] == 50]
    data = data.loc[data['input_cost'] == 'baseline']

    data = data[['GID_id', cost_type[2]]]
    regions = regions[['GID_id', 'geometry']]

    regions = regions.merge(data, left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)

    metric = cost_type[2]

    if cost_type[2] == 'govt_cost_per_user':
        bins = [-1e9,0,100,200,300,400,500,600,700,800,900,1000, 1e9]
        labels = ['Viable','$100','$200','$300','$400','$500','$600',
        '$700','$800','$900','$1000', '>$1000']
    else:
        bins = [0,300,600,900,1200,1500,1800,2100,2400,2700,3000,3300,1e9]
        labels = ['$300','$600','$900','$1200','$1500','$1800',
        '$2100','$2400','$2700','$3000','$3300','>$3300']

    regions['bin'] = pd.cut(
        regions[metric],
        bins=bins,
        labels=labels
    )

    fig, ax = plt.subplots(1, 1, figsize=(10,10))

    minx, miny, maxx, maxy = regions.total_bounds

    ax.set_xlim(minx+7, maxx-12)
    ax.set_ylim(miny+5, maxy)

    plt.figure()

    base = regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.1,
        legend=True, edgecolor='grey')

    replacement_dict = [('<', ''), ('$', ''), ('#', ''), (' ', ''), ('>', '')]
    cmap = cm.get_cmap('inferno_r', len(bins)) # PiYG
    blended_hex = get_blended_hex(regions, cmap, bins, replacement_dict)
    abyei = disputed_areas[disputed_areas['WB_NAME'] == 'Abyei']
    abyei.plot(ax=base, color=blended_hex[0], edgecolor='grey', linewidth=0.2)
    western_sahara = disputed_areas[disputed_areas['WB_NAME'] == 'Western Sahara']
    western_sahara.plot(ax=base, color='lightgrey', edgecolor='grey', linewidth=0.2)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    fig.suptitle(
        '{} Per User Cost for 4G (Wireless) Universal Broadband ({} GB/Month) (n={}) (10-year NPV)'.format(
            cost_type[0].split(' ')[0], capacity, n))

    fig.tight_layout()
    filename = 'z_cost_per_user_spatially_{}_{}_mbps.png'.format(
        cost_type[0].split(' ')[0], capacity)
    fig.savefig(os.path.join(VIS, filename))

    plt.close(fig)


def get_blended_hex(regions, cmap, bins, replacement_dict):
    """
    Get a blended hex.

    """
    sdn = regions.loc[regions['GID_id'] == 'SDN.17.1_1']
    ssd = regions.loc[regions['GID_id'] == 'SSD.5.4_1']

    sdn = sdn['bin'].values[0]
    ssd = ssd['bin'].values[0]

    values_hex = {}

    for i, z in zip(range(cmap.N), bins):
        rgba = cmap(i) # rgb2hex accepts rgb or rgba
        values_hex[str(z)] = str(matplotlib.colors.rgb2hex(rgba))

    for k, v in replacement_dict:
        sdn = sdn.replace(k, v)
        ssd = ssd.replace(k, v)

    if '-' in sdn:
        sdn = sdn[:2]
    if '-' in ssd:
        ssd = ssd[:2]

    if 'Viable' in sdn:
        sdn = -1000000000.0
    if 'Viable' in ssd:
        ssd = -1000000000.0

    sdn_hex = values_hex[str(sdn)].replace('#', '')
    ssd_hex = values_hex[str(ssd)].replace('#', '')

    blended_hex = jcolor_split(sdn_hex, ssd_hex)

    return blended_hex


def jcolor_split(hex_color_1, hex_color_2):
    """
    Blend two hex colors.

    """
    r1s = hex_color_1[0:2]
    g1s = hex_color_1[2:4]
    b1s = hex_color_1[4:6]

    r2s = hex_color_2[0:2]
    g2s = hex_color_2[2:4]
    b2s = hex_color_2[4:6]

    r1 = int(r1s, 16); g1 = int(g1s, 16); b1 = int(b1s, 16)
    r2 = int(r2s, 16); g2 = int(g2s, 16); b2 = int(b2s, 16)

    # get the average
    ra = int(round(float(r1+r2)/2))
    ga = int(round(float(g1+g2)/2))
    ba = int(round(float(b1+b2)/2))

    format1 = '#' + format(ra, 'x') + format(ga, 'x') + format(ba, 'x')
    format2 = '#' + str(ra) + str(ga) + str(ba)

    return (format1, format2)


def plot_investment_as_gdp_percent(data, gdp, regions, capacity, cost_type, disputed_areas):
    """
    Plot sub national cost per user.

    """
    if not cost_type[1] == 'total_government_cost':
        return

    gdp = gdp[['iso3', 'gdp']]

    n = len(regions)
    handle = 'baseline_{}_{}_{}'.format(capacity, capacity, capacity)
    data = data.loc[data['scenario'] == handle]
    data = data.loc[data['strategy'] == '4G_epc_wireless_baseline_baseline_baseline_baseline']
    data = data.loc[data['confidence'] == 50]
    data = data.loc[data['input_cost'] == 'baseline']

    data = data[['GID_0', 'GID_id', cost_type[1]]]
    data = pd.merge(left=data, right=gdp, how='left',  left_on='GID_0', right_on='iso3')
    data['gdp_percentage'] = round(data[cost_type[1]] / data['gdp'] *100, 3)

    regions = regions[['GID_id', 'geometry']]

    regions = regions.merge(data, left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)

    metric = 'gdp_percentage'

    bins = [-1e9,0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1, 1e9]
    if cost_type[1] == 'total_government_cost':
        labels = ['Viable','<0.1%','<0.2%','<0.3%','<0.4%','<0.5%',
        '<0.6%','<0.7%','<0.8%','<0.9%','<1%','>1%']
    else:
        bins = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1, 1e9]
        labels = ['<0.1%','<0.2%','<0.3%','<0.4%','<0.5%',
            '<0.6%','<0.7%','<0.8%','<0.9%','<1%','>1%']

    regions['bin'] = pd.cut(
        regions[metric],
        bins=bins,
        labels=labels
    )

    fig, ax = plt.subplots(1, 1, figsize=(10,10))

    minx, miny, maxx, maxy = regions.total_bounds

    ax.set_xlim(minx+7, maxx-12)
    ax.set_ylim(miny+5, maxy)

    plt.figure()

    base = regions.plot(column='bin', ax=ax, cmap='inferno_r', linewidth=0.1,
        legend=True, edgecolor='grey')

    replacement_dict = [('<', ''), ('%', ''), ('#', ''), (' ', ''), ('>', '')]
    cmap = cm.get_cmap('inferno_r', len(bins)) # PiYG
    blended_hex = get_blended_hex(regions, cmap, bins, replacement_dict)
    abyei = disputed_areas[disputed_areas['WB_NAME'] == 'Abyei']
    try:
        abyei.plot(ax=base, color=blended_hex[1], edgecolor='grey', linewidth=0.2)
    except:
        abyei.plot(ax=base, color=blended_hex[0], edgecolor='grey', linewidth=0.2)
    western_sahara = disputed_areas[disputed_areas['WB_NAME'] == 'Western Sahara']
    western_sahara.plot(ax=base, color='lightgrey', edgecolor='grey', linewidth=0.2)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles[::-1], labels[::-1])

    ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    fig.suptitle(
        str('{} Cost for 4G (Wireless) Universal Broadband ({} GB/Month) ({}GDP) (n={}) (10-year NPV)'.format(
            cost_type[0].split(' ')[0], capacity, '%', n)))

    fig.tight_layout()
    filename = 'z_gdp_percentage_spatially_{}_{}_mbps.png'.format(
        cost_type[0].split(' ')[0], capacity)
    fig.savefig(os.path.join(VIS, filename))

    plt.close(fig)


if __name__ == '__main__':

    capacities = [
        10,
        20,
        30
    ]

    cost_types = [
        ('Private Mean Cost Per User ($USD)', 'total_private_cost', 'private_cost_per_user'),
        ('Government Mean Cost Per User ($USD)', 'total_government_cost', 'govt_cost_per_user'),
        ('Financial Mean Cost Per User ($USD)', 'total_financial_cost', 'financial_cost_per_user'),
    ]

    da_path = os.path.join(VIS, '..', 'disputed_areas', 'DisputedAreasWGS84.shp')
    disputed_areas = gpd.read_file(da_path, crs='epsg:4326')

    for capacity in capacities:
        for cost_type in cost_types:

            print('Working on {} ({} GB/Month)'.format(cost_type[0], capacity))

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
            path = os.path.join(VIS, 'z_region_by_pop_density.png')
            if not os.path.exists(path):
                plot_regions_by_geotype(data, shapes, path, disputed_areas)

            #Loading regional results data
            filename = 'user_cost_estimates.csv'
            path = os.path.join(USER_COSTS, filename)
            regional_costs = pd.read_csv(path)

            #Plotting sub-national regions by cost per user
            plot_sub_national_cost_per_user(regional_costs, shapes,
                capacity, cost_type, disputed_areas)

            #Loading regional results data
            path = os.path.join(VIS, '..', 'gdp.csv')
            gdp = pd.read_csv(path)

            #Plotting sub-national regions by cost per user
            plot_investment_as_gdp_percent(regional_costs, gdp, shapes,
                capacity, cost_type, disputed_areas)

    print('Complete')
