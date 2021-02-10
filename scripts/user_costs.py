"""
Estimate the costs of upgrades.

Written by Ed Oughton.

July 2020

"""
import os
import configparser
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
RESULTS = os.path.join(BASE_PATH, '..', 'results')
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')


def process_data(data):
    """

    """
    # Add population density
    data['population_density_km2'] = data['population'] / data['area_km2']
    # print(data.columns)
    # Only get baseline for integration (slim down the number of variants)
    # data = data.loc[data['integration'] == 'baseline']

    # #subset desited columns
    # data = data[['scenario', 'strategy', 'confidence',
    #     'population_density_km2', 'cost_per_network_user']]

    #relabel long strings
    data['scenario'] = data['scenario'].replace(['low_10_10_10'], 'Low')
    data['scenario'] = data['scenario'].replace(['baseline_10_10_10'], 'Baseline')
    data['scenario'] = data['scenario'].replace(['high_10_10_10'], 'High')
    data['strategy'] = data['strategy'].replace(['3G_epc_wireless_baseline_baseline_baseline_baseline_baseline'], '3G (MW)')
    data['strategy'] = data['strategy'].replace(['3G_epc_fiber_baseline_baseline_baseline_baseline_baseline'], '3G (FB)')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline_baseline'], '4G (MW)')
    data['strategy'] = data['strategy'].replace(['4G_epc_fiber_baseline_baseline_baseline_baseline_baseline'], '4G (FB)')

    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=["cost_per_network_user"], how="all")
    data['cost_user'] = round(data['cost_per_network_user'])

    return data


def define_density_categories(data):
    """

    """
    bins = [-1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 111607]
    labels = ['<20','20-43','43-69','69-109','109-171','171-257','257-367','367-541','541-1104','>1104']

    data['decile'] = pd.cut(
        data['population_density_km2'],
        bins=bins,
        labels=labels
    )#.fillna('<20')

    # bins = [0, 25, 100, 300, 1500, 500000]
    # labels = ['Rural 3', 'Rural 2', 'Rural 1','Suburban', 'Urban']
    # data['geotype'] = pd.cut(
    #     data['population_density_km2'],
    #     bins=bins,
    #     labels=labels
    # )

    # data['decile'] = pd.qcut(
    #     data['population_density_km2'],
    #     10, #number of buckets - deciles
    #     # labels=[1,2,3,4,5,6,7,8,9,10]
    # )

    # bins = [0, 25, 100, 300, 1500, 500000]
    # labels = ['<25', '25-100', '100-300','300-1500', '>1500']
    # data['geotype'] = pd.cut(
    #     data['population_density_km2'],
    #     bins=bins,
    #     labels=labels
    # )

    return data


def summarize_data(data):
    """

    """
    #subset desired columns
    data = data[['scenario', 'strategy', 'confidence', 'decile', 'cost_user']]

    #get the median value
    data = data.groupby(['scenario', 'strategy', 'confidence', 'decile'])['cost_user'].median().reset_index()

    data.columns = ['Scenario', 'Strategy', 'Confidence', 'Decile', 'Cost Per User ($)']

    return data


def process_all_regional_data(data):
    """

    """
    data = data[['GID_0','GID_id','GID_level','population','population_km2','area_km2']].copy()

    bins = [-1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 111607]
    labels = ['<20','20-43','43-69','69-109','109-171','171-257','257-367','367-541','541-1104','>1104']

    data['decile'] = pd.cut(
        data['population_km2'],
        bins=bins,
        labels=labels
    )

    return data


