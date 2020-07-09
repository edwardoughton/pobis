import pytest
import math
from podis.costs import (upgrade_to_3g, upgrade_to_4g,
    greenfield_3g, greenfield_4g, backhaul_quantity,
    get_fronthaul_costs, get_backhaul_costs,
    regional_net_costs, core_costs, discount_opex,
    discount_capex_and_opex, calc_costs,
    find_single_network_cost)

#test approach is to:
#test each function which returns the cost structure
#test the function which calculates quantities
#test infrastructure sharing strategies
#test meta cost function

def test_upgrade_to_3g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):

    setup_region[0]['sites_estimated_total'] = 1
    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['new_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['io_fronthaul'] ==1500
    assert cost_structure['site_rental'] == 9600

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_pss_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban']  /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])

    assert cost_structure['backhaul'] == (
        setup_costs['microwave_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] /
        setup_country_parameters['networks']['baseline_urban'])

    assert cost_structure['bbu_cabinet'] == (
        setup_costs['bbu_cabinet'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_cns_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000) *
        (1 /
        setup_country_parameters['networks']['baseline_urban']))

    assert cost_structure['core_node'] == (
        (setup_costs['core_node_epc'] * 2) *
        (setup_region[0]['sites_estimated_total'] /
        setup_country_parameters['networks']['baseline_urban']))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_cns_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit']) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000)) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )

    setup_region[0]['geotype'] = 'urban'

    cost_structure = upgrade_to_3g(setup_region[0],
        '3G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_upgrade_to_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):

    setup_region[0]['sites_estimated_total'] = 1
    setup_region[0]['new_sites'] = 1
    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['io_fronthaul'] ==1500
    assert cost_structure['site_rental'] == 9600

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_pss_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_4g(setup_region[0],
        '4g_epc_microwave_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul'] == (
        setup_costs['microwave_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_4g(setup_region[0],
        '4g_epc_microwave_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['bbu_cabinet'] == (
        setup_costs['bbu_cabinet'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000)  * (1 /
        setup_country_parameters['networks']['baseline_rural']
        ))
    assert cost_structure['core_node'] == (
        (setup_costs['core_node_epc'] * 2)  * (1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_cns_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit']) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000)) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )

    setup_region[0]['geotype'] = 'urban'

    cost_structure = upgrade_to_4g(setup_region[0],
        '4G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_greenfield_3g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):

    setup_region[0]['sites_estimated_total'] = 1
    setup_region[0]['new_sites'] = 1
    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['io_fronthaul'] == 1500
    assert cost_structure['site_rental'] == 9600

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_pss_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['tower'] == (
        setup_costs['tower'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['installation'] == (
        setup_costs['installation'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul'] == (
        setup_costs['microwave_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['bbu_cabinet'] == (
        setup_costs['bbu_cabinet'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_cns_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000)  * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))
    assert cost_structure['core_node'] == (
        (setup_costs['core_node_epc'] * 2)  * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_cns_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit']) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000)) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )

    setup_region[0]['geotype'] = 'urban'

    cost_structure = greenfield_3g(setup_region[0],
        '3G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_greenfield_4g(setup_region, setup_option, setup_costs,
    setup_global_parameters, setup_core_lut,
    setup_country_parameters):

    setup_region[0]['sites_estimated_total'] = 1
    setup_region[0]['new_sites'] = 1
    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['site_density'] = 0.5

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_baseline_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_sector_antenna'] == 1500
    assert cost_structure['single_remote_radio_unit'] == 4000
    assert cost_structure['io_fronthaul'] == 1500
    assert cost_structure['site_rental'] == 9600

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_pss_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['tower'] == (
        setup_costs['tower'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['installation'] == (
        setup_costs['installation'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_psb_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['site_rental'] == (
        setup_costs['site_rental_urban'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['backhaul'] == (
        setup_costs['microwave_small'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_moran_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] /
        setup_country_parameters['networks']['baseline_urban'])
    assert cost_structure['bbu_cabinet'] == (
        setup_costs['bbu_cabinet'] /
        setup_country_parameters['networks']['baseline_urban'])

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000)  * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))
    assert cost_structure['core_node'] == (
        (setup_costs['core_node_epc'] * 2)  * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_cns_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'] * (
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        ))

    setup_region[0]['geotype'] = 'rural'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit']) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000)) * (  # 20*1000
        1 /
        setup_country_parameters['networks']['baseline_rural']
        )

    setup_region[0]['geotype'] = 'urban'

    cost_structure = greenfield_4g(setup_region[0],
        '4G_epc_microwave_baseline_srn_baseline_baseline',
        setup_costs, setup_global_parameters,
        setup_core_lut, setup_country_parameters)

    assert cost_structure['single_remote_radio_unit'] == (
        setup_costs['single_remote_radio_unit'])
    assert cost_structure['core_edge'] == (
        (setup_costs['core_edge'] * 1000))


def test_backhaul_quantity():

    assert backhaul_quantity(2, 1) == 0


def test_get_fronthaul_costs(setup_region, setup_costs):

    setup_region[0]['site_density'] = 4

    assert get_fronthaul_costs(setup_region[0], setup_costs) == (
        setup_costs['fiber_urban_m'] * math.sqrt(1/setup_region[0]['site_density'])) * 1000

    setup_region[0]['site_density'] = 0.5

    assert get_fronthaul_costs(setup_region[0], setup_costs) == (
        setup_costs['fiber_urban_m'] * math.sqrt(1/setup_region[0]['site_density'])) * 1000

    setup_region[0]['site_density'] = 0.00001

    assert get_fronthaul_costs(setup_region[0], setup_costs) == (
        setup_costs['fiber_urban_m'] * math.sqrt(1/setup_region[0]['site_density'])) * 1000


def test_get_backhaul_costs(setup_region, setup_costs, setup_core_lut, setup_empty_core_lut):

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, setup_core_lut) == (setup_costs['microwave_small'])

    setup_region[0]['area_km2'] = 5000

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, setup_core_lut) == (setup_costs['microwave_small'])

    setup_region[0]['area_km2'] = 20000

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, setup_core_lut) == (setup_costs['microwave_medium'])

    setup_region[0]['area_km2'] = 100000

    assert get_backhaul_costs(setup_region[0], 'microwave',
        setup_costs, setup_core_lut) == (setup_costs['microwave_large'] * (55901.69943749474 / 30000))

    setup_region[0]['area_km2'] = 2

    assert get_backhaul_costs(setup_region[0], 'fiber',
        setup_costs, setup_core_lut) == (setup_costs['fiber_urban_m'] * 250)

    assert get_backhaul_costs(setup_region[0], 'incorrect_backhaul_tech_name',
        setup_costs, setup_core_lut) == 0

    assert get_backhaul_costs(setup_region[0], 'fiber',
        setup_costs, setup_empty_core_lut) == 14140


def test_regional_net_costs(setup_region, setup_option, setup_costs, setup_core_lut,
    setup_country_parameters):

    setup_region[0]['sites_estimated_total'] = 6
    setup_region[0]['upgraded_sites'] = 0
    setup_region[0]['new_sites'] = 6

    assert regional_net_costs(setup_region[0], 'regional_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_edge'] * setup_core_lut['regional_edge']['MWI.1.1.1_1_new']) /
            (setup_region[0]['sites_estimated_total'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['sites_estimated_total'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    setup_region[0]['sites_estimated_total'] = 10
    setup_region[0]['new_sites'] = 10

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['sites_estimated_total'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    setup_core_lut['regional_node']['MWI.1.1.1_1'] = 10
    setup_region[0]['area_km2'] = 100

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == (
            (setup_costs['regional_node_epc'] * setup_core_lut['regional_node']['MWI.1.1.1_1_new']) /
            (setup_region[0]['sites_estimated_total'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    assert regional_net_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 'Asset name not in lut'

    setup_region[0]['sites_estimated_total'] = 0
    setup_region[0]['new_sites'] = 0

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    setup_region[0]['GID_id'] = 'unknown GID ID'

    assert regional_net_costs(setup_region[0], 'regional_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    #test that no sites returns zero cost
    setup_region[0]['sites_estimated_total'] = 0

    assert regional_net_costs(setup_region[0], 'regional_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    #test asset name not being in the LUT
    assert regional_net_costs(setup_region[0], 'incorrrect_asset_name', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 'Asset name not in lut'


def test_core_costs(setup_region, setup_option, setup_costs, setup_core_lut, setup_country_parameters):

    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['new_sites'] = 1
    setup_region[0]['sites_estimated_total'] = 2
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
            (setup_region[0]['sites_estimated_total'] /
            (setup_country_parameters['networks']['baseline_urban'])))

    #test that no sites returns zero cost
    setup_region[0]['upgraded_sites'] = 0
    setup_region[0]['new_sites'] = 0

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    assert core_costs(setup_region[0], 'core_node', setup_costs,
        setup_core_lut, setup_option['strategy'], setup_country_parameters) == 0

    assert core_costs(setup_region[0], 'core_edge', setup_costs,
        {}, setup_option['strategy'], setup_country_parameters) == 0

    assert core_costs(setup_region[0], 'core_node', setup_costs,
        {}, setup_option['strategy'], setup_country_parameters) == 0


def test_discount_capex_and_opex(setup_global_parameters, setup_country_parameters):

    assert discount_capex_and_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1195 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))


def test_discount_opex(setup_global_parameters, setup_country_parameters):

    assert discount_opex(1000, setup_global_parameters, setup_country_parameters) == (
        1952 * (1 + (setup_country_parameters['financials']['wacc'] / 100)))


def test_calc_costs(setup_region, setup_global_parameters, setup_country_parameters):

    setup_region[0]['sites_4G'] = 0
    setup_region[0]['upgraded_sites'] = 1
    setup_region[0]['new_sites'] = 1

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline_baseline',
        {'single_sector_antenna': 1500},
        1,
        setup_global_parameters,
        setup_country_parameters
    )

    assert answer == 5379 * (1 + (setup_country_parameters['financials']['wacc'] / 100))

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline_baseline',
        {'single_baseband_unit': 4000},
        1,
        setup_global_parameters,
        setup_country_parameters
    )

    assert answer == 4781 * (1 + (setup_country_parameters['financials']['wacc'] / 100))

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline_baseline',
        {'tower': 10000},
        1,
        setup_global_parameters,
        setup_country_parameters
    )

    assert answer == 10000

    answer, structure = calc_costs(
        setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline_baseline',
        {'site_rental': 9600},
        1,
        setup_global_parameters,
        setup_country_parameters
    )

    assert answer == 18743 *  (1 + (setup_country_parameters['financials']['wacc'] / 100))#two years' of rent

    answer, structure = calc_costs(setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline_baseline',
        {
        'single_sector_antenna': 1500,
        'single_baseband_unit': 4000,
        'tower': 10000,
        'site_rental': 9600
        },
        6,
        setup_global_parameters,
        setup_country_parameters)

    #answer = sum of antenna, bbu, tower, site_rental (5379 + 4781 + 10000 + 18743)
    assert answer == (
        (5379 + 4781 + 18743) *
        (1 + (setup_country_parameters['financials']['wacc'] / 100)) +
        10000) # <- no opex on the tower

    answer, structure = calc_costs(setup_region[0],
        '4G_epc_microwave_cns_baseline_baseline_baseline_baseline',
        {
        'incorrect_name': 9600,
        },
        6,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 0 #two years' of rent

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_baseline',
        {
        'cots_processing': 6,
        'io_n2_n3': 6,
        'low_latency_switch': 6,
        'rack': 6,
        'cloud_power_supply_converter': 6,
        'software': 6,
        },
        1,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == sum([
        8 * 1.15, #cots_processing = capex + opex
        8 * 1.15, #io_n2_n3 = capex + opex
        8 * 1.15, #low_latency_switch = capex + opex
        6, #rack = capex
        8 * 1.15, #cloud_power_supply_converter = capex + opex
        12 * 1.15,#software = opex
    ])

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_baseline',
        {'backhaul': 100,},
        1,
        setup_global_parameters,
        setup_country_parameters
    )

    assert answer == 120 * (1 + (setup_country_parameters['financials']['wacc'] / 100))

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_baseline',
        {'backhaul': 100},
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 0

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_baseline',
        {'bbu_cabinet': 100},
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 100

    setup_region[0]['integration'] = 'integration'

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_integration',
        {'bbu_cabinet': 100},
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 90

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_integration',
        {'single_remote_radio_unit': 4000},
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 4948.335

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_integration',
        {'per_site_spectrum_acquisition_cost': 100},
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 50

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_integration',
        {'site_rental': 1000},
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 2020.3199999999997

    answer, structure = calc_costs(setup_region[0],
        '5G_sa_microwave_cns_baseline_baseline_baseline_integration',
        {'per_site_administration_cost': 100},
        0,
        setup_global_parameters,
        setup_country_parameters)

    assert answer == 224.24999999999997 / 2

# # # def test_find_single_network_cost(setup_region, setup_costs,
# # #     setup_global_parameters, setup_country_parameters,
# # #     setup_backhaul_lut, setup_core_lut):

# # #     setup_region[0]['sites_4G'] = 0
# # #     setup_region[0]['new_sites'] = 1
# # #     setup_region[0]['upgraded_sites'] = 1
# # #     setup_region[0]['site_density'] = 0.5
# # #     setup_region[0]['backhaul_new'] = 0

# # #     answer = find_single_network_cost(
# # #         setup_region[0],
# # #         {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
# # #         setup_costs,
# # #         setup_global_parameters,
# # #         setup_country_parameters,
# # #         setup_backhaul_lut,
# # #         setup_core_lut
# # #     )

# # #     #~42k is a single 4G upgraded site
# # #     #~68k is a single 4G greenfield site
# # #     assert answer['network_cost'] == 1138228

# # #     setup_region[0]['sites_4G'] = 0
# # #     setup_region[0]['new_sites'] = 1
# # #     setup_region[0]['upgraded_sites'] = 1
# # #     setup_region[0]['site_density'] = 0.5
# # #     setup_region[0]['backhaul_new'] = 1

# # #     answer = find_single_network_cost(
# # #         setup_region[0],
# # #         {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
# # #         setup_costs,
# # #         setup_global_parameters,
# # #         setup_country_parameters,
# # #         setup_backhaul_lut,
# # #         setup_core_lut
# # #     )

# # #     #42k is a single 4G upgraded site
# # #     #68k is a single 4G greenfield site
# # #     #11952 is a new backhaul (10k capex + opex of 1952)
# # #     assert answer['network_cost'] == (110322 + 11952 + 1027906)

# # #     setup_region[0]['sites_4G'] = 0
# # #     setup_region[0]['new_sites'] = 1
# # #     setup_region[0]['upgraded_sites'] = 1
# # #     setup_region[0]['site_density'] = 0.5
# # #     setup_region[0]['backhaul_new'] = 2

# # #     answer = find_single_network_cost(
# # #         setup_region[0],
# # #         {'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline'},
# # #         setup_costs,
# # #         setup_global_parameters,
# # #         setup_country_parameters,
# # #         setup_backhaul_lut,
# # #         setup_core_lut
# # #     )

# #     # #42189 is a single 4G upgraded site
# #     # #68165 is a single 4G greenfield site
# #     # #11952 is a new backhaul (10k capex + opex of 1952) * 2
# #     # assert answer['network_cost'] == (110322 + 11952 + 11952 + 1027906)

# #     # answer = find_single_network_cost(
# #     #     setup_region[0],
# #     #     {'strategy': '5G_sa_microwave_baseline_baseline_baseline_baseline'},
# #     #     setup_costs,
# #     #     setup_global_parameters,
# #     #     setup_country_parameters,
# #     #     setup_backhaul_lut,
# #     #     setup_core_lut
# #     # )

# #     # assert answer['network_cost'] == (110322 + 11952 + 11952 + 1027906)

# #     # setup_region[0]['new_sites'] = 0
# #     # setup_region[0]['upgraded_sites'] = 1
# #     # setup_region[0]['site_density'] = 0.5
# #     # setup_region[0]['backhaul_new'] = 0

# #     # answer = find_single_network_cost(
# #     #     setup_region[0],
# #     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
# #     #     setup_costs,
# #     #     setup_global_parameters,
# #     #     setup_country_parameters,
# #     #     setup_backhaul_lut,
# #     #     setup_core_lut
# #     # )

# #     # assert answer['network_cost'] == 63357.0 + 1027906

# #     # setup_region[0]['new_sites'] = 0
# #     # setup_region[0]['upgraded_sites'] = 1
# #     # setup_region[0]['site_density'] = 0.5
# #     # setup_region[0]['backhaul_new'] = 1

# #     # answer = find_single_network_cost(
# #     #     setup_region[0],
# #     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
# #     #     setup_costs,
# #     #     setup_global_parameters,
# #     #     setup_country_parameters,
# #     #     setup_backhaul_lut,
# #     #     setup_core_lut
# #     # )

# #     # assert answer['network_cost'] == 63357 + 1027906

# #     # setup_region[0]['new_sites'] = 1
# #     # setup_region[0]['upgraded_sites'] = 1
# #     # setup_region[0]['site_density'] = 0.5
# #     # setup_region[0]['backhaul_new'] = 2

# #     # answer = find_single_network_cost(
# #     #     setup_region[0],
# #     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
# #     #     setup_costs,
# #     #     setup_global_parameters,
# #     #     setup_country_parameters,
# #     #     setup_backhaul_lut,
# #     #     setup_core_lut
# #     # )

# #     # assert answer['network_cost'] == 152690 + 1027906

# #     # setup_region[0]['new_sites'] = 1
# #     # setup_region[0]['upgraded_sites'] = 0
# #     # setup_region[0]['site_density'] = 0.001
# #     # setup_region[0]['backhaul_new'] = 1

# #     # answer = find_single_network_cost(
# #     #     setup_region[0],
# #     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
# #     #     setup_costs,
# #     #     setup_global_parameters,
# #     #     setup_country_parameters,
# #     #     setup_backhaul_lut,
# #     #     setup_core_lut
# #     # )

# #     # assert answer['network_cost'] == 450398.0 + 1027906

# #     # setup_region[0]['new_sites'] = 10
# #     # setup_region[0]['upgraded_sites'] = 10
# #     # setup_region[0]['site_density'] = 1
# #     # setup_region[0]['backhaul_new'] = 20

# #     # answer = find_single_network_cost(
# #     #     setup_region[0],
# #     #     {'strategy': '5G_sa_fiber_baseline_baseline_baseline_baseline'},
# #     #     setup_costs,
# #     #     setup_global_parameters,
# #     #     setup_country_parameters,
# #     #     setup_backhaul_lut,
# #     #     setup_core_lut
# #     # )

# #     # assert answer['network_cost'] == 1451800.0 + 1027906
