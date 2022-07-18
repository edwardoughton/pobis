"""
Functions for writing to .csv

September 2020

Written by Ed Oughton

"""
import os
import pandas as pd
import datetime


def define_deciles(regions):
    """
    Allocate deciles to regions.

    """
    regions = regions.sort_values(by='population_km2', ascending=True)

    regions['decile'] = regions.groupby([
        'GID_0',
        'scenario',
        'strategy',
        'confidence'
    ], as_index=True).population_km2.apply( #cost_per_sp_user
        pd.qcut, q=11, precision=0,
        labels=[100,90,80,70,60,50,40,30,20,10,0],
        duplicates='drop') #   [0,10,20,30,40,50,60,70,80,90,100]

    return regions


def write_mno_demand(regional_annual_demand, folder, metric, path):
    """
    Write all annual demand results for a single hypothetical Mobile
    Network Operator (MNO).

    """
    print('Writing annual_demand')
    regional_annual_demand = pd.DataFrame(regional_annual_demand)
    regional_annual_demand = regional_annual_demand[[
        'GID_0', 'GID_id', 'scenario', 'strategy',
        'confidence', 'input_cost', 'year', 'population', 'area_km2', 'population_km2',
        'geotype', 'arpu_discounted_monthly', 'penetration', 'population_with_phones',
        'phones_on_network', 'smartphone_penetration', 'population_with_smartphones',
        'smartphones_on_network', 'revenue'
    ]]

    regional_annual_demand.to_csv(path, index=False)


def write_regional_results(regional_results, folder, metric):
    """
    Write all results.

    """
    print('Writing regional results')
    regional_mno_results = pd.DataFrame(regional_results)
    regional_mno_results = define_deciles(regional_mno_results)
    regional_mno_results = regional_mno_results[[
        'GID_0', 'GID_id', 'scenario', 'strategy', 'decile',
        'confidence', 'input_cost', 'population', 'area_km2',
        'phones_on_network', 'smartphones_on_network',
        'total_estimated_sites', 'existing_mno_sites',
        'upgraded_mno_sites', 'new_mno_sites',
        'total_mno_revenue',
        'mno_network_capex', 'mno_network_opex', 'mno_network_cost',
        'total_mno_cost',
    ]]
    regional_mno_results = regional_mno_results.drop_duplicates()
    regional_mno_results['cost_per_network_user'] = (
        regional_mno_results['total_mno_cost'] / regional_mno_results['phones_on_network'])
    regional_mno_results['cost_per_smartphone_user'] = (
        regional_mno_results['total_mno_cost'] /
        regional_mno_results['smartphones_on_network'])

    if not os.path.exists(folder):
        os.mkdir(folder)

    path = os.path.join(folder,'regional_mno_results_{}.csv'.format(metric))
    regional_mno_results.to_csv(path, index=False)


    # print('Writing regional results')
    # regional_market_results = pd.DataFrame(regional_results)
    # regional_market_results = define_deciles(regional_market_results)
    # regional_market_results = regional_market_results[[
    #     'GID_0', 'GID_id', 'scenario', 'strategy', 'decile',
    #     'confidence', 'population', 'area_km2', 'geotype',
    #     'total_phones', 'total_smartphones',
    #     'total_upgraded_sites','total_new_sites',
    #     'total_market_revenue', 'total_market_cost',
    # ]]
    # regional_market_results = regional_market_results.drop_duplicates()
    # regional_market_results['cost_per_network_user'] = (
    #     regional_market_results['total_market_cost'] /
    #     regional_market_results['total_phones'])
    # regional_market_results['cost_per_smartphone_user'] = (
    #     regional_market_results['total_market_cost'] /
    #     regional_market_results['total_smartphones'])

    # path = os.path.join(folder,'regional_market_results_{}.csv'.format(metric))
    # regional_market_results.to_csv(path, index=False)


    print('Writing regional cost results')
    regional_mno_cost_results = pd.DataFrame(regional_results)
    regional_mno_cost_results = define_deciles(regional_mno_cost_results)
    regional_mno_cost_results = regional_mno_cost_results[[
        'GID_0', 'GID_id', 'scenario', 'strategy',
        'decile', 'confidence', 'input_cost', 'population', 'area_km2', 'geotype',
        'phones_on_network', 'smartphones_on_network', 'total_mno_revenue',
        'ran_capex', 'ran_opex', 'backhaul_capex',
        'backhaul_opex', 'civils_capex', 'core_capex', 'core_opex',
        'administration', 'spectrum_cost', 'tax', 'profit_margin',
        'total_mno_cost', 'available_cross_subsidy', 'deficit',
        'used_cross_subsidy', 'required_state_subsidy',
    ]]

    regional_mno_cost_results = regional_mno_cost_results.drop_duplicates()
    regional_mno_cost_results['private_cost'] = regional_mno_cost_results['total_mno_cost']
    regional_mno_cost_results['government_cost'] = (
    regional_mno_cost_results['required_state_subsidy'] -
        (regional_mno_cost_results['spectrum_cost'] +
        regional_mno_cost_results['tax']))
    regional_mno_cost_results['financial_cost'] = (
        regional_mno_cost_results['private_cost'] +
        regional_mno_cost_results['government_cost'])

    regional_mno_cost_results['private_cost_per_network_user'] = (
        regional_mno_cost_results['total_mno_cost'] /
        regional_mno_cost_results['phones_on_network'])
    regional_mno_cost_results['government_cost_per_network_user'] = (
        regional_mno_cost_results['government_cost'] /
        regional_mno_cost_results['phones_on_network'])
    regional_mno_cost_results['financial_cost_per_network_user'] = (
        regional_mno_cost_results['financial_cost'] /
        regional_mno_cost_results['phones_on_network'])

    regional_mno_cost_results['private_cost_per_smartphone_user'] = (
        regional_mno_cost_results['total_mno_cost'] /
        regional_mno_cost_results['smartphones_on_network'])
    regional_mno_cost_results['government_cost_per_smartphone_user'] = (
        regional_mno_cost_results['government_cost'] /
        regional_mno_cost_results['smartphones_on_network'])
    regional_mno_cost_results['financial_cost_per_smartphone_user'] = (
        regional_mno_cost_results['financial_cost'] /
        regional_mno_cost_results['smartphones_on_network'])

    # regional_mno_cost_results['required_efficiency_saving'] = (
    #     regional_mno_cost_results['government_cost'] /
    #     regional_mno_cost_results['private_cost'] * 100)

    path = os.path.join(folder,'regional_mno_cost_results_{}.csv'.format(metric))
    regional_mno_cost_results.to_csv(path, index=False)


