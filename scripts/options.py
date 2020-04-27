"""
Options consisting of scenarios and strategies.

Country parameters consist of those parameters which are specific
to each country.

Written by Ed Oughton

January 2020

#strategy is defined based on generation_core_backhaul_sharing_subsidy_spectrum_tax_integration

"""
OPTIONS = {
    'technology_options': [
        {
            'scenario': 'S1_2_2_2',
            'strategy': '3G_epc_microwave_baseline_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_2_2_2',
            'strategy': '3G_epc_fiber_baseline_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_2_2_2',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_2_2_2',
            'strategy': '4G_epc_fiber_baseline_baseline_baseline_baseline_baseline',
        },
    ],
    'business_model_options': [
        {
            'scenario': 'S1_2_2_2',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_2_2_2',
            'strategy': '4G_epc_microwave_passive_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_2_2_2',
            'strategy': '4G_epc_microwave_active_baseline_baseline_baseline_baseline',
        },
    ],
    'policy_options': [
        {
            'scenario': 'S1_2_2_2',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline_baseline',
        },
        {
            'scenario': 'S1_2_2_2',
            'strategy': '4G_epc_microwave_baseline_baseline_baseline_baseline_integration',
        },
    ]
}


COUNTRY_PARAMETERS = {
    'CIV': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 10,
            'medium': 7,
            'low': 5,
        },
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '3G': [
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2100,
                    'bandwidth': 10,
                },
            ],
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 5,
            'subsidy_high': 20,
            'spectrum_coverage_baseline_usd_mhz_pop': 2,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.5,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },
    'KEN': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 12,
            'medium': 9,
            'low': 5,
        },
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '3G': [
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2100,
                    'bandwidth': 10,
                },
            ],
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.2,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },
    'MLI': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 15,
            'medium': 10,
            'low': 5,
        },
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '3G': [
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2100,
                    'bandwidth': 10,
                },
            ],
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.3,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },
    'SEN': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 10,
            'medium': 8,
            'low': 5,
        },
        'smartphone_pen': 0.5,
        'networks': 3,
        'proportion_of_sites': 50,
        'frequencies': {
            '3G': [
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2100,
                    'bandwidth': 10,
                },
            ],
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.3,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },
    'TZA': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 10,
            'medium': 3,
            'low': 2,
        },
        'networks': 2,
        'proportion_of_sites': 50,
        'frequencies': {
            '3G': [
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2100,
                    'bandwidth': 10,
                },
            ],
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.3,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },
    'UGA': {
        'luminosity': {
            'high': 5,
            'medium': 1,
        },
        'arpu': {
            'high': 10,
            'medium': 3,
            'low': 2,
        },
        'networks': 2,
        'proportion_of_sites': 50,
        'frequencies': {
            '3G': [
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 2100,
                    'bandwidth': 10,
                },
            ],
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': 10,
                },
                {
                    'frequency': 1800,
                    'bandwidth': 10,
                },
            ],
        },
        'financials': {
            'profit_margin': 10,
            'subsidy_low': 10,
            'subsidy_high': 40,
            'spectrum_coverage_baseline_usd_mhz_pop': 0.3,
            'spectrum_capacity_baseline_usd_mhz_pop': 0.1,
            'tax_low': 10,
            'tax_baseline': 25,
            'tax_high': 40,
            },
        },
    }
