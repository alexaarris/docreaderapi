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
        
    if docpart == 'Summary':
        speech = "In September 2017, 2 product groups were above the benchmark unit sales of 1,000 units. W (2,328 units), which accounted for 61.78% of the product groups' unit sales, generated the highest unit sales and T (8 units), which accounted for 0.21% of the product groups' unit sales, generated the lowest unit sales. Product comparisons: W generated much higher unit sales than D, which generated the second highest unit sales, did (by 1,117 units)."
    elif docpart == 'WUnitSales':
        speech = "W generated much higher unit sales in September 2017 than September 2016. Its unit sales increased by 433 units (22.85%), from 1,895 units in September 2016 to 2,328 units in September 2017. Geographically, Copenhagen (251, 64.03%), Paris (157, 28.04%), Vienna (39, 39.8%), Not Assigned (23, 43.4%), and Berlin (20, 117.65%) were the largest contributors to the increase in W's unit sales and Helsinki (-27, -34.18%), Bern (-26, -54.17%), Astana (-18, -45%), Amsterdam (-10, -3.33%), and Stockholm (-8, -9.76%) were the largest detractors from the increase in W's unit sales."
    elif docpart == 'CustomerChains':
        speech = "From September 2016 to September 2017, Target (138, 44.23%), Zara (66, 28.45%), and Carrefour (63, 29.58%) were the largest contributors to the increase in W's unit sales and Intersport (-63, -16.89%), Metro (-14, -66.67%), and Tesco (-13, -61.9%) were the largest detractors from the increase in W's unit sales. In September 2017, W generated unit sales of 2,328. Target (450), which accounted for 19.32% of the unit sales of the contributors to the product group's unit sales, Intersport (310), which accounted for 13.31%, Zara (298), which accounted for 12.8%, Carrefour (276), which accounted for 11.85%, and IKEA (158), which accounted for 6.78%, were the largest contributors to the product group's unit sales and accounted for 64.06% of the unit sales of the contributors to its unit sales."
    elif docpart == 'ProductTypes':
        speech = "From September 2016 to September 2017, W's unit sales increased by 433. GGU (268, 24.28%), GGL (114, 23.08%), GPL (24, 39.34%), GIU (17, 89.47%), and GPU (10, 6.9%) were the largest contributors to the increase in W's unit sales and VIU (-8, -57.14%), VFA (-7, -43.75%), GVO (-3, -33.33%), GIL (-3, -30%), and VRW (-2, -100%) were the largest detractors from the increase in W's unit sales. In September 2017, W generated a unit sales of 2,328. GGU (1,372), which accounted for 58.93% of the unit sales of the contributors to the product group's unit sales, GGL (608), which accounted for 26.12%, and GPU (155), which accounted for 6.66%, were the largest contributors to the product group's unit sales and accounted for 91.71% of the unit sales of the contributors to its unit sales."
    elif docpart == 'ProductVariants':
        speech = "From September 2016 to September 2017, 0066 (338, 127.55%) and 2066 (213, 178.99%) were the largest contributors to the increase in the product group's unit sales and 0070 (-120, -13.51%) and 2070 (-38, -10.92%) were the largest detractors from the increase in its unit sales."
    elif docpart == 'ProductSize':
        speech = "M (183, 22.18%), P (155, 37.35%), and C (103, 35.76%) were the largest contributors to the increase in the product group's unit sales and N (-24, -44.44%), + (-3, -33.33%), and 3 (-1, -25%) were the largest detractors from the increase in its unit sales."
    elif docpart == 'ProductSurface':
        speech = "0 (291, 22.61%), 2 (174, 33.4%), and 1 (3, inf%) drove the increase in the product group's unit sales and + (-22, -42.31%), 3 (-11, -33.33%), and Not Assigned (-2, -100%) offset the increase in its unit sales."
    elif docpart == 'PVariant':
        speech = "66 (627, 141.22%) and 60 (67, inf%) were the largest contributors to the increase in the product group's unit sales and 70 (-184, -14.08%) and 73 (-39, -100%) were the largest detractors from the increase in its unit sales."
    elif docpart == 'DUnitSales':
        speech = "D's unit sales increased by 142 (13.28%), from 1,069 in September 2016 to 1,211 in September 2017. Split by product types, DSL (101, 315.63%), MHL (71, 133.96%), and FHC (51, 300%) were the largest contributors to the increase in D's unit sales and PAL (-118, -71.95%), DKL (-40, -8.68%), and DFD (-12, -16%) were the largest detractors from the increase in D's unit sales. In September 2017, D generated a unit sales of 1,211. DKL (421), which accounted for 34.76% of the unit sales of the contributors to the product group's unit sales, RFL (185), which accounted for 15.28%, and DSL (133), which accounted for 10.98%, were the largest contributors to the product group's unit sales and accounted for 61.02% of the unit sales of the contributors to its unit sales."
    elif docpart == 'OtherUnitSales':
        speech = "F's unit sales decreased by 2 units (3.03%), from 66 units in September 2016 to 64 units in September 2017. T's unit sales increased by 1 unit (14.29%), from 7 units in September 2016 to 8 units in September 2017."        
    elif docpart == 'WholeDocument':
        speech = "W Unit Sales: W generated much higher unit sales in September 2017 than September 2016. Its unit sales increased by 433 units (22.85%), from 1,895 units in September 2016 to 2,328 units in September 2017. Geographically, Copenhagen (251, 64.03%), Paris (157, 28.04%), Vienna (39, 39.8%), Not Assigned (23, 43.4%), and Berlin (20, 117.65%) were the largest contributors to the increase in W's unit sales and Helsinki (-27, -34.18%), Bern (-26, -54.17%), Astana (-18, -45%), Amsterdam (-10, -3.33%), and Stockholm (-8, -9.76%) were the largest detractors from the increase in W's unit sales. Customer Chains: From September 2016 to September 2017, Target (138, 44.23%), Zara (66, 28.45%), and Carrefour (63, 29.58%) were the largest contributors to the increase in W's unit sales and Intersport (-63, -16.89%), Metro (-14, -66.67%), and Tesco (-13, -61.9%) were the largest detractors from the increase in W's unit sales. In September 2017, W generated unit sales of 2,328. Target (450), which accounted for 19.32% of the unit sales of the contributors to the product group's unit sales, Intersport (310), which accounted for 13.31%, Zara (298), which accounted for 12.8%, Carrefour (276), which accounted for 11.85%, and IKEA (158), which accounted for 6.78%, were the largest contributors to the product group's unit sales and accounted for 64.06% of the unit sales of the contributors to its unit sales. Product Types: From September 2016 to September 2017, W's unit sales increased by 433. GGU (268, 24.28%), GGL (114, 23.08%), GPL (24, 39.34%), GIU (17, 89.47%), and GPU (10, 6.9%) were the largest contributors to the increase in W's unit sales and VIU (-8, -57.14%), VFA (-7, -43.75%), GVO (-3, -33.33%), GIL (-3, -30%), and VRW (-2, -100%) were the largest detractors from the increase in W's unit sales. In September 2017, W generated a unit sales of 2,328. GGU (1,372), which accounted for 58.93% of the unit sales of the contributors to the product group's unit sales, GGL (608), which accounted for 26.12%, and GPU (155), which accounted for 6.66%, were the largest contributors to the product group's unit sales and accounted for 91.71% of the unit sales of the contributors to its unit sales. Product Variants: From September 2016 to September 2017, 0066 (338, 127.55%) and 2066 (213, 178.99%) were the largest contributors to the increase in the product group's unit sales and 0070 (-120, -13.51%) and 2070 (-38, -10.92%) were the largest detractors from the increase in its unit sales. Product Size: M (183, 22.18%), P (155, 37.35%), and C (103, 35.76%) were the largest contributors to the increase in the product group's unit sales and N (-24, -44.44%), + (-3, -33.33%), and 3 (-1, -25%) were the largest detractors from the increase in its unit sales. Product Surface: 0 (291, 22.61%), 2 (174, 33.4%), and 1 (3, inf%) drove the increase in the product group's unit sales and + (-22, -42.31%), 3 (-11, -33.33%), and Not Assigned (-2, -100%) offset the increase in its unit sales. P Variant: 66 (627, 141.22%) and 60 (67, inf%) were the largest contributors to the increase in the product group's unit sales and 70 (-184, -14.08%) and 73 (-39, -100%) were the largest detractors from the increase in its unit sales. D Unit Sales: D's unit sales increased by 142 (13.28%), from 1,069 in September 2016 to 1,211 in September 2017. Split by product types, DSL (101, 315.63%), MHL (71, 133.96%), and FHC (51, 300%) were the largest contributors to the increase in D's unit sales and PAL (-118, -71.95%), DKL (-40, -8.68%), and DFD (-12, -16%) were the largest detractors from the increase in D's unit sales. In September 2017, D generated a unit sales of 1,211. DKL (421), which accounted for 34.76% of the unit sales of the contributors to the product group's unit sales, RFL (185), which accounted for 15.28%, and DSL (133), which accounted for 10.98%, were the largest contributors to the product group's unit sales and accounted for 61.02% of the unit sales of the contributors to its unit sales. Other Unit Sales: F's unit sales decreased by 2 units (3.03%), from 66 units in September 2016 to 64 units in September 2017. T's unit sales increased by 1 unit (14.29%), from 7 units in September 2016 to 8 units in September 2017."
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