def write_decile_results(regional_results, folder, metric):
    """
    Write decile results.

    """
    print('Writing general decile results')
    decile_results = pd.DataFrame(regional_results)
    decile_results = define_deciles(decile_results)
    decile_results = decile_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence', 'input_cost',
        'population', 'area_km2', 'phones_on_network',
        'smartphones_on_network', 'total_estimated_sites',
        'existing_mno_sites', 'upgraded_mno_sites', 'new_mno_sites',
        'total_mno_revenue',
        'mno_network_capex', 'mno_network_opex', 'mno_network_cost',
        'total_mno_cost',
    ]]
    decile_results = decile_results.drop_duplicates()
    decile_results = decile_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_results['population_km2'] = (
        decile_results['population'] / decile_results['area_km2'])
    decile_results['phone_density_on_network_km2'] = (
        decile_results['phones_on_network'] / decile_results['area_km2'])
    decile_results['sp_density_on_network_km2'] = (
        decile_results['smartphones_on_network'] / decile_results['area_km2'])
    decile_results['total_estimated_sites_km2'] = (
        decile_results['total_estimated_sites'] / decile_results['area_km2'])
    decile_results['existing_mno_sites_km2'] = (
        decile_results['existing_mno_sites'] / decile_results['area_km2'])
    decile_results['cost_per_network_user'] = (
        decile_results['total_mno_cost'] / decile_results['phones_on_network'])
    decile_results['cost_per_smartphone_user'] = (
        decile_results['total_mno_cost'] / decile_results['smartphones_on_network'])

    if not os.path.exists(folder):
        os.mkdir(folder)

    path = os.path.join(folder,'decile_mno_results_{}.csv'.format(metric))
    decile_results.to_csv(path, index=False)


    print('Writing cost decile results')
    decile_cost_results = pd.DataFrame(regional_results)
    decile_cost_results = define_deciles(decile_cost_results)
    decile_cost_results = decile_cost_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence', 'input_cost',
        'population', 'area_km2', 'phones_on_network', 'smartphones_on_network',
        'total_mno_revenue', 'ran_capex', 'ran_opex', 'backhaul_capex',
        'backhaul_opex', 'civils_capex', 'core_capex', 'core_opex',
        'administration', 'spectrum_cost', 'tax', 'profit_margin',
        'mno_network_capex', 'mno_network_opex', 'mno_network_cost',
        'total_mno_cost',
        'available_cross_subsidy', 'deficit', 'used_cross_subsidy',
        'required_state_subsidy',
    ]]
    decile_cost_results = decile_cost_results.drop_duplicates()
    decile_cost_results = decile_cost_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_cost_results['cost_per_network_user'] = (
        decile_cost_results['total_mno_cost'] / decile_cost_results['phones_on_network'])
    decile_cost_results['cost_per_smartphone_user'] = (
        decile_cost_results['total_mno_cost'] / decile_cost_results['smartphones_on_network'])
    decile_cost_results['private_cost'] = decile_cost_results['total_mno_cost']
    decile_cost_results['government_cost'] = (
        decile_cost_results['required_state_subsidy'] -
            (decile_cost_results['spectrum_cost'] + decile_cost_results['tax']))
    decile_cost_results['financial_cost'] = (
        decile_cost_results['private_cost'] + decile_cost_results['government_cost'])

    path = os.path.join(folder,'decile_mno_cost_results_{}.csv'.format(metric))
    decile_cost_results.to_csv(path, index=False)

    # print('Writing general decile results')
    # decile_results = pd.DataFrame(regional_results)
    # decile_results = define_deciles(decile_results)
    # decile_results = decile_results[[
    #     'GID_0', 'scenario', 'strategy', 'decile', 'confidence',
    #     'population', 'area_km2', 'total_phones', 'total_smartphones',
    #     'total_market_revenue',
    #     # 'total_market_capex', 'total_market_opex',
    #     'total_market_cost',
    # ]]
    # decile_results = decile_results.drop_duplicates()
    # decile_results = decile_results.groupby([
    #     'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    # decile_results['population_km2'] = (
    #     decile_results['population'] / decile_results['area_km2'])
    # decile_results['cost_per_network_user'] = (
    #     decile_results['total_market_cost'] / decile_results['total_phones'])
    # decile_results['cost_per_smartphone_user'] = (
    #     decile_results['total_market_cost'] / decile_results['total_smartphones'])

    # path = os.path.join(folder,'decile_market_results_{}.csv'.format(metric))
    # decile_results.to_csv(path, index=False)


    # print('Writing cost decile results')
    # decile_cost_results = pd.DataFrame(regional_results)
    # decile_cost_results = define_deciles(decile_cost_results)
    # decile_cost_results = decile_cost_results[[
    #     'GID_0', 'scenario', 'strategy', 'decile', 'confidence',
    #     'population', 'area_km2', 'total_phones', 'total_smartphones',
    #     'total_market_revenue',
    #     'total_ran_capex', 'total_ran_opex',
    #     'total_backhaul_capex', 'total_backhaul_opex',
    #     'total_civils_capex',
    #     'total_core_capex', 'total_core_opex',
    #     'total_administration', 'total_spectrum_cost', 'total_tax',
    #     'total_profit_margin',
    #     'total_network_capex', 'total_network_opex',
    #     'total_market_cost',
    #     'total_available_cross_subsidy', 'total_deficit',
    #     'total_used_cross_subsidy', 'total_required_state_subsidy'
    # ]]
    # decile_cost_results = decile_cost_results.drop_duplicates()
    # decile_cost_results = decile_cost_results.groupby([
    #     'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    # decile_cost_results['cost_per_network_user'] = (
    #     decile_cost_results['total_market_cost'] /
    #     decile_cost_results['total_phones'])
    # decile_cost_results['cost_per_smartphone_user'] = (
    #     decile_cost_results['total_market_cost'] /
    #     decile_cost_results['total_smartphones'])

    # path = os.path.join(folder,'decile_market_cost_results_{}.csv'.format(metric))
    # decile_cost_results.to_csv(path, index=False)


