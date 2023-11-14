import pytest
from railway import fare_price, Station, RailNetwork
import numpy as np

# Used to store various parameters for Station object creation to carry out similar tests more efficiently
@pytest.mark.parametrize("name, region, crs, lat, lon, hub",
                         # This CRS code is not completely uppercase
                         [("Brighton", "South East", "Btn", 50.829659, -0.141234, True),
                            # This CRS code is 4 characters rather than 3
                          ("Brighton", "South East", "BTNN", 50.829659, -0.141234, True),
                         # This CRS code is 2 characters rather than 3
                          ("Brighton", "South East", "BT", 50.829659, -0.141234, True),
                          # The below 2 have latitudes outside the accepted range
                          ("Brighton", "South East", "BTN", 91.0, -0.141234, True),
                          ("Brighton", "South East", "BTN", -91.0, -0.141234, True),
                          # The below 2 have longitudes outside the accepted range
                          ("Brighton", "South East", "BTN", 50.829659, 181.0, True),
                          ("Brighton", "South East", "BTN", 50.829659, -181.0, True)])
def test_value_error_station(name, region, crs, lat, lon, hub):
    """
    Function to test whether each of the various incorrect inputs (parametrized above) provided to
    the Station class with the purpose of creating Station objects would raise a ValueError.
    """
    with pytest.raises(ValueError):  # Checks whether a ValueError is raised for each test
        Station(name, region, crs, lat, lon, hub)


def test_fare_price():
    """
    Function to test whether the fare_price function calculates the fare price as intended through
    comparing what the function returns to the calculation done within this function using preset values for each of
    the variables used for the function.
    """
    distance = 100
    different_regions = 1
    hubs_in_dest_region = 3
    result = fare_price(distance, different_regions, hubs_in_dest_region)
    expected = 1 + distance * np.exp((-1 * distance) / 100) * (1 + (different_regions * hubs_in_dest_region) / 10)
    assert result == expected


@pytest.mark.parametrize("name, region, crs, lat, lon, hub",
                         # This has an int value in the name parameter rather than a string
                         [(6, "South East", "BTN", 50.829659, -0.141234, True),
                          # This has an int value in the region parameter rather than a string
                          ("Brighton", 6, "BTN", 50.829659, -0.141234, True),
                          # This has an int value in the crs parameter rather than a string
                          ("Brighton", "South East", 6, 50.829659, -0.141234, True),
                          # The latitude is a str value rather than a float
                          ("Brighton", "South East", "BTN", "50.829659", -0.141234, True),
                          # The longitude is a str value rather than a float
                          ("Brighton", "South East", "BTN", 50.829659, "-0.141234", True),
                          # The hub is a str value rather than a bool
                          ("Brighton", "South East", "BTN", 50.829659, -0.141234, "True")])
def test_type_error_station(name, region, crs, lat, lon, hub):
    """
    Function to test whether each of the various incorrect inputs (parametrized above) provided to
    the Station class with the purpose of creating Station objects would raise a TypeError.
    """
    with pytest.raises(TypeError):  # Checks whether a TypeError is raised for each test
        Station(name, region, crs, lat, lon, hub)


@pytest.fixture()
def stations():
    """
    Test function that sets up example station objects that can be called by other tests.
    """
    brighton = Station("Brighton", "South East", "BTN", 50.829659, -0.141234, True)
    kings_cross = Station("London Kings Cross", "London", "KGX", 51.530827, -0.122907, True)
    edinburgh_park = Station("Edinburgh Park", "Scotland", "EDP", 55.927615, -3.307829, False)
    return brighton, kings_cross, edinburgh_park


def test_correct_station_input(stations):
    """
    Function to test that the attributes of a Station object created from the Station class are created correctly.

    This compares the attributes of the brighton Station object created by the test function to values I expect them
    to have.
    """
    brighton, kings_cross, edinburgh_park = stations
    result = [brighton.name, brighton.region, brighton.crs, brighton.lat, brighton.lon, brighton.hub]
    expected = ["Brighton", "South East", "BTN", 50.829659, -0.141234, True]
    assert result == expected


def test_crs_codes(stations):
    """
    Function to test whether the Rail Network class raises a ValueError when 2 of the station objects within the list
    of station objects given as a parameter to the Rail Network class share the same CRS code as CRS codes within a
    Rail Network object must be unique.
    """
    brighton, kings_cross, edinburgh_park = stations
    # Makes it so that the kings_cross and brighton station objects have the same CRS code
    kings_cross = Station("London Kings Cross", "London", "BTN", 51.530827, -0.122907, True)
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    with pytest.raises(ValueError):
        RailNetwork(list_of_stations)


