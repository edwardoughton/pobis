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
        'high',
        'baseline',
        'low'
    ]

    strategies = [
        '3G_epc_wireless_baseline_baseline_baseline_baseline',
        '3G_epc_fiber_baseline_baseline_baseline_baseline',
        '4G_epc_wireless_baseline_baseline_baseline_baseline',
        '4G_epc_fiber_baseline_baseline_baseline_baseline',
    ]

    capacities = [
        '10',
        '20',
        '30'
    ]

    input_costs = [
        60,
        80,
        100,
        120,
        140,
    ]

    output = []

    for strategy in strategies:
        for scenario in scenarios:
            for input_cost in input_costs:
                for capacity in capacities:

                    output.append({
                        'strategy': strategy,
                        'scenario': scenario,
                        'cost_perc': input_cost,
                        'capacity': capacity
                    })

    return output


if __name__ == '__main__':

    options = generate_sensitivity_options()

    print(options)