def write_national_results(regional_results, folder, metric):
    """
    Write national results.

    """
    # print('Writing national MNO results')
    # national_results = pd.DataFrame(regional_results)
    # national_results = national_results[[
    #     'GID_0', 'scenario', 'strategy', 'confidence', 'population', 'area_km2',
    #     'phones_on_network', 'smartphones_on_network', 'total_estimated_sites',
    #     'existing_mno_sites', 'upgraded_mno_sites', 'new_mno_sites',
    #     'mno_network_capex', 'mno_network_opex','mno_network_cost',
    #     'total_mno_revenue', 'total_mno_cost',
    # ]]
    # national_results = national_results.drop_duplicates()
    # national_results = national_results.groupby([
    #     'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    # national_results['cost_per_network_user'] = (
    #     national_results['total_mno_cost'] / national_results['phones_on_network'])
    # national_results['cost_per_smartphone_user'] = (
    #     national_results['total_mno_cost'] / national_results['smartphones_on_network'])

    # if not os.path.exists(folder):
    #     os.mkdir(folder)

    # path = os.path.join(folder,'national_mno_results_{}.csv'.format(metric))
    # national_results.to_csv(path, index=False)


    # print('Writing national cost composition results')
    # national_cost_results = pd.DataFrame(regional_results)
    # national_cost_results = national_cost_results[[
    #     'GID_0', 'scenario', 'strategy', 'confidence', 'population',
    #     'phones_on_network', 'smartphones_on_network', 'total_mno_revenue',
    #     'ran_capex', 'ran_opex', 'backhaul_capex', 'backhaul_opex',
    #     'civils_capex', 'core_capex', 'core_opex',
    #     'administration', 'spectrum_cost', 'tax', 'profit_margin',
    #     'mno_network_capex', 'mno_network_opex',
    #     'mno_network_cost',
    #     'available_cross_subsidy', 'deficit',
    #     'used_cross_subsidy', 'required_state_subsidy', 'total_mno_cost'
    # ]]
    # national_cost_results = national_cost_results.drop_duplicates()
    # national_cost_results = national_cost_results.groupby([
    #     'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    # national_cost_results['cost_per_network_user'] = (
    #     national_cost_results['total_mno_cost'] /
    #     national_cost_results['phones_on_network'])
    # national_cost_results['cost_per_smartphone_user'] = (
    #     national_cost_results['total_mno_cost'] /
    #     national_cost_results['smartphones_on_network'])
    # #Calculate private, govt and financial costs
    # national_cost_results['private_cost'] = national_cost_results['total_mno_cost']
    # national_cost_results['government_cost'] = (
    #     national_cost_results['required_state_subsidy'] -
    #         (national_cost_results['spectrum_cost'] + national_cost_results['tax']))
    # national_cost_results['financial_cost'] = (
    #     national_cost_results['private_cost'] + national_cost_results['government_cost'])
    # # national_cost_results['required_efficiency_saving'] = (
    # #     national_cost_results['government_cost'] /
    # #     national_cost_results['private_cost'] * 100)

    # path = os.path.join(folder,'national_mno_cost_results_{}.csv'.format(metric))
    # national_cost_results.to_csv(path, index=False)

    # print('Writing national market results')
    # national_results = pd.DataFrame(regional_results)
    # national_results = national_results[[
    #     'GID_0', 'scenario', 'strategy', 'confidence', 'population', 'area_km2',
    #     'total_phones', 'total_smartphones',
    #     'total_estimated_sites',
    #     'total_upgraded_sites',
    #     'total_new_sites',
    #     'total_market_revenue',
    #     'total_network_capex', 'total_network_opex',
    #     'total_market_cost',
    #     'total_required_state_subsidy', 'total_spectrum_cost', 'total_tax',
    # ]]
    # national_results = national_results.drop_duplicates()
    # national_results = national_results.groupby([
    #     'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    # national_results['cost_per_network_user'] = (
    #     national_results['total_market_cost'] / national_results['total_phones'])
    # national_results['cost_per_smartphone_user'] = (
    #     national_results['total_market_cost'] / national_results['total_smartphones'])
    # national_results['private_cost'] = (
    #     national_results['total_market_cost'])
    # national_results['government_cost'] = (
    #     national_results['total_required_state_subsidy'] -
    #         (national_results['total_spectrum_cost'] + national_results['total_tax']))
    # national_results['financial_cost'] = (
    #     national_results['private_cost'] + national_results['government_cost'])

    # path = os.path.join(folder,'national_market_results_{}.csv'.format(metric))
    # national_results.to_csv(path, index=False)

    #=cost / market share * 100
    print('Writing national market cost composition results')
    national_cost_results = pd.DataFrame(regional_results)
    national_cost_results = national_cost_results[[
        'GID_0', 'scenario', 'strategy', 'confidence', 'input_cost', 'population',
        'total_phones', 'total_smartphones',
        'total_market_revenue',
        'total_ran_capex', 'total_ran_opex',
        'total_backhaul_capex', 'total_backhaul_opex',
        'total_civils_capex',
        'total_core_capex', 'total_core_opex',
        'total_administration', 'total_spectrum_cost',
        'total_tax', 'total_profit_margin',
        'total_network_capex', 'total_network_opex',
        'total_market_cost',
        'total_available_cross_subsidy',
        'total_deficit', 'total_used_cross_subsidy',
        'total_required_state_subsidy',
    ]]
    national_cost_results = national_cost_results.drop_duplicates()
    national_cost_results = national_cost_results.groupby([
        'GID_0', 'scenario', 'strategy', 'input_cost', 'confidence'], as_index=True).sum().reset_index()

    national_cost_results['cost_per_network_user'] = (
        national_cost_results['total_market_cost'] / national_cost_results['total_phones'])
    national_cost_results['cost_per_smartphone_user'] = (
        national_cost_results['total_market_cost'] / national_cost_results['total_smartphones'])
    #Calculate private, govt and financial costs
    national_cost_results['private_cost'] = (
        national_cost_results['total_market_cost'])
    national_cost_results['government_cost'] = (
        national_cost_results['total_required_state_subsidy'] -
            (national_cost_results['total_spectrum_cost'] + national_cost_results['total_tax']))
    national_cost_results['financial_cost'] = (
        national_cost_results['private_cost'] + national_cost_results['government_cost'])
    national_cost_results['required_efficiency_saving'] = (
        national_cost_results['government_cost'] /
        national_cost_results['private_cost'] * 100)

    path = os.path.join(folder,'national_market_cost_results_{}.csv'.format(metric))
    national_cost_results.to_csv(path, index=False)


