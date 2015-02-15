# Zipcode_HJ

Given two addresses (in the San Francisco Bay Area), we try to find all the zip codes present in the straight line connecting the two addresses and draw them out on a static map.


System Desgin:
Python Flask for the backend. We hit the Google API url from the backend to map zipcodes to lat,lng and vice versa.

To run the application, run app.py and the the output is in localhost. The screenshots folder has the output for a couple of valid inputs.

Improvements:

Response is quite slow for addresses far apart. The original approach involved finding the "adjacent" polygon along the line by reading values from the shape file cache and a geometrical solution. It was not viable because of Python round-off errors.

Add test cases (TDD)

Handle "invalid" addresses
