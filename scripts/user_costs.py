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


def process_data(data, capacity):
    """
    Add any necessary variables and rename scenarios and strategies.

    Parameters
    ----------
    data : pandas df
        All model results.
    capacity : int
        The capacity we wish to process.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    #subset based on defined capacity
    data = data[data['scenario'].str.contains(str(capacity))].reset_index()

    # Add population density
    data['population_density_km2'] = data['population'] / data['area_km2']

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

    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=["private_cost_per_network_user"], how="all")
    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=["private_cost_per_smartphone_user"], how="all")
    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=["social_cost_per_network_user"], how="all")
    data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=["social_cost_per_smartphone_user"], how="all")

    data['private_cost_per_user'] = round(data['private_cost_per_network_user'])
    data['social_cost_per_user'] = round(data['social_cost_per_network_user'])

    bins = [-1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 111607]
    labels = ['<20','20-43','43-69','69-109','109-171','171-257','257-367','367-541','541-1104','>1104']

    data['decile'] = pd.cut(
        data['population_density_km2'],
        bins=bins,
        labels=labels
    )

    return data


def summarize_data(data, capacity):
    """
    Summarize the data by taking the median costs across the
    scenarios and strategies.

    Parameters
    ----------
    data : pandas df
        All model results.
    capacity : int
        The capacity we wish to process.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    #subset desired columns
    data = data[[
        'scenario', 'strategy', 'confidence', 'decile',
        'private_cost_per_user', 'social_cost_per_user',
        'government_cost_per_network_user'
    ]]

    #get the median value
    data = data.groupby(['scenario', 'strategy', 'confidence', 'decile'])[
        [
            'private_cost_per_user',
            'government_cost_per_network_user',
            'social_cost_per_user',
            ]].median().reset_index()

    data.columns = [
        'Scenario', 'Strategy', 'Confidence', 'Decile',
        'Private Cost Per User ($USD)', 'Government Cost Per User ($USD)',
        'Social Cost Per User ($USD)'
    ]

    return data


def process_all_regional_data(data):
    """
    Add any necessary variables and rename scenarios
    and strategies.

    Parameters
    ----------
    data : pandas df
        All model results.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data = data[[
        'GID_0','GID_id','GID_level','population',
        'population_km2','area_km2'
    ]].copy()

    bins = [
        -1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 111607
    ]

    labels = [
        '<20','20-43','43-69','69-109','109-171','171-257',
        '257-367','367-541','541-1104','>1104'
    ]

    data['decile'] = pd.cut(
        data['population_km2'],
        bins=bins,
        labels=labels
    )

    return data


def get_costs(data, costs):
    """
    Combining the regional data and cost data across
    the scenarios and strategies.

    Parameters
    ----------
    data : pandas df
        All regional data created in scripts/uba_prep.py.
    costs : pandas df
        All cost results.

    Returns
    -------
    output : list of dicts
        All combined data.

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

        lookup[handle] = {
            'Private Cost Per User ($USD)': item['Private Cost Per User ($USD)'],
            'Government Cost Per User ($USD)': item['Government Cost Per User ($USD)'],
            # 'Social Cost Per User ($USD)': item['Social Cost Per User ($USD)'],
        }

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

                    private_cost_per_user = lookup[handle]['Private Cost Per User ($USD)']
                    govt_cost_per_user = lookup[handle]['Government Cost Per User ($USD)']
                    # social_cost_per_user = lookup[handle]['Social Cost Per User ($USD)']

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
                        'private_cost_per_user': private_cost_per_user,
                        'govt_cost_per_user': govt_cost_per_user,
                        'social_cost_per_user': private_cost_per_user + govt_cost_per_user,
                        'total_private_cost': item['population'] * private_cost_per_user,
                        'total_government_cost': item['population'] * govt_cost_per_user,
                        'total_social_cost': (item['population'] *
                        (private_cost_per_user + govt_cost_per_user)),
                    })

    return output


