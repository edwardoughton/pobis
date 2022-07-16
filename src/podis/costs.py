"""
Cost module
Author: Edward Oughton
Date: April 2019

Based off the repo pytal:
https://github.com/edwardoughton/pytal

"""
import math
from itertools import tee
import collections, functools, operator

def find_network_cost(region, parameters,
    country_parameters, core_lut):
    """
    Calculates the annual total cost using capex and opex.

    Parameters
    ----------
    region : dict
        The region being assessed and all associated parameters.
    parameters : dict
        Contains all parameters.
    country_parameters :
        Contains all country parameters.
    backhaul_lut : dict
        Backhaul distance by region.

    Returns
    -------
    output : list of dicts
        Contains a list of costs, with affliated discounted capex and
        opex costs.

    """
    strategy = parameters['strategy']
    generation = strategy.split('_')[0]

    new_sites = region['new_mno_sites']
    upgraded_sites = region['upgraded_mno_sites']
    all_sites = new_sites + upgraded_sites

    new_backhaul = region['backhaul_new']

    regional_asset_cost = []

    for i in range(1, int(all_sites) + 1):

        if i <= upgraded_sites and generation == '3G':

            cost_structure = upgrade_to_3g(region, strategy,
                parameters, core_lut, country_parameters)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost, cost_by_asset = calc_costs(region, strategy, cost_structure,
                backhaul_quant, parameters, country_parameters)

            regional_asset_cost.append(cost_by_asset)

        if i <= upgraded_sites and generation == '4G':

            cost_structure = upgrade_to_4g(region,strategy,
                parameters, core_lut, country_parameters, )

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost, cost_by_asset = calc_costs(region, strategy, cost_structure,
                backhaul_quant, parameters, country_parameters)

            regional_asset_cost.append(cost_by_asset)


        if i > upgraded_sites and generation == '3G':

            cost_structure = greenfield_3g(region, strategy,
                parameters, core_lut, country_parameters)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost, cost_by_asset = calc_costs(region, strategy, cost_structure,
                backhaul_quant, parameters, country_parameters)

            regional_asset_cost.append(cost_by_asset)


        if i > upgraded_sites and generation == '4G':

            cost_structure = greenfield_4g(region, strategy,
                parameters, core_lut, country_parameters)

            backhaul_quant = backhaul_quantity(i, new_backhaul)

            total_cost, cost_by_asset = calc_costs(region, strategy, cost_structure,
                backhaul_quant, parameters, country_parameters)

            regional_asset_cost.append(cost_by_asset)


    counter = collections.Counter()
    for d in regional_asset_cost:
        counter.update(d)
    all_costs = dict(counter)

    capex = 0
    opex = 0
    network_cost = 0
    for k, v in all_costs.items():

        region[k] = v
        network_cost += v

        cost_type = k.rsplit('_')[-1]

        if cost_type == 'capex':
            capex += v
        elif cost_type == 'opex':
            opex += v
        else:
            print('Did not recognize cost type')

    region['mno_network_cost'] = network_cost
    region['mno_network_capex'] = capex
    region['mno_network_opex'] = opex

    return region


def backhaul_quantity(i, new_backhaul):
    if i <= new_backhaul:
        return 1
    else:
        return 0


