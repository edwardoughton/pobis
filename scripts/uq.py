"""
Generate sensitivity analysis options.

"""
import os
import configparser
import pandas as pd

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')


def generate_uq(global_parameters, costs):
    """
    Function to generate uncertainty quantification inputs:

    """
    strategies = [
        #baseline
        ('technology_options', '3G_epc_wireless_baseline_baseline_baseline_baseline'),
        ('technology_options', '3G_epc_fiber_baseline_baseline_baseline_baseline'),
        ('technology_options', '4G_epc_wireless_baseline_baseline_baseline_baseline'),
        ('technology_options', '4G_epc_fiber_baseline_baseline_baseline_baseline'),
        #3g wireless sharing
        ('business_model_options', '3G_epc_wireless_psb_baseline_baseline_baseline_baseline'),
        ('business_model_options', '3G_epc_wireless_moran_baseline_baseline_baseline_baseline'),
        ('business_model_options', '3G_epc_wireless_srn_srn_baseline_baseline_baseline'),
        #3g fiber sharing
        ('business_model_options', '3G_epc_fiber_psb_baseline_baseline_baseline_baseline'),
        ('business_model_options', '3G_epc_fiber_moran_baseline_baseline_baseline_baseline'),
        ('business_model_options', '3G_epc_fiber_srn_srn_baseline_baseline_baseline'),
        #4g wireless sharing
        ('business_model_options', '4G_epc_wireless_psb_baseline_baseline_baseline_baseline'),
        ('business_model_options', '4G_epc_wireless_moran_baseline_baseline_baseline_baseline'),
        ('business_model_options', '4G_epc_wireless_srn_srn_baseline_baseline_baseline'),
        #4g fiber sharing
        ('business_model_options', '4G_epc_fiber_psb_baseline_baseline_baseline_baseline'),
        ('business_model_options', '4G_epc_fiber_moran_baseline_baseline_baseline_baseline'),
        ('business_model_options', '4G_epc_fiber_srn_srn_baseline_baseline_baseline'),
    ]

    scenarios = [
        'high',
        'baseline',
        'low'
    ]

    capacities = [
        10,
        20,
        30
    ]

    input_costs = [
        60,
        80,
        100,
        120,
        140,
    ]

    output = []
    iteration = 0

    for strategy in strategies:
        for scenario in scenarios:
            for input_cost in input_costs:
                for capacity in capacities:

                    scenario_handle = '{}_{}_{}_{}'.format(
                        scenario,
                        capacity,
                        capacity,
                        capacity
                    )

                    output.append({
                        'iteration': iteration,
                        'decision_option': strategy[0],
                        'strategy': strategy[1],
                        'scenario': scenario_handle,
                        'cost_perc': input_cost,
                        'capacity': capacity,
                        #global params
                        'return_period': global_parameters['return_period'],
                        'discount_rate': global_parameters['discount_rate'],
                        'opex_percentage_of_capex': global_parameters['opex_percentage_of_capex'],
                        'confidence': global_parameters['confidence'],
                        'traffic_in_the_busy_hour_perc': global_parameters['traffic_in_the_busy_hour_perc'],
                        #costs
                        'equipment_capex': 40000 * (input_cost/100),
                        'site_build_capex': 30000 * (input_cost/100),
                        'installation_capex': 30000 * (input_cost/100),
                        'operation_and_maintenance_opex': 7400 * (input_cost/100),
                        'power_opex': 3000 * (input_cost/100),
                        'site_rental_urban_opex': 10000 * (input_cost/100),
                        'site_rental_suburban_opex': 5000 * (input_cost/100),
                        'site_rental_rural_opex': 3000 * (input_cost/100),
                        'fiber_urban_m_capex': 25 * (input_cost/100),
                        'fiber_suburban_m_capex': 15 * (input_cost/100),
                        'fiber_rural_m_capex': 10 * (input_cost/100),
                        'wireless_small_capex': 15000 * (input_cost/100),
                        'wireless_medium_capex': 20000 * (input_cost/100),
                        'wireless_large_capex': 45000 * (input_cost/100),
                        'core_node_epc_capex': 500000 * (input_cost/100),
                        'core_edge_capex': 25 * (input_cost/100),
                        'regional_node_epc_capex': 200000 * (input_cost/100),
                        'regional_edge_capex': 25 * (input_cost/100),
                    })

                    iteration += 1

    output = pd.DataFrame(output)
    path = os.path.join(DATA_INTERMEDIATE, 'uq_inputs.csv')
    output.to_csv(path, index=False)

    return output


if __name__ == '__main__':

    GLOBAL_PARAMETERS = {
        # 'overbooking_factor': 20,
        'return_period': 10,
        'discount_rate': 5,
        'opex_percentage_of_capex': 10,
        'confidence': 50,#[5, 50, 95]
        'traffic_in_the_busy_hour_perc': 15,
        }

    COSTS = {
        #all costs in $USD
        'equipment_capex': 40000,
        'site_build_capex': 30000,
        'installation_capex': 30000,
        'operation_and_maintenance_opex': 7400,
        'power_opex': 3000,
        'site_rental_urban_opex': 10000,
        'site_rental_suburban_opex': 5000,
        'site_rental_rural_opex': 3000,
        'fiber_urban_m_capex': 25,
        'fiber_suburban_m_capex': 15,
        'fiber_rural_m_capex': 10,
        'wireless_small_capex': 15000,
        'wireless_medium_capex': 20000,
        'wireless_large_capex': 45000,
        'core_node_epc_capex': 500000,
        'core_edge_capex': 25,
        'regional_node_epc_capex': 200000,
        'regional_edge_capex': 25,
    }

    options = generate_uq(GLOBAL_PARAMETERS, COSTS)
