"""
Generate sensitivity data for modeling.

Written by Ed Oughton.

October 2021

"""
import os
import csv
import configparser
import pandas as pd
import geopandas
from collections import OrderedDict

from options import OPTIONS, COUNTRY_PARAMETERS
from podis.demand import estimate_demand
from podis.supply import estimate_supply
from podis.assess import assess
from write import define_deciles, write_mno_demand, write_results, write_inputs
from sensitivity_options import generate_sensitivity_options

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'sensitivity_analysis')
# PARAMETERS = os.path.join(BASE_PATH, '..', 'results', 'model_parameters')


def load_regions(iso3, path):
    """
    Load country regions.

    """
    regions = pd.read_csv(path)

    regions['geotype'] = regions.apply(define_geotype, axis=1)

    return regions


def define_geotype(x):
    """
    Allocate geotype given a specific population density.

    """
    if x['population_km2'] > 5000:
        return 'urban'
    elif x['population_km2'] > 1500:
        return 'suburban 1'
    elif x['population_km2'] > 1000:
        return 'suburban 2'
    elif x['population_km2'] > 500:
        return 'rural 1'
    elif x['population_km2'] > 100:
        return 'rural 2'
    elif x['population_km2'] > 50:
        return 'rural 3'
    elif x['population_km2'] > 10:
        return 'rural 4'
    else:
        return 'rural 5'


def read_capacity_lookup(path):
    """

    """
    capacity_lookup_table = {}

    with open(path, 'r') as capacity_lookup_file:
        reader = csv.DictReader(capacity_lookup_file)
        for row in reader:

            if float(row["capacity_mbps_km2"]) <= 0:
                continue
            environment = row["environment"].lower()
            ant_type = row["ant_type"]
            frequency_GHz = str(int(float(row["frequency_GHz"]) * 1e3))
            generation = str(row["generation"])
            ci = str(row['confidence_interval'])

            if (environment, ant_type, frequency_GHz, generation, ci) \
                not in capacity_lookup_table:
                capacity_lookup_table[(
                    environment, ant_type, frequency_GHz, generation, ci)
                    ] = []

            capacity_lookup_table[(
                environment,
                ant_type,
                frequency_GHz,
                generation,
                ci)].append((
                    float(row["sites_per_km2"]),
                    float(row["capacity_mbps_km2"])
                ))

        for key, value_list in capacity_lookup_table.items():
            value_list.sort(key=lambda tup: tup[0])

    return capacity_lookup_table


def lookup_cost(lookup, strategy, environment):
    """
    Find cost of network.

    """
    if (strategy, environment) not in lookup:
        raise KeyError("Combination %s not found in lookup table",
                       (strategy, environment))

    density_capacities = lookup[
        (strategy, environment)
    ]

    return density_capacities


