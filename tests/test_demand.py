import pytest
from podis.demand import (estimate_demand, get_per_user_capacity,
    estimate_arpu, discount_arpu)


def test_estimate_demand(
    setup_region,
    setup_region_rural,
    setup_option,
    setup_option_high,
    setup_global_parameters,
    setup_country_parameters,
    setup_timesteps,
    setup_penetration_lut
    ):

    answer = estimate_demand(
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        {2020: 50},
        {'MWI':{'urban': {'smartphone': 0.5}}}
    )

    # pop = 10000
    # pen = 50%
    # = 5000 phones
    assert answer[0]['population_with_phones'] == 5000

    # 5000 total phones
    # 2 networks
    # = 2500 phones on network
    assert round(answer[0]['phones_on_network']) == round(5000 / 2)

    # 5000 total phones
    # 2 networks
    # 2500 phones on network
    # 50% smartphones
    # = 1250 smartphones
    smartphones_on_network = round(5000 / 2 * (50 / 100))
    assert round(answer[0]['smartphones_on_network']) == smartphones_on_network

    # arpu = 15
    # 5000 phones
    # 2 networks
    # = $37,500
    assert round(answer[0]['total_revenue']) == round(15 * 5000 / 2)

    # $37,500 / 2 km2
    assert round(answer[0]['revenue_km2']) == round((15 * 5000 / 2) / 2)

    # 1250 smartphones
    # scenario = 50
    # overbooking factor = 100
    # area = 2
    # demand_mbps_km2 = 132
    assert round(answer[0]['demand_mbps_km2']) == round(
        smartphones_on_network * 50 / 100 / 2
    )

    #test that the region is dropped if the area is 0 km^2
    setup_region[0]['area_km2'] = 0

    answer = estimate_demand(
        setup_region,
        setup_option,
        setup_global_parameters,
        setup_country_parameters,
        setup_timesteps,
        {2020: 50},
        {'MWI':{'urban': {'smartphone': 0.5}}}
    )

    assert answer == []


def test_get_per_user_capacity():

    answer = get_per_user_capacity('urban', {'scenario': 'S1_25_5_1'})

    assert answer == 25

    answer = get_per_user_capacity('suburban', {'scenario': 'S1_25_5_1'})

    assert answer == 5

    answer = get_per_user_capacity('rural', {'scenario': 'S1_25_5_1'})

    assert answer == 1

    answer = get_per_user_capacity('made up geotype', {'scenario': 'S1_25_5_1'})

    assert answer == 'Did not recognise geotype'


def test_estimate_arpu(setup_region, setup_timesteps, setup_global_parameters,
    setup_country_parameters):

    answer = estimate_arpu({'mean_luminosity_km2': 10}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 15

    answer = estimate_arpu({'mean_luminosity_km2': 2}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 5

    answer = estimate_arpu({'mean_luminosity_km2': 0}, 2020, setup_global_parameters,
        setup_country_parameters)

    assert answer == 2


def test_discount_arpu(setup_global_parameters):

    arpu = 15
    timestep = 2
    global_params = {'discount_rate': 10}
    answer = discount_arpu(arpu, timestep, global_params)

    assert answer == arpu / 1.1 ** timestep
