import pytest
import math
from podis.costs import (upgrade_to_3g, upgrade_to_4g,
    greenfield_3g, greenfield_4g, backhaul_quantity,
    get_backhaul_capex, regional_net_capex,
    core_capex, discount_opex,
    calc_costs,
    find_network_cost)

#test approach is to:
#test each function which returns the cost structure
#test the function which calculates quantities
#test infrastructure sharing strategies
#test meta cost function


def test_find_network_cost(setup_region,
    setup_parameters, setup_country_parameters,
    setup_core_lut):
    """
    Integration test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    setup_parameters['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'

    answer = find_network_cost(
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['mno_network_cost'] == 185599.65 #460504.85

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 1

    setup_parameters['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'

    answer = find_network_cost(
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['mno_network_cost'] ==  458160.0 #595612.6

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    setup_parameters['strategy'] = '3G_epc_wireless_baseline_baseline_baseline_baseline'

    answer = find_network_cost(
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['mno_network_cost'] == 469660.0 #607112.6

    setup_parameters['strategy'] = '4G_epc_wireless_baseline_baseline_baseline_baseline'

    answer = find_network_cost(
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['mno_network_cost'] == 607112.6

    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 0

    setup_parameters['strategy'] = '4G_epc_fiber_baseline_baseline_baseline_baseline'

    answer = find_network_cost(
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['mno_network_cost'] == 705492.0333333332

    setup_region[0]['new_mno_sites'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 1

    setup_parameters['strategy'] = '4G_epc_fiber_baseline_baseline_baseline_baseline'

    answer = find_network_cost(
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['mno_network_cost'] == 708367.0333333332

    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['site_density'] = 0.5
    setup_region[0]['backhaul_new'] = 2

    setup_parameters['strategy'] = '4G_epc_fiber_baseline_baseline_baseline_baseline'

    answer = find_network_cost(
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )

    assert answer['mno_network_cost'] == 873931.7666666666


def test_find_network_cost_for_sharing_strategies(setup_region,
    setup_parameters, setup_country_parameters,
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

    setup_parameters['strategy'] = '4G_epc_wireless_baseline_baseline_baseline_baseline'

    answer = find_network_cost(  #baseline
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 460504.85

    setup_parameters['strategy'] = '4G_epc_wireless_psb_baseline_baseline_baseline'

    answer = find_network_cost(  #passive sharing
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 400135.6

    setup_parameters['strategy'] = '4G_epc_wireless_moran_baseline_baseline_baseline'

    answer = find_network_cost(  #active sharing
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 355099.6833333333

    setup_parameters['strategy'] = '4G_epc_wireless_srn_srn_baseline_baseline'

    answer = find_network_cost(  #shared rural network
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 460504.85

    ####Test different sharing strategies - rural area
    setup_region[0]['geotype'] = 'rural'

    setup_parameters['strategy'] = '4G_epc_wireless_baseline_baseline_baseline_baseline'

    answer = find_network_cost(  #baseline
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 443441.14999999997

    setup_parameters['strategy'] = '4G_epc_wireless_psb_baseline_baseline_baseline'

    answer = find_network_cost(  #passive sharing
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 394447.7

    setup_parameters['strategy'] = '4G_epc_wireless_moran_baseline_baseline_baseline'

    answer = find_network_cost(  #active sharing
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 349411.78333333333

    setup_parameters['strategy'] = '4G_epc_wireless_srn_srn_baseline_baseline'

    answer = find_network_cost(  #shared rural network
        setup_region[0],
        setup_parameters,
        setup_country_parameters,
        setup_core_lut
    )
    assert answer['mno_network_cost'] == 147814.8666666667


def test_upgrade_to_3g(setup_region, setup_parameters, setup_core_lut,
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
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == 40000
    assert cost_structure['installation_capex'] ==30000
    assert cost_structure['core_edge_capex'] == 20000
    assert cost_structure['core_node_capex'] == 200000
    assert cost_structure['core_node_opex'] == 20000 #(10% of above)

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_psb_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental_opex'] == (
        setup_parameters['site_rental_urban_opex'] /
        setup_country_parameters['networks']['baseline_urban'])

    assert cost_structure['backhaul_capex'] == (
        setup_parameters['wireless_small_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_moran_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    assert cost_structure['installation_capex'] == (
        setup_parameters['installation_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment_capex']) == round(
        (setup_parameters['equipment_capex']))
    assert round(cost_structure['core_edge_capex']) == round(
        (setup_parameters['core_edge_capex'] * 1000))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'])
    assert cost_structure['core_edge_capex'] == (
        (setup_parameters['core_edge_capex'] * 1000))


def test_upgrade_to_4g(setup_region,
    setup_parameters, setup_core_lut,
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
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == 40000
    assert cost_structure['installation_capex'] == 30000
    assert cost_structure['site_rental_opex'] == 9600

    cost_structure = upgrade_to_4g(setup_region[0],
        '4g_epc_wireless_psb_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental_opex'] == (
        setup_parameters['site_rental_urban_opex'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul_capex'] == (
        setup_parameters['wireless_small_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_4g(setup_region[0],
        '4g_epc_wireless_moran_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment_capex']) == round(
        (setup_parameters['equipment_capex']))
    assert round(cost_structure['core_edge_capex']) == round(
        (setup_parameters['core_edge_capex'] * 1000))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'])
    assert cost_structure['core_edge_capex'] == (
        (setup_parameters['core_edge_capex'] * 1000))


def test_greenfield_3g(setup_region,
    setup_parameters, setup_core_lut,
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
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == 40000
    assert cost_structure['site_rental_opex'] == 9600

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_psb_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental_opex'] == (
        setup_parameters['site_rental_urban_opex'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul_capex'] == (
        setup_parameters['wireless_small_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_moran_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    setup_region[0]['geotype'] = 'urban'
    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment_capex']) == round(
        (setup_parameters['equipment_capex']))
    assert round(cost_structure['core_edge_capex']) == round(
        (setup_parameters['core_edge_capex'] * 1000))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'])
    assert cost_structure['core_edge_capex'] == (
        (setup_parameters['core_edge_capex'] * 1000))


def test_greenfield_4g(setup_region,
    setup_parameters, setup_core_lut,
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
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == 40000
    assert cost_structure['site_rental_opex'] == 9600

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_psb_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental_opex'] == (
        setup_parameters['site_rental_urban_opex'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul_capex'] == (
        setup_parameters['wireless_small_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_moran_baseline_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    #These are urban, hence no sharing in a shared rural network
    assert round(cost_structure['equipment_capex']) == setup_parameters['equipment_capex']
    assert round(cost_structure['backhaul_capex']) == setup_parameters['wireless_small_capex']
    assert round(cost_structure['core_edge_capex']) == round(
        (setup_parameters['core_edge_capex'] * 1000))
    assert round(cost_structure['core_node_capex']) == round(
        (setup_parameters['core_node_epc_capex'] * 2))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert round(cost_structure['equipment_capex']) == round(
        setup_parameters['equipment_capex'] * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'urban'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_wireless_srn_srn_baseline_baseline',
        setup_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['equipment_capex'] == (
        setup_parameters['equipment_capex'])
    assert cost_structure['core_edge_capex'] == (
        (setup_parameters['core_edge_capex'] * 1000))


def test_backhaul_quantity():
    """
    Unit test.

    """
    assert backhaul_quantity(2, 1) == 0


def test_get_backhaul_capex(setup_region, setup_core_lut,
    setup_parameters, setup_empty_core_lut):
    """
    Unit test.

    """
    assert get_backhaul_capex(setup_region[0], 'wireless', setup_parameters,
        setup_core_lut) == (setup_parameters['wireless_small_capex'])

    setup_region[0]['area_km2'] = 5000

    assert get_backhaul_capex(setup_region[0], 'wireless',setup_parameters,
        setup_core_lut) == (setup_parameters['wireless_small_capex'])

    setup_region[0]['area_km2'] = 20000

    assert get_backhaul_capex(setup_region[0], 'wireless', setup_parameters,
        setup_core_lut) == (setup_parameters['wireless_medium_capex'])

    setup_region[0]['area_km2'] = 100000

    assert get_backhaul_capex(setup_region[0], 'wireless', setup_parameters,
        setup_core_lut) == (setup_parameters['wireless_large_capex'] * (55901.69943749474 / 30000))

    setup_region[0]['area_km2'] = 2

    assert get_backhaul_capex(setup_region[0], 'fiber', setup_parameters,
        setup_core_lut) == (setup_parameters['fiber_urban_m_capex'] * 250)

    assert get_backhaul_capex(setup_region[0], 'incorrect_backhaul_tech_name', setup_parameters,
        setup_core_lut) == 0

    assert get_backhaul_capex(setup_region[0], 'fiber', setup_parameters,
        setup_empty_core_lut) == 14140


def test_regional_net_capex(setup_region, setup_parameters, setup_core_lut,
    setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['total_estimated_sites'] = 6
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 6

    assert regional_net_capex(setup_region[0], 'regional_edge', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == (
            (setup_parameters['regional_edge_capex'] * setup_core_lut['regional_edge']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    assert regional_net_capex(setup_region[0], 'regional_node', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == (
            (setup_parameters['regional_node_epc_capex'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    setup_region[0]['total_estimated_sites'] = 10
    setup_region[0]['new_mno_sites'] = 10

    assert regional_net_capex(setup_region[0], 'regional_node', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == (
            (setup_parameters['regional_node_epc_capex'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    setup_core_lut['regional_node']['MWI.1.1.1_1'] = 10
    setup_region[0]['area_km2'] = 100

    assert regional_net_capex(setup_region[0], 'regional_node', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == (
            (setup_parameters['regional_node_epc_capex'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    assert regional_net_capex(setup_region[0], 'incorrrect_asset_name', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 'Asset name not in lut'

    setup_region[0]['total_estimated_sites'] = 0
    setup_region[0]['new_mno_sites'] = 0

    assert regional_net_capex(setup_region[0], 'regional_node', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 0

    setup_region[0]['GID_id'] = 'unknown GID ID'

    assert regional_net_capex(setup_region[0], 'regional_node', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 0

    #test that no sites returns zero cost
    setup_region[0]['total_estimated_sites'] = 0

    assert regional_net_capex(setup_region[0], 'regional_edge', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 0

    #test asset name not being in the LUT
    assert regional_net_capex(setup_region[0], 'incorrrect_asset_name', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 'Asset name not in lut'


def test_core_capex(setup_region, setup_parameters, setup_core_lut, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1
    setup_region[0]['total_estimated_sites'] = 2
    setup_country_parameters['networks']['baseline_urban'] = 2

    assert core_capex(setup_region[0], 'core_edge', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == (
            setup_parameters['core_edge_capex'] * 1000)

    assert core_capex(setup_region[0], 'core_node', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == (
            setup_parameters['core_node_{}_capex'.format('epc')] * 2)

    assert core_capex(setup_region[0], 'incorrrect_asset_name', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 0

    setup_region[0]['GID_id'] == 'unknown'

    assert core_capex(setup_region[0], 'core_edge', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == (
            (setup_parameters['core_edge_capex'] * setup_core_lut['core_edge']['MWI.1.1.1_1_new']) /
            (setup_region[0]['total_estimated_sites'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    #test that no sites returns zero cost
    setup_region[0]['upgraded_mno_sites'] = 0
    setup_region[0]['new_mno_sites'] = 0

    assert core_capex(setup_region[0], 'core_edge', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 0

    assert core_capex(setup_region[0], 'core_node', setup_parameters,
        setup_core_lut, setup_parameters['strategy'], setup_country_parameters) == 0

    assert core_capex(setup_region[0], 'core_edge', setup_parameters,
        {}, setup_parameters['strategy'], setup_country_parameters) == 0

    assert core_capex(setup_region[0], 'core_node', setup_parameters,
        {}, setup_parameters['strategy'], setup_country_parameters) == 0


def test_calc_costs(setup_region, setup_parameters, setup_country_parameters):
    """
    Unit test.

    """
    setup_region[0]['sites_4G'] = 0
    setup_region[0]['upgraded_mno_sites'] = 1
    setup_region[0]['new_mno_sites'] = 1

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline',
        {'equipment_capex': 40000},
        1,
        setup_parameters,
        setup_country_parameters
    )

    assert answer == 40000 * (1 + (setup_country_parameters['financials']['wacc'] / 100))

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline',
        {'site_rental_opex': 9600},
        1,
        setup_parameters,
        setup_country_parameters
    )

    assert answer == 18743 *  (1 + (setup_country_parameters['financials']['wacc'] / 100))#two years' of rent
    assert structure['ran_opex'] == 21554.449999999997

    answer, structure = calc_costs(setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline',
        {
        'equipment_capex': 40000,
        'site_rental_opex': 9600,
        },
        6,
        setup_parameters,
        setup_country_parameters)

    #answer = sum of equipment + site_rental
    assert answer == (
        40000 * (1 + (setup_country_parameters['financials']['wacc'] / 100)) +
        18743 *  (1 + (setup_country_parameters['financials']['wacc'] / 100))
        )
    assert structure['ran_capex'] == 46000.0

    answer, structure = calc_costs(setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline',
        {
        'core_edge_opex': 10,
        'core_node_opex': 10,
        },
        6,
        setup_parameters,
        setup_country_parameters)

    #answer = sum of equipment + site_rental
    assert answer == 23
    assert structure['core_opex'] == 23

    setup_country_parameters['financials']['wacc'] = 0
    setup_region[0]['upgraded_mno_sites'] = 0
    answer, structure = calc_costs(setup_region[0],
        '4G_epc_fiber_baseline_baseline_baseline_baseline_baseline',
        {
        'equipment_capex': 1,
        'backhaul_capex': 1,
        'site_build_capex': 1,
        'installation_capex': 1,
        'regional_node_capex': 1,
        'regional_edge_capex': 1,
        'core_node_capex': 1,
        'core_edge_capex': 1,
        'operation_and_maintenance_opex': 1,
        'site_rental_opex': 1,
        'power_opex': 1,
        'backhaul_opex': 1,
        'regional_node_opex': 1,
        'regional_edge_opex': 1,
        'core_node_opex': 1,
        'core_edge_opex': 1,
        },
        60,
        setup_parameters,
        setup_country_parameters)

    #answer = sum of equipment + site_rental
    assert answer == 24 #(15 is the length of the cost dict)
    assert structure['ran_capex'] == 1
    assert structure['ran_opex'] == 1 * 6 #(3 items of 10 over 2 years)
    assert structure['backhaul_capex'] == 1
    assert structure['backhaul_opex'] == 1 * 2
    assert structure['civils_capex'] == 1 * 2
    assert structure['core_capex'] == 1 * 4
    assert structure['core_opex'] == 1 * 8

    setup_country_parameters['financials']['wacc'] = 15

    answer, structure = calc_costs(setup_region[0],
        '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline',
        {
        'incorrect_name': 9600,
        },
        6,
        setup_parameters,
        setup_country_parameters)

    assert answer == 'Did not recognize cost type'


def test_discount_opex(setup_parameters, setup_country_parameters):
    """
    Unit test.

    """
    assert discount_opex(1000, setup_parameters, setup_country_parameters) == (
        1952 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))
