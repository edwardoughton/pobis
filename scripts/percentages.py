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


def process_percentages():
    """

    """
    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    capacities = [
        10,
        30
    ]

    cost_types = [
        'financial_cost',
        'government_cost'
    ]

    for capacity in capacities:
        for cost_type in cost_types:

            print('- {} GB per user ({})'.format(capacity, cost_type.split('_')[0]))

            #Processing PODIS data
            process_technologies_data(capacity, cost_type)

            #Processing PODIS data
            process_sharing_data(capacity, cost_type)

    return


def process_technologies_data(capacity, cost_type):
    """
    Process the technology results.

    Parameters
    ----------
    capacity : int
        The capacity we wish to process.
    cost_type : string
        The cost type we wish to process.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data = []

    path = os.path.join(RESULTS, 'national_results')

    for filename in os.listdir(path):

        # if not capacity in filename:
        #     continue

        if not 'national_market_cost_results' in filename:
            continue

        filepath = os.path.join(path, filename)

        sample = pd.read_csv(filepath)
        sample = sample.to_dict('records')
        data = data + sample

    data = pd.DataFrame(data)

    #subset based on defined capacity
    handle = '{}_{}_{}'.format(capacity, capacity, capacity)
    data = data[data['scenario'].str.contains(str(handle))].reset_index()

    #subset based on defined confidence (mean results)
    data = data.loc[data['confidence'] == 50]
    data = data.loc[data['input_cost'] == 'baseline']

    #relabel long strings
    scenario = 'low_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'Low')
    scenario = 'baseline_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'Baseline')
    scenario = 'high_{}_{}_{}'.format(capacity, capacity, capacity)
    data['scenario'] = data['scenario'].replace([scenario], 'High')
    data['strategy'] = data['strategy'].replace(['3G_epc_wireless_baseline_baseline_baseline_baseline'], '3G (W)')
    data['strategy'] = data['strategy'].replace(['3G_epc_fiber_baseline_baseline_baseline_baseline'], '3G (FB)')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline'], '4G (W)')
    data['strategy'] = data['strategy'].replace(['4G_epc_fiber_baseline_baseline_baseline_baseline'], '4G (FB)')

    data = data[data['strategy'].isin(['3G (W)','3G (FB)','4G (W)','4G (FB)'])]

    data['generation'] = data['strategy'].str.split(' ').str[0]
    data['backhaul'] = data['strategy'].str.split(' ').str[1]

    data = data[['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost', cost_type]]

    data_gen = data.copy()
    data_gen['4G_vs_3G'] = round(data_gen.groupby(
                                    ['GID_0', 'scenario', 'backhaul', 'input_cost'])[
                                    cost_type].pct_change()*100)

    data_gen = data_gen.dropna()

    data = pd.merge(data,
            data_gen[['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost', '4G_vs_3G']],
            how='left',
            left_on=['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost'],
            right_on = ['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost']
        )

    data_backhaul = data[['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost', cost_type]].copy()

    data_backhaul['w_over_fb'] = round(data_backhaul.groupby(
                                    ['GID_0', 'scenario', 'generation', 'input_cost'])[
                                    cost_type].pct_change()*100)
    data_gen = data_gen.dropna()

    data = pd.merge(data,
            data_backhaul[['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost', 'w_over_fb']],
            how='left',
            left_on=['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost'],
            right_on = ['GID_0', 'scenario', 'generation', 'backhaul', 'input_cost']
        )

    #Writing regional per user cost data to .csv
    filename = 'percentages_technologies_{}_{}.csv'.format(capacity, cost_type)
    path = os.path.join(OUTPUT, filename)
    data.to_csv(path, index=False)

    return


def process_sharing_data(capacity, cost_type):
    """
    Process any infrastructure sharing strategies.

    Parameters
    ----------
    capacity : int
        The capacity we wish to process.
    cost_type : string
        The cost type we wish to process.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data = []

    path = os.path.join(RESULTS, 'national_results')

    for filename in os.listdir(path):

        # if not capacity in filename:
        #     continue

        if not 'national_market_cost_results' in filename:
            continue

        filepath = os.path.join(path, filename)

        sample = pd.read_csv(filepath)
        sample = sample.to_dict('records')
        data = data + sample

    data = pd.DataFrame(data)

    #subset based on defined capacity
    handle = '{}_{}_{}'.format(capacity, capacity, capacity)
    data = data[data['scenario'].str.contains(str(handle))].reset_index()

    #subset based on defined confidence (mean results)
    data = data.loc[data['confidence'] == 50]
    data = data.loc[data['input_cost'] == 'baseline']

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
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_srn_srn_baseline_baseline_baseline'], 'SRN')

    data = data[data['strategy'].isin(['Baseline','Passive','Active','SRN'])]

    data = data[['GID_0', 'scenario', 'strategy', 'input_cost', cost_type]]

    baseline = data.loc[data['strategy'] == 'Baseline']

    data = pd.merge(data, baseline,
                how='left',
                left_on=['GID_0', 'scenario', 'input_cost'],
                right_on = ['GID_0', 'scenario', 'input_cost']
            )

    cost_type_y = cost_type + '_y'
    cost_type_x = cost_type + '_x'
    data['saving_against_baseline'] = ((abs(data[cost_type_y] - data[cost_type_x])) /
                                    data[cost_type_y]) * 100

    data['saving_against_baseline'] = round(data['saving_against_baseline'], 1)

    #Writing regional per user cost data to .csv
    filename = 'percentages_sharing_{}_{}.csv'.format(capacity, cost_type)
    path = os.path.join(OUTPUT, filename)
    data.to_csv(path, index=False)

    return


if __name__ == '__main__':

    process_percentages()

    print('-- Processing completed')
