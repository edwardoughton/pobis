import pytest
from podis.assess import (get_spectrum_costs, calculate_tax,
    calculate_profit, assess,
    estimate_subsidies, allocate_available_excess,
    calculate_total_market_costs, calc)

def test_get_spectrum_costs(setup_region, setup_option, setup_global_parameters,
    setup_country_parameters):

    setup_region[0]['new_sites'] = 1

    # 10000 people
    # 200000 = 1 * 20 * 10000 (cost = cost_mhz_pop * bw * pop )
    # 200000 = 1 * 20 * 10000 (cost = cost_mhz_pop * bw * pop )
    assert get_spectrum_costs(setup_region[0], setup_option['strategy'],
        setup_global_parameters, setup_country_parameters) == 400000

    setup_region[0]['new_sites'] = 1

    # test high spectrum costs which are 50% higher
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_high_baseline',
        setup_global_parameters, setup_country_parameters) == (
            400000 * (setup_country_parameters['financials']['spectrum_cost_high'] / 100))

    # test low spectrum costs which are 50% lower
    assert get_spectrum_costs(setup_region[0], '4G_epc_microwave_baseline_baseline_low_baseline',
        setup_global_parameters, setup_country_parameters) == (
            400000 * (setup_country_parameters['financials']['spectrum_cost_low'] / 100))

def test_calculate_tax(setup_region, setup_option, setup_country_parameters):

    setup_region[0]['mno_network_cost'] = 1e6

    assert calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters) == 1e6 * (25/100)

    setup_region[0]['mno_network_cost'] = 1e6
    setup_option['strategy'] = '4G_epc_microwave_baseline_baseline_baseline_high'

    answer = calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters)

    assert answer == 1e6 * (40/100)

    setup_region[0]['mno_network_cost'] = 1e6
    setup_option['strategy'] = '4G_epc_microwave_baseline_baseline_baseline_low'

    answer = calculate_tax(setup_region[0], setup_option['strategy'], setup_country_parameters)

    assert answer == 1e6 * (10/100)


def test_calculate_profit(setup_region, setup_country_parameters):

    setup_region[0]['mno_network_cost'] = 1e6
    setup_region[0]['administration'] = 1e6*0.1
    setup_region[0]['spectrum_cost'] = 6e4
    setup_region[0]['tax'] = 265e3

    assert calculate_profit(setup_region[0], setup_country_parameters) == 285000


def test_estimate_subsidies():

    region = {
            'GID_id': 'a',
            'total_mno_revenue': 10000,
            'total_mno_cost': 5000,
            'available_cross_subsidy': 5000,
            'deficit': 0,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 0)

    assert answer['available_cross_subsidy'] == 5000
    assert answer['used_cross_subsidy'] == 0
    assert answer['required_state_subsidy'] == 0
    assert available_cross_subsidy == 0

    region = {
            'GID_id': 'a',
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
            'available_cross_subsidy': 0,
            'deficit': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 5000)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 5000
    assert answer['required_state_subsidy'] == 0
    assert available_cross_subsidy == 0

    region = {
            'GID_id': 'a',
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
            'available_cross_subsidy': 0,
            'deficit': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 0)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 0
    assert answer['required_state_subsidy'] == 5000
    assert available_cross_subsidy == 0

    region = {
            'GID_id': 'a',
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
            'available_cross_subsidy': 0,
            'deficit': 5000,
        }

    answer, available_cross_subsidy = estimate_subsidies(region, 2500)

    assert answer['available_cross_subsidy'] == 0
    assert answer['used_cross_subsidy'] == 2500
    assert answer['required_state_subsidy'] == 2500
    assert available_cross_subsidy == 0


