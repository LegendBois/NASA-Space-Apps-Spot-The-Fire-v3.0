import pandas as pd

def get_state_name(lat, lon):
    from geopy.geocoders import Nominatim
    locator = Nominatim(user_agent="myGeocoder")
    coordinates = str(lat)+", "+str(lon)
    location = locator.reverse(coordinates)
    return location.raw['address']["state"]

def get_value_per_acre(lat, lon):
    propertydata = pd.read_csv("Data/statewise-pricing-usa.csv")
    state = get_state_name(lat, lon)
    return propertydata.loc[propertydata['State'] == state].values[0,1]

def get_total_economic_loss(lat, lon, area):
    acres = 247.105 * area
    return get_value_per_acre(lat, lon) * acres

def get_area_from_scan_track(scan, track):
    l = scan * 111 #km
    h = track * 111 #km
    area_in_km2 = l*h
    return area_in_km2

def get_weighted_economic_loss(total_economic_loss, risk, risk_scale): #risk_scale is maximum value of risk possible (such as out of 5 or out of 100 etc)
    if(risk > risk_scale):
        raise ArithmeticError("Risk cannot be greater than risk scale")
    return total_economic_loss * risk / risk_scale

def get_lat_long_from_location(name):
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(name)
    return (location.latitude,location.longitude)

def get_county_name(lat, lon):
    from geopy.geocoders import Nominatim
    locator = Nominatim(user_agent="myGeocoder")
    coordinates = str(lat)+", "+str(lon)
    location = locator.reverse(coordinates)
    county = location.raw['address']["county"]
    if 'County' in county:
        county = county.replace(' County','')
    return county

def get_df_endangered_species(lat, lon):
    county = get_county_name(lat, lon)
    wild = pd.read_csv("Data/wildlife.csv")
    wild = wild.loc[(wild['County'] == county) & (wild['Global Conservation Rank'].isin(['G1','G2']))]['Common Name']
    if wild.empty:
        return None
    return wild