def processing_national_costs(regional_data, capacity):
    """
    Processing national costs using regional data.

    Parameters
    ----------
    regional_data : pandas df
        All regional data created in scripts/uba_prep.py.
    capacity : int
        The capacity we wish to process.

    Returns
    -------
    output : list of dicts
        All combined data.

    """
    #subset for desired capacity
    regional_data = regional_data[regional_data['scenario'].str.contains(
        str(capacity))].reset_index()

    national_costs = regional_data[[
        'GID_0', 'scenario', 'strategy', 'confidence',
        'population', 'area_km2', 'total_private_cost',
        'total_government_cost', 'total_social_cost'
    ]]

    national_costs = national_costs.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum().reset_index()

    national_costs['total_private_cost'] = national_costs['total_private_cost'] / 1e9
    national_costs['total_government_cost'] = national_costs['total_government_cost'] / 1e9
    national_costs['total_social_cost'] = national_costs['total_social_cost'] / 1e9

    national_costs.columns = [
        'Country', 'Scenario', 'Strategy', 'Confidence',
        'Population', 'Area (Km2)', 'Private Cost ($Bn)',
        'Government Cost ($Bn)', 'Social Cost ($Bn)'
    ]

    return national_costs


def processing_total_costs(regional_results):
    """

    """
    total_costs = regional_results[[
        'scenario', 'strategy', 'confidence', 'population',
        'area_km2', 'total_private_cost',
        'total_government_cost', 'total_social_cost'
    ]]

    total_costs = total_costs.groupby([
        'scenario', 'strategy', 'confidence'], as_index=True).sum().reset_index()

    total_costs['total_private_cost'] = total_costs['total_private_cost'] / 1e9
    total_costs['total_government_cost'] = total_costs['total_government_cost'] / 1e9
    total_costs['total_social_cost'] = total_costs['total_social_cost'] / 1e9

    total_costs.columns = [
        'Scenario', 'Strategy', 'Confidence',
        'Population', 'Area (Km2)', 'Private Cost ($Bn)',
        'Government Cost ($Bn)', 'Social Cost ($Bn)'
    ]

    return total_costs


if __name__ == '__main__':

    capacities = [
        10,
        2
    ]

    for capacity in capacities:

        print('Working on {} Mbps per user'.format(capacity))

        #Loading PODIS cost estimate data
        path = os.path.join(RESULTS, 'regional_mno_cost_results_technology_options.csv')
        data = pd.read_csv(path)

        #Processing PODIS data
        data = process_data(data, capacity)

        #Writing regional per user cost data to .csv
        filename = 'regional_per_user_cost_{}.csv'.format(capacity)
        path = os.path.join(DATA_INTERMEDIATE, filename)
        data.to_csv(path, index=False)

        #Summarizing data
        costs = summarize_data(data, capacity)

        #Writing summarized data to .csv
        filename = 'median_per_user_cost_by_pop_density_{}.csv'.format(capacity)
        path = os.path.join(DATA_INTERMEDIATE, filename)
        costs.to_csv(path, index=False)

        #Loading regional data by pop density geotype
        path = os.path.join(DATA_INTERMEDIATE, 'all_regional_data.csv')
        regional_data = pd.read_csv(path)

        #Processing all regional data
        regional_data = process_all_regional_data(regional_data)

        #Combining regional data with costs
        regional_data = get_costs(regional_data, costs)

        #Exporting results
        regional_data = pd.DataFrame(regional_data)
        filename = 'regional_cost_estimates_{}.csv'.format(capacity)
        path = os.path.join(RESULTS, filename)
        regional_data.to_csv(path, index=False)

        #Processing results data
        national_costs = processing_national_costs(regional_data, capacity)

        #Exporting national results
        filename = 'national_cost_estimates_{}.csv'.format(capacity)
        path = os.path.join(RESULTS, filename)
        national_costs.to_csv(path, index=False)

        #Processing total cost data
        total_costs = processing_total_costs(regional_data)

        #Exporting national results
        filename = 'total_cost_estimates_{}.csv'.format(capacity)
        path = os.path.join(RESULTS, filename)
        total_costs.to_csv(path, index=False)

    print('-- Processing completed')
