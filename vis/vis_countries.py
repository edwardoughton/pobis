"""
Country specific extracts.

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

RESULTS = os.path.join(BASE_PATH, '..', 'results')
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')


def plot_median_per_user_cost(data, countries, capacity):
    """

    """
    data = data[data['GID_0'].isin(countries)]
    data = data[['GID_0', 'scenario', 'strategy', 'confidence',
        'private_cost_per_user', 'govt_cost_per_user', 'social_cost_per_user']]

    data = data.loc[data['scenario'] == 'Baseline'].reset_index()

    data.columns = ['Index', 'Country', 'Scenario', 'Strategy', 'Confidence',
        'Private Cost Per User ($USD)', 'Government Cost Per User ($USD)',
        'Social Cost Per User ($USD)']

    cost_types = [
        'Private Cost Per User ($USD)',
        'Government Cost Per User ($USD)',
        'Social Cost Per User ($USD)'
    ]

    for cost_type in cost_types:

        plot = sns.FacetGrid(
            data, col="Country", col_wrap=3,
            )

        plot.map(sns.barplot, "Strategy", cost_type)
        plt.subplots_adjust(top=0.9)

        title = 'Median {} by Universal Broadband Technology Strategy ({} Mbps)'.format(cost_type, capacity)
        plot.fig.suptitle(title)
        plot.set_xticklabels(rotation=30)
        plot.set(xlabel=None)
        plt.tight_layout()

        filename = '{}_cost_per_user_{}.png'.format(cost_type.split(' ')[0], capacity)
        plot.savefig(os.path.join(VIS, filename), index=False)

    data = data.groupby(['Country', 'Scenario', 'Strategy', 'Confidence']).mean()

    data.to_csv(os.path.join(VIS, 'per_user_cost_estimates_{}.csv'.format(capacity)))

    return 'Complete'


def plot_total_cost(data, countries):
    """

    """
    data = data[data['Country'].isin(countries)]
    data = data[['Country', 'Scenario', 'Strategy', 'Confidence', 'Cost ($Bn)']]

    data['Strategy'] = data['Strategy'].replace(['3G(FB)'], '3G (FB)')
    data['Strategy'] = data['Strategy'].replace(['3G(MW)'], '3G (W)')
    data['Strategy'] = data['Strategy'].replace(['4G(FB)'], '4G (FB)')
    data['Strategy'] = data['Strategy'].replace(['4G(MW)'], '4G (W)')

    data = data.loc[data['Scenario'] == 'Baseline']

    data.columns = ['Country', 'Scenario', 'Strategy', 'Confidence', 'Cost ($Bn)']

    plot = sns.FacetGrid(
        data, col="Country", col_wrap=3,
        )

    plot.map(sns.barplot, "Strategy", "Cost ($Bn)")
    plt.subplots_adjust(top=0.9)
    plot.fig.suptitle('Total Cost by Universal Broadband Technology Strategy')
    plot.set_xticklabels(rotation=30)
    plot.set(xlabel=None)
    plt.tight_layout()
    plot.savefig(os.path.join(VIS, 'total_cost_estimates.png'), index=False)

    data = data.groupby(['Country', 'Scenario', 'Strategy', 'Confidence']).mean()

    data.to_csv(os.path.join(VIS, 'cost_per_user.csv'))

    return 'Complete'


if __name__ == '__main__':

    countries = ['BDI', 'KEN', 'RWA', 'SSD', 'TZA', 'UGA']

    capacities = [
        10,
        2
    ]

    for capacity in capacities:

        ########
        #NOTE: only half of this code was adapted, but the rest isn't really needed.
        ########
        print('Loading median cost by pop density geotype')
        path = os.path.join(RESULTS, 'regional_cost_estimates_{}.csv'.format(capacity))
        data = pd.read_csv(path)

        print('Plotting median per user cost')
        plot_median_per_user_cost(data, countries, capacity)

        # print('Loading national cost estimates')
        # path = os.path.join(RESULTS, 'national_cost_estimates.csv')
        # data = pd.read_csv(path)

        # print('Plotting total cost')
        # plot_total_cost(data, countries)

    print('Complete')