def upgrade_to_3g(region, strategy, parameters,
    core_lut, country_parameters):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.
    '4G_epc_wireless_moran_baseline_baseline_baseline_baseline',
    """
    backhaul = '{}_backhaul'.format(strategy.split('_')[2])
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    net_handle = 'baseline' + '_' + geotype
    networks = country_parameters['networks'][net_handle]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    core_edge_capex = core_capex(region, 'core_edge', parameters, core_lut, strategy, country_parameters)
    core_node_capex = core_capex(region, 'core_node', parameters, core_lut, strategy, country_parameters)
    regional_edge_capex = regional_net_capex(region, 'regional_edge', parameters, core_lut, strategy, country_parameters)
    regional_node_capex = regional_net_capex(region, 'regional_node', parameters, core_lut, strategy, country_parameters)

    ###provides a single year of costs for the first year of assessment
    assets = {
        'equipment_capex': parameters['equipment_capex'],
        'installation_capex': parameters['installation_capex'],
        'site_rental_opex': parameters['site_rental_{}_opex'.format(geotype)],
        'operation_and_maintenance_opex': parameters['operation_and_maintenance_opex'],
        'power_opex': parameters['power_opex'],
        'backhaul_capex': get_backhaul_capex(region, backhaul, parameters, core_lut),
        'backhaul_opex': 0,
        'core_edge_capex': core_edge_capex,
        'core_node_capex': core_node_capex,
        'regional_edge_capex': regional_edge_capex,
        'regional_node_capex': regional_node_capex,
        'core_edge_opex': core_edge_capex * (parameters['opex_percentage_of_capex'] / 100),
        'core_node_opex': core_node_capex * (parameters['opex_percentage_of_capex'] / 100),
        'regional_edge_opex': regional_edge_capex * (parameters['opex_percentage_of_capex'] / 100),
        'regional_node_opex': regional_node_capex * (parameters['opex_percentage_of_capex'] / 100),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            if sharing == 'srn':
                if geotype == 'urban' or geotype == 'suburban':
                    cost_structure[key] = value
                else:
                    cost_structure[key] = value / networks
            else:
                cost_structure[key] = value / networks

    return cost_structure


def upgrade_to_4g(region, strategy, parameters,
    core_lut, country_parameters):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    backhaul = '{}_backhaul'.format(strategy.split('_')[2])
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    net_handle = 'baseline' + '_' + geotype
    networks = country_parameters['networks'][net_handle]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    core_edge_capex = core_capex(region, 'core_edge', parameters, core_lut, strategy, country_parameters)
    core_node_capex = core_capex(region, 'core_node', parameters, core_lut, strategy, country_parameters)
    regional_edge_capex = regional_net_capex(region, 'regional_edge', parameters, core_lut, strategy, country_parameters)
    regional_node_capex = regional_net_capex(region, 'regional_node', parameters, core_lut, strategy, country_parameters)

    ###provides a single year of costs for the first year of assessment
    assets = {
        'equipment_capex': parameters['equipment_capex'],
        'installation_capex': parameters['installation_capex'],
        'site_rental_opex': parameters['site_rental_{}_opex'.format(geotype)],
        'operation_and_maintenance_opex': parameters['operation_and_maintenance_opex'],
        'power_opex': parameters['power_opex'],
        'backhaul_capex': get_backhaul_capex(region, backhaul, parameters, core_lut),
        'backhaul_opex': 0,
        'core_edge_capex': core_edge_capex,
        'core_node_capex': core_node_capex,
        'regional_edge_capex': regional_edge_capex,
        'regional_node_capex': regional_node_capex,
        'core_edge_opex': core_edge_capex * (parameters['opex_percentage_of_capex'] / 100),
        'core_node_opex': core_node_capex * (parameters['opex_percentage_of_capex'] / 100),
        'regional_edge_opex': regional_edge_capex * (parameters['opex_percentage_of_capex'] / 100),
        'regional_node_opex': regional_node_capex * (parameters['opex_percentage_of_capex'] / 100),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            if sharing == 'srn':
                if geotype == 'urban' or geotype == 'suburban':
                    cost_structure[key] = value
                else:
                    cost_structure[key] = value / networks
            else:
                cost_structure[key] = value / networks

    return cost_structure


def greenfield_3g(region, strategy, parameters,
    core_lut, country_parameters):
    """
    Build a greenfield 3G asset.

    """
    backhaul = '{}_backhaul'.format(strategy.split('_')[2])
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    net_handle = 'baseline' + '_' + geotype
    networks = country_parameters['networks'][net_handle]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    core_edge_capex = core_capex(region, 'core_edge', parameters, core_lut, strategy, country_parameters)
    core_node_capex = core_capex(region, 'core_node', core_lut, parameters, strategy, country_parameters)
    regional_edge_capex = regional_net_capex(region, 'regional_edge', parameters, core_lut, strategy, country_parameters)
    regional_node_capex = regional_net_capex(region, 'regional_node', parameters, core_lut, strategy, country_parameters)

    ###provides a single year of costs for the first year of assessment
    assets = {
        'equipment_capex': parameters['equipment_capex'],
        'installation_capex': parameters['installation_capex'],
        'site_build_capex': parameters['site_build_capex'],
        'site_rental_opex': parameters['site_rental_{}_opex'.format(geotype)],
        'operation_and_maintenance_opex': parameters['operation_and_maintenance_opex'],
        'power_opex': parameters['power_opex'],
        'backhaul_capex': get_backhaul_capex(region, backhaul, parameters, core_lut),
        'backhaul_opex': 0,
        'core_edge_capex': core_edge_capex,
        'core_node_capex': core_node_capex,
        'regional_edge_capex': regional_edge_capex,
        'regional_node_capex': regional_node_capex,
        'core_edge_opex': core_edge_capex * (int(parameters['opex_percentage_of_capex']) / 100),
        'core_node_opex': core_node_capex * (int(parameters['opex_percentage_of_capex']) / 100),
        'regional_edge_opex': regional_edge_capex * (int(parameters['opex_percentage_of_capex']) / 100),
        # 'regional_node_opex': regional_node_capex * (parameters['opex_percentage_of_capex'] / 100),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            if sharing == 'srn':
                if geotype == 'urban' or geotype == 'suburban':
                    cost_structure[key] = value
                else:
                    cost_structure[key] = value / networks
            else:
                cost_structure[key] = value / networks

    return cost_structure


def greenfield_4g(region, strategy, parameters,
    core_lut, country_parameters):
    """
    Build a greenfield 4G asset.

    """
    backhaul = '{}_backhaul'.format(strategy.split('_')[2])
    sharing = strategy.split('_')[3]
    geotype = region['geotype'].split(' ')[0]

    net_handle = 'baseline' + '_' + geotype
    networks = country_parameters['networks'][net_handle]

    shared_assets = INFRA_SHARING_ASSETS[sharing]

    core_edge_capex = core_capex(region, 'core_edge', parameters, core_lut, strategy, country_parameters)
    core_node_capex = core_capex(region, 'core_node', parameters, core_lut, strategy, country_parameters)
    regional_edge_capex = regional_net_capex(region, 'regional_edge', parameters, core_lut, strategy, country_parameters)
    regional_node_capex = regional_net_capex(region, 'regional_node', parameters, core_lut, strategy, country_parameters)

    ###provides a single year of costs for the first year of assessment
    assets = {
        'equipment_capex': parameters['equipment_capex'],
        'installation_capex': parameters['installation_capex'],
        'site_build_capex': parameters['site_build_capex'],
        'site_rental_opex': parameters['site_rental_{}_opex'.format(geotype)],
        'operation_and_maintenance_opex': parameters['operation_and_maintenance_opex'],
        'power_opex': parameters['power_opex'],
        'backhaul_capex': get_backhaul_capex(region, backhaul, parameters, core_lut),
        'backhaul_opex': 0,
        'core_edge_capex': core_edge_capex,
        'core_node_capex': core_node_capex,
        'regional_edge_capex': regional_edge_capex,
        'regional_node_capex': regional_node_capex,
        'core_edge_opex': core_edge_capex * (parameters['opex_percentage_of_capex'] / 100),
        'core_node_opex': core_node_capex * (parameters['opex_percentage_of_capex'] / 100),
        'regional_edge_opex': regional_edge_capex * (parameters['opex_percentage_of_capex'] / 100),
        'regional_node_opex': regional_node_capex * (parameters['opex_percentage_of_capex'] / 100),
    }

    cost_structure = {}

    for key, value in assets.items():
        if not key in shared_assets:
            cost_structure[key] = value
        else:
            if sharing == 'srn':
                if geotype == 'urban' or geotype == 'suburban':
                    cost_structure[key] = value
                else:
                    cost_structure[key] = value / networks
            else:
                cost_structure[key] = value / networks

    return cost_structure


def get_backhaul_capex(region, backhaul, costs, core_lut):
    """
    Calculate backhaul costs.
    # backhaul_fiber backhaul_copper backhaul_wireless	backhaul_satellite

    """
    backhaul_tech = backhaul.split('_')[0]
    geotype = region['geotype'].split(' ')[0]

    nodes = 0
    for asset_type in ['core_node', 'regional_node']:
        for age in ['new', 'existing']:
            combined_key = '{}_{}'.format(region['GID_id'], age)
            nodes += core_lut[asset_type][combined_key]

    node_density_km2 = nodes / region['area_km2']
    if node_density_km2 > 0:
        ave_distance_to_a_node_m = (math.sqrt(1/node_density_km2) / 2) * 1000
    else:
        ave_distance_to_a_node_m = round(math.sqrt(region['area_km2']) * 1000)

    if backhaul_tech == 'wireless':
        if ave_distance_to_a_node_m < 15000:
            tech = '{}_{}_capex'.format(backhaul_tech, 'small')
            cost = costs[tech]
        elif 15000 < ave_distance_to_a_node_m < 30000:
            tech = '{}_{}_capex'.format(backhaul_tech, 'medium')
            cost = costs[tech]
        else:
            tech = '{}_{}_capex'.format(backhaul_tech, 'large')
            cost = costs[tech] * (ave_distance_to_a_node_m / 30000)

    elif backhaul_tech == 'fiber':
        tech = '{}_{}_m_capex'.format(backhaul_tech, geotype)
        cost_per_meter = costs[tech]
        cost = cost_per_meter * ave_distance_to_a_node_m

    else:
        print('Did not recognise the backhaul technology {}'.format(backhaul_tech))
        cost = 0

    return cost


def regional_net_capex(region, asset_type, costs, core_lut, strategy, country_parameters):
    """
    Return regional asset costs for only the 'new' assets that have been planned.
    """
    core = strategy.split('_')[1]
    geotype = region['geotype'].split(' ')[0]

    networks = country_parameters['networks']['baseline' + '_' + geotype]

    if asset_type in core_lut.keys():

        combined_key = '{}_{}'.format(region['GID_id'], 'new')

        if combined_key in core_lut[asset_type]:

            if asset_type == 'regional_edge':

                distance_m = core_lut[asset_type][combined_key]
                cost_m = costs['regional_edge_capex']
                cost = int(distance_m * cost_m)

                sites = ((region['upgraded_mno_sites'] + region['new_mno_sites']) / networks)

                if sites == 0:
                    return 0
                elif sites <= 1:
                    return cost * sites
                else:
                    return cost / sites

            if asset_type == 'regional_node':

                regional_nodes = core_lut[asset_type][combined_key]

                cost_each = costs['regional_node_{}_capex'.format(core)]

                regional_node_cost = int(regional_nodes * cost_each)

                sites = ((region['upgraded_mno_sites'] + region['new_mno_sites']) / networks)

                if sites == 0:
                    return 0
                elif sites <= 1:
                    return regional_node_cost
                else:
                    return regional_node_cost / sites
        else:
            return 0

    return 'Asset name not in lut'


def core_capex(region, asset_type, parameters, core_lut, strategy, country_parameters):
    """
    Return core asset costs for only the 'new' assets that have been planned.

    """
    core = strategy.split('_')[1]
    geotype = region['geotype'].split(' ')[0]
    networks = country_parameters['networks']['baseline' + '_' + geotype]

    if asset_type == 'core_edge':

        if asset_type in core_lut.keys():

            total_cost = []

            #only grab the new edges that need to be built
            combined_key = '{}_{}'.format(region['GID_id'], 'new')

            if combined_key in core_lut[asset_type].keys():
                distance_m = core_lut[asset_type][combined_key]

                cost = int(distance_m * parameters['core_edge_capex'])
                total_cost.append(cost)

                sites = ((region['upgraded_mno_sites'] + region['new_mno_sites']) / networks)

                if sites == 0:
                    return 0
                elif sites < 1:
                    return sum(total_cost)
                else:
                    return sum(total_cost) / sites
        else:
            return 0

    elif asset_type == 'core_node':

        if asset_type in core_lut.keys():

            total_cost = []

            #only grab the new nodes that need to be built
            combined_key = '{}_{}'.format(region['GID_id'], 'new')

            nodes = core_lut[asset_type][combined_key]

            cost = int(nodes * parameters['core_node_{}_capex'.format(core)])
            total_cost.append(cost)

            sites = ((region['upgraded_mno_sites'] + region['new_mno_sites']) / networks)

            if sites == 0:
                return 0
            elif sites < 1:
                return sum(total_cost)
            else:
                return sum(total_cost) / sites

        else:
            return 0

    else:
        print('Did not recognise core asset type {}'.format(asset_type))

    return 0


def calc_costs(region, strategy, cost_structure, backhaul_quantity,
    parameters, country_parameters):
    """

    """
    backhaul = strategy.split('_')[2]

    all_sites = region['upgraded_mno_sites'] + region['new_mno_sites']

    total_cost = 0
    cost_by_asset = []

    for asset_name, cost in cost_structure.items():

        type_of_cost = asset_name.rsplit('_')[-1]

        if 'backhaul' in asset_name and backhaul_quantity == 0:
            continue

        if 'regional_node' in asset_name and backhaul == 'wireless':
            continue

        if 'regional_edge' in asset_name and backhaul == 'wireless':
            continue

        if type_of_cost == 'capex':

            if asset_name in [
                'core_edge_capex',
                'core_node_capex',
                'regional_edge_capex',
                'regional_node_capex',
                ]:
                cost = cost / all_sites

            cost = cost * (1 + (country_parameters['financials']['wacc'] / 100))

        elif type_of_cost == 'opex':

            if asset_name in [
                'core_edge_opex',
                'core_node_opex',
                'regional_edge_opex',
                'regional_node_opex',
                ]:
                cost = cost / all_sites

            cost = discount_opex(cost, parameters, country_parameters)

        else:
            return 'Did not recognize cost type', 'Did not recognize cost type'

        total_cost += cost

        cost_by_asset.append({
            'asset': asset_name,
            'cost': cost,
        })

    cost_by_asset = {item['asset']: item['cost'] for item in cost_by_asset}

    ran_capex = ['equipment_capex']
    ran_opex = ['site_rental_opex', 'operation_and_maintenance_opex', 'power_opex']
    backhaul_capex = ['backhaul_capex']
    backhaul_opex = ['backhaul_opex']
    civils_capex = ['site_build_capex','installation_capex']
    core_capex = ['regional_node_capex','regional_edge_capex',
                    'core_node_capex','core_edge_capex']
    core_opex = ['regional_node_opex','regional_edge_opex',
                    'core_node_opex','core_edge_opex']

    ran_cost_capex = 0
    ran_cost_opex = 0
    backhaul_cost_capex = 0
    backhaul_cost_opex = 0
    civils_cost_capex = 0
    core_cost_capex = 0
    core_cost_opex = 0

    for key, value in cost_by_asset.items():
        if key in ran_capex:
            ran_cost_capex += value
        if key in ran_opex:
            ran_cost_opex += value
        if key in backhaul_capex:
            backhaul_cost_capex += value
        if key in backhaul_opex:
            backhaul_cost_opex += value
        if key in civils_capex:
             civils_cost_capex += value
        if key in core_capex:
            core_cost_capex += value
        if key in core_opex:
            core_cost_opex += value

    cost_by_asset = {
        'ran_capex': ran_cost_capex,
        'ran_opex': ran_cost_opex,
        'backhaul_capex': backhaul_cost_capex,
        'backhaul_opex': backhaul_cost_opex,
        'civils_capex': civils_cost_capex,
        'core_capex': core_cost_capex,
        'core_opex': core_cost_opex,
    }

    return total_cost, cost_by_asset


def discount_opex(opex, parameters, country_parameters):
    """
    Discount opex based on return period.

    """
    return_period = parameters['return_period']
    discount_rate = parameters['discount_rate'] / 100
    wacc = country_parameters['financials']['wacc']

    costs_over_time_period = []

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = round(sum(costs_over_time_period))

    #add wacc
    discounted_cost = discounted_cost * (1 + (wacc/100))

    return discounted_cost


INFRA_SHARING_ASSETS = {
    'baseline': [],
    'psb': [
        'site_build_capex',
        'installation_capex',
        'site_rental_opex',
        'backhaul_capex',
        'backhaul_opex',
    ],
    'moran': [
        'equipment_capex',
        'site_build_capex',
        'installation_capex',
        'site_rental_opex',
        'operation_and_maintenance_opex',
        'power_opex',
        'backhaul_capex',
        'backhaul_opex',
    ],
    'srn': [
        'equipment_capex',
        'site_build_capex',
        'installation_capex',
        'site_rental_opex',
        'operation_and_maintenance_opex',
        'power_opex',
        'backhaul_capex',
        'backhaul_opex',
        'regional_edge_capex',
        'regional_edge_opex',
        'regional_node_capex',
        'regional_node_opex',
        'core_edge_capex',
        'core_edge_opex',
        'core_node_capex',
        'core_node_opex',
    ],
}
