from cache import LocalCache, JSONRedis
import fiona
from flask import Flask, render_template, request
import json
import redis
import sys
import urllib


app = Flask(__name__)

# Config
app.config.update({
    'DEBUG': True,
    'ZIP_BOUNDARY_FILE': '/Users/rajaggan/Documents/Codes/cb_2013_us_zcta510_500k/cb_2013_us_zcta510_500k.shp',
    # 'ZIP_BOUNDARY_FILE': '/home/ubuntu/zip_boundary_data/cb_2013_us_zcta510_500k.shp',
})


# Cache
cache = JSONRedis(host='localhost', port=6379, db=0)
try:
    cache.set('test', 'test')
except redis.exceptions.ConnectionError:
    cache = LocalCache()


# Initializing the zipcode boundary data cache. This will take a few minutes
#   the first time the server is run.
if not cache.get('zips_loaded') or '--reload-zips' in sys.argv:
    all_zipcodes = []
    with fiona.open(app.config.get('ZIP_BOUNDARY_FILE'), 'r') as source:
        while(True):
            zipcode = next(source, None)
            if zipcode:
                zipcode_name = zipcode['properties']['ZCTA5CE10']
                all_zipcodes.append(zipcode_name)
                cache.set(zipcode_name, zipcode['geometry'])
            else:
                cache.set('zips_loaded', True)
                break
    cache.set('all_zipcodes', all_zipcodes)

#Helpers
zips_set = set()
googleGeocodeUrl = 'http://maps.googleapis.com/maps/api/geocode/json?'

def get_zipcode(latlng, from_sensor = False):
    sensor = "true" if from_sensor else "false"
    params = "latlng={lat},{lon}&sensor={sen}".format(
        lat=latlng[0],
        lon=latlng[1],
        sen=sensor
    )

    url = "{base}{params}".format(base=googleGeocodeUrl, params=params)
    #url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    response = json.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['address_components']
        for items in location:
            if items['types'][0] == 'postal_code':
                zipcode = items['long_name']
                return zipcode
    else:
        location = None
    

    return None 
    
def get_coordinates(query, from_sensor = False):
    query = query.encode('utf-8')
    params = {
        'address': query,
        'sensor': "true" if from_sensor else "false"
    }
    url = googleGeocodeUrl + urllib.urlencode(params)
    json_response = urllib.urlopen(url)
    response = json.loads(json_response.read())
    if response['results']:
        location = response['results'][0]['geometry']['location']
        lat,lng = location['lat'], location['lng']
    else:
        lat,lng = 0,0
    return (lat,lng)

def find_mid_point(source,dest,zips_dict):
	global zips_set
	zip1 = get_zipcode(source)
	zip2 = get_zipcode(dest)
	midpoint = [(a+b)/2 for a,b in zip(source,dest)]
	zip_mid = get_zipcode(midpoint)
	print "zip1=",zip1
	print "zip2=",zip2
	print "zip_midpoint = ",zip_mid
	if zip1 and zip1 not in zips_dict:
		if cache.get(zip1)['type'] == 'Polygon':
			zips_dict[zip1] = [cache.get(zip1)['coordinates']]
		else:
			zips_dict[zip1] = cache.get(zip1)['coordinates']
		zips_set.add(zip1)
		print zip1, cache.get(zip1)['type']
	if zip2 and zip2 not in zips_dict:
		if cache.get(zip2)['type'] == 'Polygon':
			zips_dict[zip2] = [cache.get(zip2)['coordinates']]
		else:
			zips_dict[zip2] = cache.get(zip2)['coordinates']
		zips_set.add(zip2)
		print zip2, cache.get(zip2)['type']
	if zip1 == zip2:
		return
	if zip1==zip_mid: 
		if zip2 not in zips_dict:
			find_mid_point(midpoint,dest,zips_dict)
	elif zip2==zip_mid:
		if zip1 not in zips_dict:
			find_mid_point(source,midpoint,zips_dict)
	else:
		find_mid_point(source,midpoint,zips_dict)
		find_mid_point(midpoint,dest,zips_dict)
		
            
# Handlers
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query1 = request.form['addressa']
        query2 = request.form['addressb']
    else:
        query1 = "San Francisco, CA"
        query2 = "San Francisco, CA"
    '''
    query1 = "580 California St San Francisco CA 94104"
    #query2 = "3333 Coyote Hill Rd, Palo Alto, CA 94304"
    query2 = "San Francisco International Airport, San Francisco, CA 94128"
    #query2 = "1000 High Street, Santa Cruz, CA 95060"
    #query2 = "760 Market Street San Francisco CA 94102" 
    #query2 = "1533 Eddy Street San Francisco CA 94115"
    #query2 = "135 4th st San Francisco CA 94103"
    '''
    source = get_coordinates(query1)
    dest = get_coordinates(query2)
    zip1 = get_zipcode(source)
    zip2 = get_zipcode(dest)
    zips_dict = {}

    userloc = [source,dest]
    center = [(a+b)/2 for a,b in zip(source,dest)]
    if source != dest:
        find_mid_point(source,dest,zips_dict)
    if source != dest:
        zoom = 2/(max(abs(source[1]-dest[1]),abs(source[0]-dest[0])))
    else:
        zoom = 12
    global zips_set
    print zips_dict.keys()
    print zips_set
    zips = json.dumps(zips_dict)
    center = json.dumps(center)
    userloc = json.dumps(userloc)
    zoom = json.dumps(int(zoom))
    return render_template('zipcodes.html', zips=zips, center= center, userloc = userloc, zoom = zoom)

if __name__ == '__main__':
    app.run(port=8000)
