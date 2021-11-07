"""
Estimate the percentage differences across scenarios and strategies.

Written by Ed Oughton.

July 2020

"""
import os
import configparser
import numpy as np
import pandas as pd

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

RESULTS = os.path.join(BASE_PATH, '..', 'results', 'model_results')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'percentages')


def process_technologies_data(data, capacity, cost_type):
    """
    Process the technology results.

    Parameters
    ----------
    data : pandas df
        All model results.
    capacity : int
        The capacity we wish to process.
    cost_type : string
        The cost type we wish to process.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    #subset based on defined capacity
    data = data[data['scenario'].str.contains(str(capacity))].reset_index()

    #subset based on defined confidence (mean results)
    data = data.loc[data['confidence'] == 50]

    #relabel long strings
    scenario = 'low_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'Low')
    scenario = 'baseline_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'Baseline')
    scenario = 'high_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'High')
    data['strategy'] = data['strategy'].replace(['3G_epc_wireless_baseline_baseline_baseline_baseline_baseline'], '3G (W)')
    data['strategy'] = data['strategy'].replace(['3G_epc_fiber_baseline_baseline_baseline_baseline_baseline'], '3G (FB)')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'], '4G (W)')
    data['strategy'] = data['strategy'].replace(['4G_epc_fiber_baseline_baseline_baseline_baseline_baseline'], '4G (FB)')

    data['generation'] = data['strategy'].str.split(' ').str[0]
    data['backhaul'] = data['strategy'].str.split(' ').str[1]

    data = data[['GID_0', 'scenario', 'generation', 'backhaul', cost_type]]

    data_gen = data.copy()
    data_gen['4G_vs_3G'] = round(data_gen.groupby(
                                    ['GID_0', 'scenario', 'backhaul'])[
                                    cost_type].pct_change()*100)

    data_gen = data_gen.dropna()

    data = pd.merge(data,
            data_gen[['GID_0', 'scenario', 'generation', 'backhaul', '4G_vs_3G']],
            how='left',
            left_on=['GID_0', 'scenario', 'generation', 'backhaul'],
            right_on = ['GID_0', 'scenario', 'generation', 'backhaul']
        )

    data_backhaul = data[['GID_0', 'scenario', 'generation', 'backhaul', cost_type]].copy()

    data_backhaul['w_over_fb'] = round(data_backhaul.groupby(
                                    ['GID_0', 'scenario', 'generation'])[
                                    cost_type].pct_change()*100)
    data_gen = data_gen.dropna()

    data = pd.merge(data,
            data_backhaul[['GID_0', 'scenario', 'generation', 'backhaul', 'w_over_fb']],
            how='left',
            left_on=['GID_0', 'scenario', 'generation', 'backhaul'],
            right_on = ['GID_0', 'scenario', 'generation', 'backhaul']
        )

    return data


def process_sharing_data(data, capacity, cost_type):
    """
    Process any infrastructure sharing strategies.

    Parameters
    ----------
    data : pandas df
        All model results.
    capacity : int
        The capacity we wish to process.
    cost_type : string
        The cost type we wish to process.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    #subset based on defined capacity
    data = data[data['scenario'].str.contains(str(capacity))].reset_index()

    #subset based on defined confidence (mean results)
    data = data.loc[data['confidence'] == 50]

    #relabel long strings
    scenario = 'low_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'Low')
    scenario = 'baseline_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'Base')
    scenario = 'high_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'High')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'], 'Baseline')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_psb_baseline_baseline_baseline_baseline'], 'Passive')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_moran_baseline_baseline_baseline_baseline'], 'Active')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_srn_baseline_baseline_baseline'], 'SRN')

    data = data[['GID_0', 'scenario', 'strategy', cost_type]]

    baseline = data.loc[data['strategy'] == 'Baseline']

    data = pd.merge(data, baseline,
                how='left',
                left_on=['GID_0', 'scenario'],
                right_on = ['GID_0', 'scenario']
            )

    cost_type_y = cost_type + '_y'
    cost_type_x = cost_type + '_x'
    data['saving_against_baseline'] = ((abs(data[cost_type_y] - data[cost_type_x])) /
                                    data[cost_type_y]) * 100

    data['saving_against_baseline'] = round(data['saving_against_baseline'], 1)

    return data


if __name__ == '__main__':

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    capacities = [
        10,
        2
    ]

    cost_types = [
        'financial_cost',
        'government_cost'
    ]

    for capacity in capacities:
        for cost_type in cost_types:

            print('- {} Mbps per user ({})'.format(capacity, cost_type.split('_')[0]))

            #Loading PODIS cost estimate data
            filename = 'national_market_results_technology_options.csv'
            path = os.path.join(RESULTS, filename)
            data = pd.read_csv(path)

            #Processing PODIS data
            data = process_technologies_data(data, capacity, cost_type)

            #Writing regional per user cost data to .csv
            filename = 'percentages_technologies_{}_{}.csv'.format(capacity, cost_type)
            path = os.path.join(OUTPUT, filename)
            data.to_csv(path, index=False)

            #Loading PODIS cost estimate data
            filename = 'national_market_results_business_model_options.csv'
            path = os.path.join(RESULTS, filename)
            data = pd.read_csv(path)

            #Processing PODIS data
            data = process_sharing_data(data, capacity, cost_type)

            #Writing regional per user cost data to .csv
            filename = 'percentages_sharing_{}_{}.csv'.format(capacity, cost_type)
            path = os.path.join(OUTPUT, filename)
            data.to_csv(path, index=False)

    print('-- Processing completed')
