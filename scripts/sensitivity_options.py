"""
Generate sensitivity analysis options.

"""

def generate_sensitivity_options():
    """
    Function to generate sensitivity options based on the following:

    generation_core_backhaul_sharing_networks_spectrum_tax_obf_costs

    obf is overbooking factor and costs relates to the percentage
    change in the input cost.

    """
    scenarios = [
        # 'high',
        'baseline',
        # 'low'
    ]

    strategies = [
        # '3G_epc_wireless_baseline_baseline_baseline_baseline',
        # '3G_epc_fiber_baseline_baseline_baseline_baseline',
        '4G_epc_wireless_baseline_baseline_baseline_baseline',
        # '4G_epc_fiber_baseline_baseline_baseline_baseline',
    ]

    capacities = [
        '20',
        '10',
        '2'
    ]

    overbooking_factors = [
        15,
        20,
        25
    ]

    input_costs = [
        75,
        100,
        125,
    ]

    output = []

    for strategy in strategies:
        for overbooking_factor in overbooking_factors:
            for input_cost in input_costs:
                for scenario in scenarios:
                    for capacity in capacities:

                        option = {}

                        option['strategy'] = '{}_{}_{}'.format(
                            strategy, overbooking_factor, input_cost
                            )

                        option['scenario'] = '{}_{}_{}_{}'.format(
                            scenario, capacity, capacity, capacity
                            )

                        output.append(option)

    return output

if __name__ == '__main__':

    options = generate_sensitivity_options()

    print(options)