# def write_inputs(folder, country, country_parameters, global_parameters,
#     decision_option):
#     """
#     Write model inputs.

#     """
#     country_folder = os.path.join(folder, country['iso3'])

#     if not os.path.exists(country_folder):
#         os.makedirs(country_folder)

#     country_info = pd.DataFrame(country.items(),
#         columns=['parameter', 'value'])
#     country_info['source'] = 'country_info'

#     country_params = pd.DataFrame(
#         country_parameters['financials'].items(),
#         columns=['parameter', 'value'])
#     country_params['source'] = 'country_parameters'

#     global_parameters = pd.DataFrame(global_parameters.items(),
#         columns=['parameter', 'value'])
#     global_parameters['source'] = 'global_parameters'

#     # costs = pd.DataFrame(costs.items(),
#     #     columns=['parameter', 'value'])
#     # costs['source'] = 'costs'

#     parameters = country_info.append(country_params)
#     parameters = parameters.append(global_parameters)
#     # parameters = parameters.append(costs)
#     parameters = parameters[['source', 'parameter', 'value']]

#     timenow = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

#     filename = 'parameters_{}_{}.csv'.format(decision_option, timenow)
#     path = os.path.join(country_folder, filename)
#     parameters.to_csv(path, index=False)

#     ###write out spectrum frequencies
#     frequencies = country_parameters['frequencies']
#     generations = ['3G', '4G', '5G']
#     all_frequencies = []
#     for generation in generations:
#         for key, item in frequencies.items():
#             if generation == key:
#                 all_frequencies.append({
#                     'generation': generation,
#                     'frequency': item[0]['frequency'],
#                     'bandwidth': item[0]['bandwidth'],
#                 })
#     frequency_lut = pd.DataFrame(all_frequencies)

#     timenow = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

#     filename = 'parameters_frequencies_{}_{}.csv'.format(decision_option, timenow)
#     path = os.path.join(country_folder, filename)
#     frequency_lut.to_csv(path, index=False)