def find_country_list(continent_list):
    """

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_processed)

    subset = countries.loc[countries['continent'].isin(continent_list)]

    country_list = []
    country_regional_levels = []

    for name in subset.GID_0.unique():

        country_list.append(name)

        if name in ['ESH', 'LBY', 'LSO'] :
            regional_level =  1
        else:
            regional_level = 2

        country_regional_levels.append({
            'country': name,
            'regional_level': regional_level,
        })

    return country_list, country_regional_levels


def load_cluster(path, iso3):
    """
    Load cluster number. You need to make sure the
    R clustering script (podis/vis/clustering/clustering.r)
    has been run first.

    """
    output = {}

    if len(iso3) <= 3:
        with open(path, 'r') as source:
            reader = csv.DictReader(source)
            for row in reader:
                if row['ISO_3digit'] == iso3:
                    output[iso3] = row['cluster']

    if len(iso3) > 3:

        list_of_country_codes = []
        country_codes = iso3.split('-')
        list_of_country_codes.extend(country_codes)

        for item in list_of_country_codes:
            with open(path, 'r') as source:
                reader = csv.DictReader(source)

                for row in reader:
                    if row['ISO_3digit'] == item:
                        output[item] = row['cluster']

    return output


def load_penetration(scenario, path):
    """
    Load penetration forecast.

    """
    output = {}
    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            if row['scenario'] == scenario.split('_')[0]:
                output[int(row['year'])] = float(row['penetration'])

    return output


def load_smartphones(scenario, path):
    """
    Load phone types forecast. The function either uses the specific data
    for the country being modeled, or data from another country in the same
    cluster. If no data are present for the country of the cluster, it
    defaults to the mean values across all surveyed countries.

    """
    output = {}
    settlement_types = [
        'urban',
        'rural']

    for settlement_type in settlement_types:
        with open(path, 'r') as source:
            reader = csv.DictReader(source)
            intermediate = {}
            for row in reader:
                if row['scenario'] == scenario.split('_')[0]:
                    if settlement_type == row['settlement_type']:
                        intermediate[int(row['year'])] = float(row['penetration'])
            output[settlement_type] = intermediate

    return output


def load_core_lut(path):
    """
    """
    interim = []

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            interim.append({
                'GID_id': row['GID_id'],
                'asset': row['asset'],
                'source': row['source'],
                'value': int(round(float(row['value']))),
            })

    asset_types = [
        'core_edge',
        'core_node',
        'regional_edge',
        'regional_node'
    ]

    output = {}

    for asset_type in asset_types:
        asset_dict = {}
        for row in interim:
            if asset_type == row['asset']:
                combined_key = '{}_{}'.format(row['GID_id'], row['source'])
                asset_dict[combined_key] = row['value']
                output[asset_type] = asset_dict

    return output


def allocate_deciles(data):
    """
    Convert to pandas df, define deciles, and then return as a list of dicts.

    """
    data = pd.DataFrame(data)

    data = define_deciles(data)

    data = data.to_dict('records')

    return data


def generate_costs(costs, cost_input_change):
    """

    """
    if cost_input_change == 100:
        return costs
    else:

        output = {}

        for key, item in costs.items():
            output[key] = item * (cost_input_change / 100)

    return output




if __name__ == '__main__':

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

    COSTS = {
        #all costs in $USD
        'equipment_capex': 40000,
        'site_build_capex': 30000,
        'installation_capex': 30000,
        'operation_and_maintenance_opex': 7400,
        'power_opex': 3000,
        'site_rental_urban_opex': 10000,
        'site_rental_suburban_opex': 5000,
        'site_rental_rural_opex': 3000,
        'fiber_urban_m_capex': 25,
        'fiber_suburban_m_capex': 15,
        'fiber_rural_m_capex': 10,
        'wireless_small_capex': 15000,
        'wireless_medium_capex': 20000,
        'wireless_large_capex': 45000,
        'core_node_epc_capex': 500000,
        'core_edge_capex': 25,
        'regional_node_epc_capex': 200000,
        'regional_edge_capex': 25,
    }

    GLOBAL_PARAMETERS = {
        'overbooking_factor': 20,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'confidence': [50],#[5, 50, 95]
        }

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    lookup = read_capacity_lookup(path)

    # countries, country_regional_levels = find_country_list(['Africa', 'South America'])

    countries = [
        {'iso3': 'CIV', 'iso2': 'CI', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'KEN', 'iso2': 'KE', 'regional_level': 3, 'regional_nodes_level': 2},
        {'iso3': 'MLI', 'iso2': 'ML', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_nodes_level': 2},
        {'iso3': 'TZA', 'iso2': 'TZ', 'regional_level': 2, 'regional_nodes_level': 1},
        {'iso3': 'UGA', 'iso2': 'UG', 'regional_level': 2, 'regional_nodes_level': 2},
        ]

    all_results = []

    decision_option = 'sensitivity_analysis'
    options = generate_sensitivity_options()

    regional_annual_demand = []
    regional_results = []
    regional_cost_structure = []

    for country in countries:#[:1]:

        iso3 = country['iso3']

        print('Working on {}'.format(iso3))

        country_parameters = COUNTRY_PARAMETERS[iso3]

        folder = os.path.join(DATA_RAW, 'clustering')
        filename = 'data_clustering_results.csv'
        country['cluster'] = load_cluster(os.path.join(folder, filename), iso3)

        folder = os.path.join(DATA_INTERMEDIATE, iso3)
        filename = 'core_lut.csv'
        core_lut = load_core_lut(os.path.join(folder, filename))

        for option in options:#[:1]:

            print('Working on {} and {}'.format(option['scenario'], option['strategy']))

            confidence_intervals = GLOBAL_PARAMETERS['confidence']

            GLOBAL_PARAMETERS['overbooking_factor'] = int(option['strategy'].split('_')[7])
            cost_input_change = int(option['strategy'].split('_')[8])

            costs = generate_costs(COSTS, cost_input_change)

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
            filename = 'subs_forecast.csv'
            path = os.path.join(folder, filename)
            penetration_lut = load_penetration(option['scenario'], path)

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'smartphones')
            filename = 'smartphone_forecast.csv'
            path = os.path.join(folder, filename)
            smartphone_lut = load_smartphones(option['scenario'], path)

            filename = 'regional_data.csv'
            path = os.path.join(DATA_INTERMEDIATE, iso3, filename)
            data = load_regions(iso3, path)

            data_initial = data.to_dict('records')

            data_demand, annual_demand = estimate_demand(
                data_initial,
                option,
                GLOBAL_PARAMETERS,
                country_parameters,
                TIMESTEPS,
                penetration_lut,
                smartphone_lut
            )

            data_supply = estimate_supply(
                country,
                data_demand,
                lookup,
                option,
                GLOBAL_PARAMETERS,
                country_parameters,
                costs,
                core_lut,
                confidence_intervals[0]
            )

            data_assess = assess(
                country,
                data_supply,
                option,
                GLOBAL_PARAMETERS,
                country_parameters,
                TIMESTEPS
            )

            final_results = allocate_deciles(data_assess)

            regional_annual_demand = regional_annual_demand + annual_demand
            regional_results = regional_results + final_results

        filename = 'regional_annual_demand_{}.csv'.format(decision_option)
        path = os.path.join(OUTPUT, filename)
        write_mno_demand(regional_annual_demand, OUTPUT, decision_option, path)

        all_results = all_results + regional_results

        # write_inputs(PARAMETERS, country, country_parameters,
        #     GLOBAL_PARAMETERS, costs, decision_option)

    write_results(regional_results, OUTPUT, decision_option)

    print('Completed model run')