def test_assess(setup_option, setup_global_parameters,
    setup_country_parameters, setup_timesteps):

    regions = [
        {
            'GID_id': 'a',
            'geotype': 'urban',
            'population': 1000,
            'population_km2': 500,
            'total_mno_revenue': 20000,
            'mno_network_cost': 5000,
            'phones_on_network': 250,
            'smartphones_on_network': 250
        },
        {
            'GID_id': 'b',
            'geotype': 'urban',
            'population': 500,
            'population_km2': 250,
            'total_mno_revenue': 12000,
            'mno_network_cost': 8000,
            'phones_on_network': 300,
            'smartphones_on_network': 250
        },
    ]

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters, setup_timesteps)

    for item in answer:
        if item['GID_id'] == 'a':
            answer1 = item
        if item['GID_id'] == 'b':
            answer2 = item

    assert answer1['total_mno_revenue'] == 20000
    assert answer1['mno_network_cost'] == 5000
    assert answer1['spectrum_cost'] == 40000
    assert answer1['tax'] == 1250
    assert answer1['profit_margin'] == 9350.0
    assert answer1['total_mno_cost'] == 56100.0
    assert answer1['available_cross_subsidy'] == 0
    assert answer1['used_cross_subsidy'] == 0
    assert answer1['required_state_subsidy'] == 36100.0

    assert answer2['total_mno_revenue'] == 12000
    assert answer2['mno_network_cost'] == 8000
    assert answer2['spectrum_cost'] == 20000
    assert answer2['tax'] == 2000
    assert answer2['profit_margin'] == 6160
    assert answer2['total_mno_cost'] == 36960.0
    assert answer2['available_cross_subsidy'] == 0
    assert answer2['used_cross_subsidy'] == 0
    assert answer2['required_state_subsidy'] == 24960.0

    regions = [
        {
            'GID_id': 'a',
            'geotype': 'urban',
            'population': 1000,
            'population_km2': 500,
            'total_mno_revenue': 20000,
            'mno_network_cost': 5200,
            'phones_on_network': 250,
            'smartphones_on_network': 250,
        },
        {
            'GID_id': 'b',
            'geotype': 'urban',
            'population': 1000,
            'population_km2': 500,
            'total_mno_revenue': 2500,
            'mno_network_cost': 5200,
            'phones_on_network': 250,
            'smartphones_on_network': 250,
        },
    ]

    answer = assess('MWI', regions, setup_option, setup_global_parameters,
        setup_country_parameters, setup_timesteps)

    assert answer[0]['available_cross_subsidy'] == 0
    assert answer[0]['used_cross_subsidy'] == 0
    assert answer[0]['required_state_subsidy'] == 36424
    assert answer[1]['available_cross_subsidy'] == 0
    assert answer[1]['used_cross_subsidy'] == 0
    assert answer[1]['required_state_subsidy'] == 53924.0


def test_allocate_available_excess():

    region = {
            'total_mno_revenue': 10000,
            'total_mno_cost': 5000,
        }

    answer = allocate_available_excess(region)

    assert answer['available_cross_subsidy'] == 5000
    assert answer['deficit'] == 0

    regions = {
            'total_mno_revenue': 5000,
            'total_mno_cost': 10000,
        }

    answer = allocate_available_excess(regions)

    assert answer['available_cross_subsidy'] == 0
    assert answer['deficit'] == 5000


def test_calculate_total_market_costs(setup_option, setup_country_parameters):
    """
    Unit test.
    """
    regions = [
        {
            'GID_id': 'a',
            'geotype': 'rural 1',
            'population': 0,
            'population_km2': 0,
            'total_mno_revenue': 33.3,
            'mno_network_cost': 0,
            'smartphones_on_network': 0,
            'phones_on_network': 0,
            'administration': 33.3,
            'spectrum_cost': 33.3,
            'tax': 33.3,
            'profit_margin': 33.3,
            'cost': 33.3,
            'available_cross_subsidy': 33.3,
            'deficit': 33.3,
            'used_cross_subsidy': 33.3,
            'required_state_subsidy': 33.3,
            'total_mno_cost': 33.3
        },
    ]

    answer = calculate_total_market_costs(regions, setup_option, setup_country_parameters)

    assert answer[0]['total_market_revenue'] == 100
    assert answer[0]['total_administration'] == 100
    assert answer[0]['total_spectrum_cost'] == 100
    assert answer[0]['total_market_cost'] == 100
    assert answer[0]['total_available_cross_subsidy'] == 100
    assert answer[0]['total_used_cross_subsidy'] == 100

    setup_option['scenario'] == '4G_epc_wireless_srn_srn_baseline_baseline'
    regions[0]['geotype'] == 'rural'

    answer = calculate_total_market_costs(regions, setup_option, setup_country_parameters)

    assert answer[0]['total_market_revenue'] == 100
    assert answer[0]['total_administration'] == 100
    assert answer[0]['total_spectrum_cost'] == 100
    assert answer[0]['total_market_cost'] == 100
    assert answer[0]['total_available_cross_subsidy'] == 100
    assert answer[0]['total_used_cross_subsidy'] == 100
