import pytest
import math
from podis.costs import (upgrade_to_3g, upgrade_to_4g,
    greenfield_3g, greenfield_4g, backhaul_quantity,
    get_backhaul_costs, regional_net_costs,
    core_costs, discount_opex,
    discount_capex_and_opex, calc_costs,
    find_network_cost)

#test approach is to:
#test each function which returns the cost structure
#test the function which calculates quantities
#test infrastructure sharing strategies
#test meta cost function


def test_find_network_cost(setup_region, setup_costs,
    setup_global_parameters, setup_country_parameters,
    setup_core_lut):
    """
    Integration test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    answer = find_network_cost(
        setup_region[0],
        {'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 460504.85

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 1

    answer = find_network_cost(
        setup_region[0],
        {'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 597858.5499999999

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    answer = find_network_cost(
        setup_region[0],
        {'strategy': '3G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 611603.35

    answer = find_network_cost(
        setup_region[0],
        {'strategy': '4G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 611603.35

    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    answer = find_network_cost(
        setup_region[0],
        {'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 705490.4999999999

    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 1

    answer = find_network_cost(
        setup_region[0],
        {'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 708926.6999999998

    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    answer = find_network_cost(
        setup_region[0],
        {'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['network_cost'] == 737603.0999999999


def test_find_network_cost_for_sharing_strategies(setup_region, setup_costs,
    setup_global_parameters, setup_country_parameters,
    setup_core_lut):
    """
    Integration test for sharing strategies.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    ####Test different sharing strategies - urban area
    setup_region[0]['geotype'] = 'urban'

    answer = find_network_cost(  #baseline
        setup_region[0],
        {'strategy': '4G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 460504.85

    answer = find_network_cost(  #passive sharing
        setup_region[0],
        {'strategy': '4G_epc_wireless_psb_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 400135.6

    answer = find_network_cost(  #active sharing
        setup_region[0],
        {'strategy': '4G_epc_wireless_moran_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 355099.6833333333

    answer = find_network_cost(  #shared rural network
        setup_region[0],
        {'strategy': '4G_epc_wireless_srn_srn_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 460504.85

    ####Test different sharing strategies - rural area
    setup_region[0]['geotype'] = 'rural'

    answer = find_network_cost(  #baseline
        setup_region[0],
        {'strategy': '4G_epc_wireless_baseline_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 443441.14999999997

    answer = find_network_cost(  #passive sharing
        setup_region[0],
        {'strategy': '4G_epc_wireless_psb_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 394447.69999999995

    answer = find_network_cost(  #active sharing
        setup_region[0],
        {'strategy': '4G_epc_wireless_moran_baseline_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 349411.78333333327

    answer = find_network_cost(  #shared rural network
        setup_region[0],
        {'strategy': '4G_epc_wireless_srn_srn_baseline_baseline'},
        setup_costs,
        setup_global_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['network_cost'] == 147815.6333333333


def test_upgrade_to_3g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == 40000
    assert cost_structure['installation'] ==30000

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])

    assert cost_structure['backhaul'] == (
        setup_costs['wireless_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'] /
        setup_country_parameters['networks']['baseline_urban'])

    assert cost_structure['installation'] == (
        setup_costs['installation'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment']) == round(
        (setup_costs['equipment']))
    assert round(cost_structure['core_edge']) == round(
        (setup_costs['core_edge'] * 1000))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_upgrade_to_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == 40000
    assert cost_structure['installation'] == 30000
    assert cost_structure['site_rental'] == 9600

    cost_structure = upgrade_to_4g(setup_region[0],
        '4g_epc_wireless_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul'] == (
        setup_costs['wireless_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_4g(setup_region[0],
        '4g_epc_wireless_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment']) == round(
        (setup_costs['equipment']))
    assert round(cost_structure['core_edge']) == round(
        (setup_costs['core_edge'] * 1000))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_greenfield_3g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == 40000
    assert cost_structure['site_rental'] == 9600

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul'] == (
        setup_costs['wireless_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'] /
        setup_country_parameters['networks']['baseline_urban'])

    setup_region[0]['geotype'] = 'urban'
    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment']) == round(
        (setup_costs['equipment']))
    assert round(cost_structure['core_edge']) == round(
        (setup_costs['core_edge'] * 1000))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_greenfield_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == 40000
    assert cost_structure['site_rental'] == 9600

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul'] == (
        setup_costs['wireless_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment']) == setup_costs['equipment']
    assert round(cost_structure['backhaul']) == setup_costs['wireless_small']
    assert round(cost_structure['core_edge']) == round(
        (setup_costs['core_edge'] * 1000))
    assert round(cost_structure['core_node']) == round(
        (setup_costs['core_node_epc'] * 2))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment']) == round(
        setup_costs['equipment'] * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment'] == (
        setup_costs['equipment'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_backhaul_quantity():
    """
    Unit test.

    """
    assert backhaul_quantity(2, 1) == 0


def test_get_backhaul_costs(setup_region, setup_costs, setup_core_lut, setup_empty_core_lut):
    """
    Unit test.

    """
    assert get_backhaul_costs(setup_region[0], 'wireless',
        setup_costs, setup_core_lut) == (setup_costs['wireless_small'])

    setup_region[0]['area_km2'] = 5000

    assert get_backhaul_costs(setup_region[0], 'wireless',
        setup_costs, setup_core_lut) == (setup_costs['wireless_small'])

    setup_region[0]['area_km2'] = 20000

    assert get_backhaul_costs(setup_region[0], 'wireless',
        setup_costs, setup_core_lut) == (setup_costs['wireless_medium'])

    setup_region[0]['area_km2'] = 100000

    assert get_backhaul_costs(setup_region[0], 'wireless',
        setup_costs, setup_core_lut) == (setup_costs['wireless_large'] * (55901.69943749474 / 30000))

    setup_region[0]['area_km2'] = 2

    assert get_backhaul_costs(setup_region[0], 'fiber',
        setup_costs, setup_core_lut) == (setup_costs['fiber_urban_m'] * 250)

    assert get_backhaul_costs(setup_region[0], 'incorrect_backhaul_tech_name',
        setup_costs, setup_core_lut) == 0

    assert get_backhaul_costs(setup_region[0], 'fiber',
        setup_costs, setup_empty_core_lut) == 14140


def test_regional_net_costs(setup_region, setup_option, setup_costs, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 6
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 6

    assert regional_net_costs(setup_region[0], 'regional_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_edge'] * setup_core_lut['regional_edge']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    setup_region[0]['total_estimated_sites'] = 10
    setup_region[0]['new_mno_sites'] = 10

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    setup_core_lut['regional_node']['MWI.1.1.1_1'] = 10
    setup_region[0]['area_km2'] = 100

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    assert regional_net_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 'Asset name not in lut'

    setup_region[0]['total_estimated_sites'] = 0
    setup_region[0]['new_mno_sites'] = 0

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    setup_region[0]['GID_id'] = 'unknown GID ID'

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    #test that no sites returns zero cost
    setup_region[0]['total_estimated_sites'] = 0

    assert regional_net_costs(setup_region[0], 'regional_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    #test asset name not being in the LUT
    assert regional_net_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 'Asset name not in lut'


def test_core_costs(setup_region, setup_option, setup_costs, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['total_estimated_sites'] = 2
    setup_country_parameters['networks']['baseline_urban'] = 2

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (setup_costs['core_edge'] * 1000)

    assert core_costs(setup_region[0], 'core_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (setup_costs['core_node_{}'.format('epc')] * 2)

    assert core_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    setup_region[0]['GID_id'] == 'unknown'

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['core_edge'] * setup_core_lut['core_edge']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    #test that no sites returns zero cost
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 0

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    assert core_costs(setup_region[0], 'core_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        {}, setup_option['strategy'], setup_country_parameters) == 0

    assert core_costs(setup_region[0], 'core_node', setup_costs,
        {}, setup_option['strategy'], setup_country_parameters) == 0


def test_calc_costs(setup_region, setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline_baseline',
        {'equipment': 40000},
        1,
        setup_global_parameters,
        setup_country_parameters
    )

    assert answer == 40000 * (1 + (setup_country_parameters['financials']['wacc'] / 100))

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline_baseline',
        {'site_rental': 9600},
        1,
        setup_global_parameters,
        setup_country_parameters
    )

    assert answer == 18743 *  (1 + (setup_country_parameters['financials']['wacc'] / 100))#two years' of rent

    answer, structure = calc_costs(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline_baseline',
        {
        'equipment': 40000,
        'site_rental': 9600,
        },
        6,
        setup_global_parameters,
        setup_country_parameters)

    #answer = sum of equipment + site_rental
    assert answer == (
        40000 * (1 + (setup_country_parameters['financials']['wacc'] / 100)) +
        18743 *  (1 + (setup_country_parameters['financials']['wacc'] / 100))
        )

    answer, structure = calc_costs(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline_baseline',
        {
        'incorrect_name': 9600,
        },
        6,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 0 #two years' of rent


def test_discount_capex_and_opex(setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    assert discount_capex_and_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1195 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))


def test_discount_opex(setup_global_parameters, setup_country_parameters):
    """
    Unit test.

    """
    assert discount_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1952 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))
