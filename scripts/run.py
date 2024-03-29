"""
Generate data for modeling.

Written by Ed Oughton.

Winter 2020

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
from write import (define_deciles, #write_mno_demand,
    write_regional_results,
    write_decile_results, write_national_results) #, write_inputs
from user_costs import (process_costs, process_all_regional_data, processing_national_costs,
    processing_decile_costs, processing_total_costs)
from percentages import process_percentages

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'model_results')
PARAMETERS_DIR = os.path.join(BASE_PATH, '..', 'results', 'model_parameters')


def load_regions(iso3, path):
    """
    Load country regions.

    """
    regions = pd.read_csv(path)

    regions['geotype'] = regions.apply(define_geotype, axis=1)

    if len(iso3) <= 3:
        regions['integration'] = 'baseline'
    else:
        regions['integration'] = 'integration'

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


if __name__ == '__main__':

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

    path = os.path.join(DATA_INTERMEDIATE, 'uq_inputs.csv')
    parameter_set = pd.read_csv(path)

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

    for idx, parameters in parameter_set.iterrows():

        # if idx == 1:
        #     break

        regional_annual_demand = []
        regional_results = []
        regional_cost_structure = []

        for country in countries:#[:1]:

            iso3 = country['iso3']

            # print('Working on {}'.format(iso3))

            country_parameters = COUNTRY_PARAMETERS[iso3]

            folder = os.path.join(DATA_RAW, 'clustering')
            filename = 'data_clustering_results.csv'
            country['cluster'] = load_cluster(os.path.join(folder, filename), iso3)

            folder = os.path.join(DATA_INTERMEDIATE, iso3)
            filename = 'core_lut.csv'
            core_lut = load_core_lut(os.path.join(folder, filename))

            print('Working on {}, {}, {}, {}, in {}'.format(
                parameters['decision_option'],
                parameters['strategy'],
                parameters['scenario'],
                parameters['input_cost'],
                iso3))

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
            filename = 'subs_forecast.csv'
            path = os.path.join(folder, filename)
            penetration_lut = load_penetration(parameters['scenario'], path)

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'smartphones')
            filename = 'smartphone_forecast.csv'
            path = os.path.join(folder, filename)
            smartphone_lut = load_smartphones(parameters['scenario'], path)

            filename = 'regional_data.csv'
            path = os.path.join(DATA_INTERMEDIATE, iso3, filename)
            data = load_regions(iso3, path)

            data_initial = data.to_dict('records')

            data_demand, annual_demand = estimate_demand(
                data_initial,
                parameters,
                country_parameters,
                TIMESTEPS,
                penetration_lut,
                smartphone_lut
            )

            data_supply = estimate_supply(
                country,
                data_demand,
                lookup,
                parameters,
                country_parameters,
                core_lut
            )

            data_assess = assess(
                country,
                data_supply,
                parameters,
                country_parameters,
                TIMESTEPS
            )

            final_results = allocate_deciles(data_assess)

            regional_annual_demand = regional_annual_demand + annual_demand
            regional_results = regional_results + final_results

            # filename = 'regional_annual_demand_{}.csv'.format(parameters['decision_option'])
            # path = os.path.join(OUTPUT, filename)
            # write_mno_demand(regional_annual_demand, OUTPUT, parameters['decision_option'], path)

            all_results = all_results + regional_results

        handle = "{}_{}_{}".format(
            parameters['scenario'],
            parameters['strategy'],
            parameters['iteration']
        )

        path = os.path.join(OUTPUT, 'regional_results')
        write_regional_results(regional_results, path, handle)

        path = os.path.join(OUTPUT, 'decile_results')
        write_decile_results(regional_results, path, handle)

        path = os.path.join(OUTPUT, 'national_results')
        write_national_results(regional_results, path, handle)

    process_costs()
    process_all_regional_data()
    processing_national_costs()
    processing_decile_costs()
    processing_total_costs()

    process_percentages()

    print('Completed model run')
