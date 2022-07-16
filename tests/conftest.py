from pytest import fixture


@fixture(scope='function')
def setup_region():
    return [{
    'GID_0': 'MWI',
    'GID_id': 'MWI.1.1.1_1',
    'mean_luminosity_km2': 26.736407691655717,
    'population': 10000,
    'pop_under_10_pop': 0,
    'area_km2': 2,
    'population_km2': 5000,
    'decile': 100,
    'geotype': 'urban',
    'demand_mbps_km2': 5000,
    'integration': 'baseline'
    }]


@fixture(scope='function')
def setup_region_rural():
    return [{
    'GID_0': 'MWI',
    'GID_id': 'MWI.1.1.1_1',
    'mean_luminosity_km2': 26.736407691655717,
    'population': 10000,
    'pop_under_10_pop': 0,
    'area_km2': 2,
    'population_km2': 5000,
    'decile': 100,
    'geotype': 'rural'
    }]


@fixture(scope='function')
def setup_parameters():
    return {
        #options
        'scenario': 'S1_50_50_50',
        'strategy': '4G_epc_wireless_baseline_baseline_baseline_baseline_baseline_baseline',
        'input_cost': 'baseline',
        #global params
        'opex_percentage_of_capex': 10,
        'traffic_in_the_busy_hour_perc': 20,
        'return_period': 2,
        'discount_rate': 5,
        'confidence': [1, 10, 50],
        'regional_integration_factor': 10,
        'confidence': 50,
        #all costs in $USD
        'equipment_capex': 40000,
        'site_build_capex': 30000,
        'installation_capex': 30000,
        'operation_and_maintenance_opex': 7400,
        'power_opex': 2200,
        'site_rental_urban_opex': 9600,
        'site_rental_suburban_opex': 4000,
        'site_rental_rural_opex': 2000,
        'fiber_urban_m_capex': 10,
        'fiber_suburban_m_capex': 5,
        'fiber_rural_m_capex': 2,
        'wireless_small_capex': 10000,
        'wireless_medium_capex': 20000,
        'wireless_large_capex': 40000,
        'core_node_epc_capex': 100000,
        'core_edge_capex': 20,
        'regional_node_epc_capex': 100000,
        'regional_edge_capex': 10,
    }


@fixture(scope='function')
def setup_country_parameters():
    return {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 15,
            'medium': 5,
            'low': 2,
        },
        'networks': {
            'baseline_urban': 3,
            'baseline_suburban': 3,
            'baseline_rural': 3,
            'srn_urban': 3,
            'srn_suburban': 3,
            'srn_rural': 1,
        },
        'frequencies': {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x50',
                },
            ]
        },
        'financials': {
            'wacc': 15,
            'profit_margin': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 1,
            'spectrum_capacity_baseline_usd_mhz_pop': 1,
            'spectrum_cost_low': 50,
            'spectrum_cost_high': 50,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            'acquisition_per_subscriber': 10,
            'administration_percentage_of_network_cost': 10
            },
        }


@fixture(scope='function')
def setup_timesteps():
    return [
        2020,
        # 2021,
        # 2022,
        # 2023,
        # 2024,
        # 2025,
        # 2026,
        # 2027,
        # 2028,
        # 2029,
        # 2030
    ]


@fixture(scope='function')
def setup_penetration_lut():
    return {
        2020: 50,
        # 2021: 75,
    }


@fixture(scope='function')
def setup_lookup():
    return {
        ('urban', 'macro', '800', '4G', '50'): [
            (0.01, 1),
            (0.02, 2),
            (0.05, 5),
            (0.15, 15),
            (2, 100)
        ],
        ('urban', 'macro', '1800', '4G', '50'): [
            (0.01, 5),
            (0.02, 10),
            (0.05, 20),
            (0.15, 40),
            (2, 1000)
        ],
    }


@fixture(scope='function')
def setup_ci():
    return 50

@fixture(scope='function')
def setup_core_lut():
    return {
        'core_edge': {
            'MWI.1.1.1_1_new': 1000,
            'MWI.1.1.1_1_existing': 1000
        },
        'core_node': {
            'MWI.1.1.1_1_new': 2,
            'MWI.1.1.1_1_existing': 2
        },
        'regional_edge': {
            'MWI.1.1.1_1_new': 1000,
            'MWI.1.1.1_1_existing': 1000
        },
        'regional_node': {
            'MWI.1.1.1_1_new': 2,
            'MWI.1.1.1_1_existing': 2
        },
    }

@fixture(scope='function')
def setup_empty_core_lut():
    return {
        'core_edge': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
        'core_node': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
        'regional_edge': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
        'regional_node': {
            'MWI.1.1.1_1_new': 0,
            'MWI.1.1.1_1_existing': 0
        },
    }