def get_costs(data, costs):
    """

    """
    costs = costs.to_dict('records')

    lookup = {}

    scenarios = set()
    strategies = set()
    cis = set()

    for item in costs:

        scenario = item['Scenario']
        strategy = item['Strategy'].replace(' ', '')
        ci = item['Confidence']
        decile = item['Decile']

        handle = '{}_{}_{}_{}'.format(scenario, strategy, ci, decile)

        lookup[handle] = item['Cost Per User ($)']

        scenarios.add(scenario)
        strategies.add(strategy)
        cis.add(ci)

    output = []

    data = data.to_dict('records')

    for scenario in list(scenarios):
        for strategy in list(strategies):
            for ci in list(cis):
                for item in data:

                    handle = '{}_{}_{}_{}'.format(scenario, strategy, ci, item['decile'])

                    cost_per_user = lookup[handle]

                    output.append({
                        'GID_id': item['GID_id'],
                        'GID_level': item['GID_level'],
                        'GID_0': item['GID_0'],
                        'scenario': scenario,
                        'strategy': strategy,
                        'confidence': ci,
                        'population': item['population'],
                        'population_km2': item['population_km2'],
                        'area_km2': item['area_km2'],
                        'decile': item['decile'],
                        'cost_per_user': cost_per_user,
                        'total_cost': item['population'] * cost_per_user,
                    })

    return output


def processing_national_costs(regional_data):
    """

    """
    national_costs = regional_data[[
        'GID_0',
        'scenario', 'strategy', 'confidence',
        'population', 'area_km2',
        'total_cost'
    ]]

    national_costs = national_costs.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum().reset_index()

    national_costs['total_cost'] = national_costs['total_cost'] / 1e9

    national_costs.columns = [
        'Country', 'Scenario', 'Strategy', 'Confidence',
        'Population', 'Area (Km2)', 'Cost ($Bn)'
    ]

    return national_costs


def processing_total_costs(regional_results):
    """

    """
    total_costs = regional_results[[
        'scenario', 'strategy', 'confidence',
        'population', 'area_km2',
        'total_cost'
    ]]

    total_costs = total_costs.groupby([
        'scenario', 'strategy', 'confidence'], as_index=True).sum().reset_index()

    total_costs['total_cost'] = total_costs['total_cost'] / 1e9

    total_costs.columns = [
        'Scenario', 'Strategy', 'Confidence',
        'Population', 'Area (Km2)', 'Cost ($Bn)'
    ]

    return total_costs


if __name__ == '__main__':

    print('Loading PODIS cost estimate data')
    path = os.path.join(RESULTS, 'regional_mno_results_technology_options.csv')
    data = pd.read_csv(path)

    print('Processing PODIS data')
    data = process_data(data)

    print('Defining population density categories')
    data = define_density_categories(data)

    print('Writing regional per user cost data to .csv')
    path = os.path.join(DATA_INTERMEDIATE, 'regional_per_user_cost.csv')
    data.to_csv(path, index=False)

    print('Summarizing data')
    costs = summarize_data(data)

    print('Writing summarized data to .csv')
    path = os.path.join(DATA_INTERMEDIATE, 'median_per_user_cost_by_pop_density.csv')
    costs.to_csv(path, index=False)

    print('Loading regional data by pop density geotype')
    path = os.path.join(DATA_INTERMEDIATE, 'all_regional_data.csv')
    regional_data = pd.read_csv(path)

    print('Processing all regional data')
    regional_data = process_all_regional_data(regional_data)

    print('Combining regional data with costs')
    regional_data = get_costs(regional_data, costs)

    print('Exporting results')
    regional_data = pd.DataFrame(regional_data)
    path = os.path.join(RESULTS, 'regional_cost_estimates.csv')
    regional_data.to_csv(path, index=False)

    print('Processing results data')
    national_costs = processing_national_costs(regional_data)

    print('Exporting national results')
    path = os.path.join(RESULTS, 'national_cost_estimates.csv')
    national_costs.to_csv(path, index=False)

    print('Processing total cost data')
    total_costs = processing_total_costs(regional_data)

    print('Exporting national results')
    path = os.path.join(RESULTS, 'total_cost_estimates.csv')
    total_costs.to_csv(path, index=False)

    print('Complete')
