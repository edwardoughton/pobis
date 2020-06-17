"""
Get incremental cost per user.

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
from ictp4d.demand import estimate_demand
from ictp4d.supply import estimate_supply
from ictp4d.assess import assess

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


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
    R clustering script (pytal/vis/clustering/clustering.r)
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


def load_penetration(timesteps):
    """
    Load penetration forecast.

    """
    output = {}

    for year in timesteps:
        output[int(year)] = 100

    return output


def load_smartphones(country, path):
    """
    Load phone types forecast. The function either uses the specific data
    for the country being modeled, or data from another country in the same
    cluster. If no data are present for the country of the cluster, it
    defaults to the mean values across all surveyed countries.

    """
    cluster_dict = country['cluster']

    countries = set()

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            countries.add(row['iso3'])

    output = {}
    all_data = {
        'urban': [],
        'rural': []
    }

    for iso3, cluster in cluster_dict.items():
        interm = {}
        with open(path, 'r') as source:
            reader = csv.DictReader(source)
            for row in reader:
                if iso3 in list(countries):
                    if row['iso3'] == iso3:
                        settlement = row['Settlement'].lower()
                        interm[settlement] = {
                            'basic': float(row['Basic']) / 100,
                            'feature': float(row['Feature']) / 100,
                            'smartphone': float(row['Smartphone']) / 100,
                        }
                elif row['cluster'] == cluster:
                    settlement = row['Settlement'].lower()
                    interm[settlement] = {
                        'basic': float(row['Basic']) / 100,
                        'feature': float(row['Feature']) / 100,
                        'smartphone': float(row['Smartphone']) / 100,
                    }
                else:
                    settlement = row['Settlement'].lower()
                    all_data[settlement].append(float(row['Smartphone']) / 100)
        output[iso3] = interm

        if len(output) == 0:
            output = {
                'urban': {'smartphone': sum(all_data['urban']) / len(all_data['urban'])},
                'rural': {'smartphone': sum(all_data['rural']) / len(all_data['rural'])},
            }

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


def define_deciles(regions):

    regions = regions.sort_values(by='population_km2', ascending=True)

    regions['decile'] = regions.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).population_km2.apply( #cost_per_sp_user
            pd.qcut, q=11, precision=0,
            labels=[100,90,80,70,60,50,40,30,20,10,0], duplicates='drop') #[0,10,20,30,40,50,60,70,80,90,100]

    return regions


def write_results(regional_results, folder, metric):
    """
    Write all results.
    """
    print('Writing national results')
    national_results = pd.DataFrame(regional_results)
    national_results = national_results[[
        'increment', 'GID_0', 'scenario',
        'strategy', 'confidence',
        'population', 'area_km2',
        'phones_on_network',
        'smartphones_on_network',
        'sites_estimated_total',
        'upgraded_sites', 'new_sites',
        'total_revenue', 'total_cost',
    ]]

    national_results = national_results.groupby([
        'increment', 'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    national_results['cost_per_network_user'] = (
        national_results['total_cost'] / national_results['phones_on_network'])

    national_results = national_results.round(0)

    path = os.path.join(folder,'national_results_{}.csv'.format(metric))
    national_results.to_csv(path, index=True)

    print('Writing general decile results')
    decile_results = pd.DataFrame(regional_results)
    decile_results = decile_results[[
        'increment', 'GID_0', 'scenario',
        'decile', 'strategy', 'confidence',
        'population', 'area_km2',
        'phones_on_network',
        'smartphones_on_network',
        'sites_estimated_total',
        'upgraded_sites', 'new_sites',
        'total_revenue', 'total_cost',
    ]]

    decile_results = decile_results.groupby([
        'increment', 'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()

    decile_results['population_km2'] = (
        decile_results['population'] / decile_results['area_km2'])
    decile_results['sites_estimated_total_km2'] = (
        decile_results['sites_estimated_total'] / decile_results['area_km2'])
    decile_results['cost_per_network_user'] = (
        decile_results['total_cost'] / decile_results['phones_on_network'])

    path = os.path.join(folder,'decile_results_{}.csv'.format(metric))
    decile_results.to_csv(path, index=True)


def allocate_deciles(data):
    """
    Convert to pandas df, define deciles, and then return as a list of dicts.

    """
    data = pd.DataFrame(data)

    data = define_deciles(data)

    data = data.to_dict('records')

    return data


if __name__ == '__main__':

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

    COSTS = {
        #all costs in $USD
        'single_sector_antenna': 1500,
        'single_remote_radio_unit': 4000,
        'io_fronthaul': 1500,
        'processing': 1500,
        'io_s1_x2': 1500,
        'control_unit': 1500,
        'cooling_fans': 250,
        'distributed_power_supply_converter': 250,
        'power_generator_battery_system': 5000,
        'bbu_cabinet': 500,
        'rack': 500,
        'tower': 10000,
        'civil_materials': 5000,
        'transportation': 5000,
        'installation': 5000,
        'site_rental_urban': 9600,
        'site_rental_suburban': 4000,
        'site_rental_rural': 2000,
        'router': 2000,
        'microwave_small': 10000,
        'microwave_medium': 20000,
        'microwave_large': 40000,
        'fiber_urban_m': 25,
        'fiber_suburban_m': 15,
        'fiber_rural_m': 10,
        'core_node_epc': 200000,
        'core_edge': 10,
        'regional_node_epc': 100000,
        'regional_edge': 5,
        'per_site_spectrum_acquisition_cost': 500,
        'per_site_administration_cost': 500,
        'per_site_facilities_cost': 500,
    }

    GLOBAL_PARAMETERS = {
        'overbooking_factor': 20,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'sectorization': 3,
        'confidence': [50], #[5, 50, 95],
        'regional_integration_factor': 20,
        }

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    lookup = read_capacity_lookup(path)

    countries = [
        {'iso3': 'SEN', 'iso2': 'SN', 'regional_level': 2, 'regional_nodes_level': 2},
        ]

    scenarios = [
        'low',
        'baseline',
        'high'
    ]

    option = {
        'scenario': 'low_2_2_2',
        'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline_baseline',
    }

    regional_results = []

    for country in countries:#[:1]:

        iso3 = country['iso3']

        print('Working on {}'.format(iso3))

        country_parameters = COUNTRY_PARAMETERS[iso3]

        country_parameters['networks']['baseline_urban'] = 1
        country_parameters['networks']['baseline_suburban'] = 1
        country_parameters['networks']['baseline_rural'] = 1

        smartphone_lut = {
            country['iso3']: {
                'urban': {'smartphone': 1},
                'rural': {'smartphone': 1},
            }
        }

        folder = os.path.join(DATA_INTERMEDIATE, iso3)
        filename = 'core_lut.csv'
        core_lut = load_core_lut(os.path.join(folder, filename))

        confidence_intervals = GLOBAL_PARAMETERS['confidence']

        penetration_lut = load_penetration(TIMESTEPS)

        ci = 50

        path = os.path.join(DATA_INTERMEDIATE, iso3, 'regional_data.csv')
        data = load_regions(iso3, path)

        data_initial = data.to_dict('records')

        increments = 10

        for i in range (1, increments + 1):

            # if i > 4:
            #     continue

            print('Working on increment {}'.format(i))

            data_fraction = []

            for region in data_initial:#[:1]:

                increment = region['population'] / (increments - 1)

                if i == 1:
                    population = 1
                else:
                    population = increment * (i - 1)

                data_fraction.append({
                    'increment': i,
                    'GID_0': region['GID_0'],
                    'GID_id': region['GID_id'],
                    'GID_level': region['GID_level'],
                    'mean_luminosity_km2': region['mean_luminosity_km2'],
                    'population': population,
                    'area_km2': region['area_km2'],
                    'population_km2': population / region['area_km2'],
                    'coverage_GSM_percent': region['coverage_GSM_percent'],
                    'coverage_3G_percent': region['coverage_3G_percent'],
                    'coverage_4G_percent': region['coverage_4G_percent'],
                    'sites_estimated_total': region['sites_estimated_total'],
                    'sites_estimated_km2': region['sites_estimated_km2'],
                    'sites_3G': region['sites_3G'],
                    'sites_4G': region['sites_4G'],
                    'backhaul_fiber': region['backhaul_fiber'],
                    'backhaul_copper': region['backhaul_copper'],
                    'backhaul_microwave': region['backhaul_microwave'],
                    'backhaul_satellite': region['backhaul_satellite'],
                    'geotype': region['geotype'],
                    'integration': region['integration'],
                })

            data_demand = estimate_demand(
                data_fraction,
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
                COSTS,
                core_lut,
                ci
            )

            data_assess = assess(
                country,
                data_supply,
                option,
                GLOBAL_PARAMETERS,
                country_parameters,
            )

            final_results = allocate_deciles(data_assess)

            regional_results = regional_results + final_results

    folder = os.path.join(BASE_PATH, '..', 'results')
    write_results(regional_results, folder, 'inc_cost')

    print('Completed model run')
