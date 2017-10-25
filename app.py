from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def processRequest(req):
    docpart = req.get("result").get("parameters").get("docpart")
    yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + docpart + "')"
    yql_url = "https://query.yahooapis.com/v1/public/yql?" + urlencode({'q': yql_query}) + "&format=json"
    data = json.loads(urlopen(yql_url).read())
    res = makeWebhookResult(data, req)
    return res

def makeWebhookResult(data, req):
    docpart = req.get("result").get("parameters").get("docpart")
    unitsales = req.get("result").get("parameters").get("unitsales")

    if unitsales == 'W':
        docpart = "WUnitSales"
    elif unitsales == 'D':
        docpart = "DUnitSales"
    elif unitsales == 'Other':
        docpart = "OtherUnitSales"
    else:    
        unitsales = unitsales
        
    if docpart == 'WUnitSales':
        speech = "W generated much higher unit sales in September 2017 than September 2016. Its unit sales increased by 433 units (22.85%), from 1,895 units in September 2016 to 2,328 units in September 2017. Sales Districts Copenhagen (251, 64.03%), Paris (157, 28.04%), and Vienna (39, 39.8%) were the largest contributors to the increase in W's unit sales. Helsinki (-27, -34.18%), Bern (-26, -54.17%), and Astana (-18, -45%) were the largest detractors from the increase in W's unit sales."
    elif docpart == 'CustomerChains':
        speech = "From September 2016 to September 2017, Target (138, 44.23%), Zara (66, 28.45%), and Carrefour (63, 29.58%) were the largest contributors to the increase in W's unit sales. Intersport (-63, -16.89%), Metro (-14, -66.67%), and Tesco (-13, -61.9%) were the largest detractors from the increase in W's unit sales."
    elif docpart == 'LargestCustomers':
        speech = ""
    elif docpart == 'ProductTypes':
        speech = ""
    elif docpart == 'ProductVariants':
        speech = ""
    elif docpart == 'ProductSize':
        speech = ""
    elif docpart == 'ProductSurface':
        speech = ""
    elif docpart == 'PVariant':
        speech = ""
    elif docpart == 'DUnitSales':
        speech = ""
    elif docpart == 'OtherUnitSales':
        speech = ""
    elif docpart == 'WholeDocument':
        speech = ""
    else:
        speech = "Sorry but I did not understand your request. What do you want me to do?"

    
    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-weather-webhook-sample"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')
