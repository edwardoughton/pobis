"""
Estimate the costs of upgrades.

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

DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
RESULTS = os.path.join(BASE_PATH, '..', 'results', 'model_results')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'user_costs')


def process_costs():
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
    data = []

    path = os.path.join(RESULTS, 'regional_results')

    for filename in os.listdir(path):

        # if not capacity in filename:
        #     continue

        if not 'regional_mno_cost_' in filename:
            continue

        filepath = os.path.join(path, filename)

        sample = pd.read_csv(filepath)

        # Add population density
        sample['population_density_km2'] = sample['population'] / sample['area_km2']

        sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=["private_cost_per_network_user"], how="all")
        sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=["private_cost_per_smartphone_user"], how="all")
        sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=["financial_cost_per_network_user"], how="all")
        sample = sample.replace([np.inf, -np.inf], np.nan).dropna(subset=["financial_cost_per_smartphone_user"], how="all")

        sample['private_cost_per_user'] = round(sample['private_cost_per_network_user'])
        sample['financial_cost_per_user'] = round(sample['financial_cost_per_network_user'])

        bins = [-1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 111607] #-1,
        labels = ['<20','20-43','43-69','69-109','109-171','171-257','257-367','367-541','541-1104','>1104']

        sample['decile'] = pd.cut(
            sample['population_density_km2'],
            bins=bins,
            labels=labels
        )

        sample = sample.to_dict('records')

        data = data + sample

    data = pd.DataFrame(data)

    #subset desired columns
    data = data[[
        'scenario', 'strategy', 'decile', 'confidence', 'input_cost',
        'private_cost_per_user', 'financial_cost_per_user',
        'government_cost_per_network_user'
    ]]

    data = data.groupby(['scenario', 'strategy', 'confidence', 'decile', 'input_cost'], as_index=False).agg(
            private_cost_per_user_mean = ('private_cost_per_user','mean'),
            government_cost_per_network_user_mean = ('government_cost_per_network_user','mean'),
            financial_cost_per_user_mean = ('financial_cost_per_user','mean'),
            # private_cost_per_user_median = ('private_cost_per_user','median'),
            # government_cost_per_network_user = ('government_cost_per_network_user','median'),
            # financial_cost_per_user = ('financial_cost_per_user','median'),
        )

    data.columns = [
        'Scenario', 'Strategy', 'Confidence', 'Decile', 'Input Cost',
        'private_mean_cpu',
        'govt_mean_cpu',
        'financial_mean_cpu'
    ]

    path = os.path.join(OUTPUT, 'decile_user_costs.csv')
    data.to_csv(path, index=False)

    return


def process_all_regional_data():
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
    #Loading regional data by pop density geotype
    filename = 'all_regional_data.csv'
    path = os.path.join(DATA_INTERMEDIATE, filename)
    data = pd.read_csv(path)

    data = data[[
        'GID_0','GID_id','GID_level',
        'population',
        'population_km2',
        'area_km2',
    ]].copy()

    bins = [-1, 20, 43, 69, 109, 171, 257, 367, 541, 1104, 111607] #-1,
    labels = ['<20','20-43','43-69','69-109','109-171','171-257','257-367','367-541','541-1104','>1104']

    data['decile'] = pd.cut(
        data['population_km2'],
        bins=bins,
        labels=labels
    )

    path = os.path.join(OUTPUT, 'decile_user_costs.csv')
    costs = pd.read_csv(path)

    costs = costs.to_dict('records')

    lookup = {}

    scenarios = set()
    strategies = set()
    cis = set()
    input_costs = set()

    for item in costs:

        scenario = item['Scenario']
        strategy = item['Strategy'].replace(' ', '')
        ci = item['Confidence']
        decile = item['Decile']
        input_cost = item['Input Cost']

        handle = '{}_{}_{}_{}_{}'.format(scenario, strategy, ci, decile, input_cost)

        lookup[handle] = {
            'Private Cost Per User ($USD)': item['private_mean_cpu'],
            'Government Cost Per User ($USD)': item['govt_mean_cpu'],
        }

        scenarios.add(scenario)
        strategies.add(strategy)
        cis.add(ci)
        input_costs.add(input_cost)

    output = []

    data = data.to_dict('records')

    for scenario in list(scenarios):
        for strategy in list(strategies):
            for ci in list(cis):
                for input_cost in input_costs:
                    for item in data:

                        handle = '{}_{}_{}_{}_{}'.format(
                            scenario,
                            strategy,
                            ci,
                            item['decile'],
                            input_cost
                        )

                        private_cost_per_user = lookup[handle]['Private Cost Per User ($USD)']
                        govt_cost_per_user = lookup[handle]['Government Cost Per User ($USD)']

                        output.append({
                            'GID_id': item['GID_id'],
                            'GID_level': item['GID_level'],
                            'GID_0': item['GID_0'],
                            'scenario': scenario,
                            'strategy': strategy,
                            'confidence': ci,
                            'input_cost': input_cost,
                            'population': item['population'],
                            'population_km2': item['population_km2'],
                            'area_km2': item['area_km2'],
                            'decile': item['decile'],
                            'private_cost_per_user': private_cost_per_user,
                            'govt_cost_per_user': govt_cost_per_user,
                            'financial_cost_per_user': private_cost_per_user + govt_cost_per_user,
                            'total_private_cost': item['population'] * private_cost_per_user,
                            'total_government_cost': item['population'] * govt_cost_per_user,
                            'total_financial_cost': (item['population'] *
                            (private_cost_per_user + govt_cost_per_user)),
                        })

    output = pd.DataFrame(output)

    path = os.path.join(OUTPUT, 'user_cost_estimates.csv')
    output.to_csv(path, index=False)

    return output


def processing_national_costs():
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
    path = os.path.join(OUTPUT, 'user_cost_estimates.csv')
    data = pd.read_csv(path)

    national_costs = data[[
        'GID_0', 'scenario', 'strategy', 'confidence', 'input_cost',
        'population', 'area_km2', 'total_private_cost',
        'total_government_cost', 'total_financial_cost'
    ]]

    national_costs = national_costs.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'input_cost'], as_index=True).sum().reset_index()

    national_costs['total_private_cost'] = national_costs['total_private_cost'] / 1e9
    national_costs['total_government_cost'] = national_costs['total_government_cost'] / 1e9
    national_costs['total_financial_cost'] = national_costs['total_financial_cost'] / 1e9

    path = os.path.join(OUTPUT, 'national_cost_estimates.csv')
    national_costs.to_csv(path, index=False)

    return


def processing_decile_costs():
    """

    """
    path = os.path.join(OUTPUT, 'user_cost_estimates.csv')
    data = pd.read_csv(path)

    decile_costs = data[[
        'scenario', 'strategy', 'confidence', 'decile', 'input_cost',
        'population', 'area_km2', 'total_private_cost',
        'total_government_cost', 'total_financial_cost'
    ]]

    decile_costs = decile_costs.groupby([
        'scenario', 'strategy', 'confidence', 'decile','input_cost'], as_index=True).sum().reset_index()

    decile_costs['total_private_cost'] = decile_costs['total_private_cost'] / 1e9
    decile_costs['total_government_cost'] = decile_costs['total_government_cost'] / 1e9
    decile_costs['total_financial_cost'] = decile_costs['total_financial_cost'] / 1e9

    path = os.path.join(OUTPUT, 'decile_cost_estimates.csv')
    decile_costs.to_csv(path, index=False)

    return


def processing_total_costs():
    """

    """
    path = os.path.join(OUTPUT, 'user_cost_estimates.csv')
    data = pd.read_csv(path)

    total_costs = data[[
        'scenario', 'strategy', 'confidence', 'input_cost', 'population',
        'area_km2', 'total_private_cost',
        'total_government_cost', 'total_financial_cost'
    ]]

    total_costs = total_costs.groupby([
        'scenario', 'strategy', 'confidence', 'input_cost'], as_index=True).sum().reset_index()

    total_costs['total_private_cost'] = total_costs['total_private_cost'] / 1e9
    total_costs['total_government_cost'] = total_costs['total_government_cost'] / 1e9
    total_costs['total_financial_cost'] = total_costs['total_financial_cost'] / 1e9

    path = os.path.join(OUTPUT, 'total_cost_estimates.csv')
    total_costs.to_csv(path, index=False)

    return total_costs


def process_total_cost_data(data, capacity):
    """
    Process total cost data.

    Parameters
    ----------
    data : pandas df
        Data to be processed.
    capacity : int
        The capacity to be processed.

    Returns
    -------
    data : pandas df
        Processed data.

    """
    data = data[['Scenario', 'Strategy', 'Confidence',
                'Financial Cost ($Bn)']].copy()

    baseline = data.loc[data['Strategy'] == '4G(W)']

    data = pd.merge(data, baseline,
                how='left',
                left_on=['Scenario', 'Confidence'],
                right_on = ['Scenario', 'Confidence']
            )

    data['perc_against_4G_W'] = ((abs(data['Financial Cost ($Bn)_x'] -
                                    data['Financial Cost ($Bn)_y'])) /
                                    data['Financial Cost ($Bn)_x']) * 100

    data['perc_against_4G_W'] = round(data['perc_against_4G_W'], 1)

    return data


if __name__ == '__main__':

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    process_costs()
    process_all_regional_data()
    processing_national_costs()
    processing_decile_costs()
    processing_total_costs()