def test_distance_to(stations):
    """
    Function to test whether the distance_to method of the Station class calculates the distance between 2
    station objects as intended through comparing what the function returns as the distance between Brighton and King's
    Cross to the calculation done within this function using the Haversine formula.
    """
    brighton, kings_cross, edinburgh_park = stations
    expected = 2 * 6371 * np.arcsin(np.sqrt((np.power((np.sin((kings_cross.lat - brighton.lat) / 2)), 2)) +
                                            np.cos(brighton.lat) * np.cos(kings_cross.lat) *
                                            np.power((np.sin((kings_cross.lon - brighton.lon) / 2)), 2)))
    result = brighton.distance_to(kings_cross)
    assert result == expected


def test_distance_to_reversible(stations):
    """
    Function to test whether the distance_to method of the Station class calculates the same distance between two
    station objects regardless of which station object is used to call the method and which is the parameter entered.
    """
    brighton, kings_cross, edinburgh_park = stations
    result_one = brighton.distance_to(kings_cross)
    result_two = kings_cross.distance_to(brighton)
    assert result_one == result_two


def test_regions(stations):
    """
    Function to test whether the regions method of the RailNetwork class returns the expected list of unique regions
    for the list of station objects that form the rail network object.

    This function uses 2 stations with the same region to verify that a list of 2 regions are returned rather than a
    list of 3 (as there are only 2 unique regions here).
    """
    brighton, kings_cross, edinburgh_park = stations
    # Gives the kings_cross station object the same region as the brighton station object
    kings_cross = Station("London Kings Cross", "South East", "KGX", 51.530827, -0.122907, True)
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    rail_network = RailNetwork(list_of_stations)
    expected = ["Scotland", "South East"]
    result = rail_network.regions()
    assert result.sort() == expected.sort() # Sort is used to ensure that the order of the regions is not what fails
    # the test as the order does not matter for this test


def test_n_stations(stations):
    """
    Function to test whether the n_stations method of the RailNetwork class returns the expected number of station
    objects in the RailNetwork class.

    This function expects 3 to be returned as there are only 3 station objects in the rail_network object.
    """
    brighton, kings_cross, edinburgh_park = stations
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    rail_network = RailNetwork(list_of_stations)
    expected = 3
    result = rail_network.n_stations()
    assert expected == result


def test_hub_stations(stations):
    """
    Function to test whether the hub_stations method of the RailNetwork class correctly returns a list of the station
    objects in the network that are hub stations.

    As this uses the example stations set up by the stations function, which contains only 2 hub stations,
    the expected output would be brighton and kings_cross which are the 2 hub stations in the network.
    """
    brighton, kings_cross, edinburgh_park = stations
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    rail_network = RailNetwork(list_of_stations)
    result = rail_network.hub_stations()
    expected = [brighton, kings_cross]
    assert expected == result


def test_hub_stations_one_region(stations):
    """
    Function to test whether, when using the optional parameter of providing a region to the hub_stations method of
    the RailNetwork class, the method correctly returns a list of the station objects in the network that are both
    hub stations and belong to the given region.

    Expected output here would be the only station object in the list that's in London which is kings_cross.
    """
    brighton, kings_cross, edinburgh_park = stations
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    rail_network = RailNetwork(list_of_stations)
    result = rail_network.hub_stations("London")
    expected = [kings_cross]
    assert expected == result


def test_hub_stations_error(stations):
    """
    Function to test whether, when using the optional parameter of providing a region to the hub_stations method of
    the RailNetwork class, the method correctly raises a KeyError if the optional parameter is not a region that any
    of the station objects belong to.
    """
    brighton, kings_cross, edinburgh_park = stations
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    rail_network = RailNetwork(list_of_stations)
    with pytest.raises(KeyError): # Checks whether this test raises a KeyError
        rail_network.hub_stations("Spain") # Spain is not a region in the above station objects


def test_closest_hub(stations):
    """
    Function to test whether the closest_hub method of the RailNetwork class correctly returns the closest hub station
    object (the smallest distance in km) to the station object given as a parameter for the method that is also
    within the same region as the station object given as a parameter.

    This compares the return to an expected answer using the example regions which was derived through manual testing
    of the code.
    """
    brighton, kings_cross, edinburgh_park = stations
    for station in stations:
        station.region = "South East"  # Sets the region of all the station objects to the South East so that both
        # brighton and kings_cross are considered for the test
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    rail_network = RailNetwork(list_of_stations)
    expected = kings_cross
    result = rail_network.closest_hub(edinburgh_park)
    assert expected == result


def test_closest_hub_error(stations):
    """
    Function to test whether the closest_hub method of the RailNetwork class correctly raises a KeyError if no hub
    stations exist within the same region as the station object given as a parameter for the method.
    """
    brighton, kings_cross, edinburgh_park = stations
    list_of_stations = [brighton, kings_cross, edinburgh_park]
    rail_network = RailNetwork(list_of_stations)
    with pytest.raises(KeyError):  # Checks whether this test raises a KeyError
        rail_network.closest_hub(edinburgh_park)
