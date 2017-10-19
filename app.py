# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "docreaderapi":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data, req)
    return res


def makeYqlQuery(req):
    docpart = req.get("result").get("parameters").get("docpart")

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + docpart + "')"


def makeWebhookResult(data, req):
    docpart = req.get("result").get("parameters").get("docpart")
    
    if docpart == 'Summary':
        speech = "In September 2017, 2 product groups were above the benchmark unit sales of 1,000 units. W (2,328 units), which accounted for 61.78% of the product groups' unit sales, generated the highest unit sales and T (8 units), which accounted for 0.21% of the product groups' unit sales, generated the lowest unit sales. Product comparisons: W generated much higher unit sales than D, which generated the second highest unit sales, did (by 1,117 units)."
    elif docpart == 'WUnitSales':
        speech = "W's unit sales increased by 433 units (22.85%), from 1,895 units in September 2016 to 2,328 units in September 2017. Geographically, Fuvahmulah (251, 64.03%), MalÃ© (157, 28.04%), and Other (43, 7.66%) drove the increase in W's unit sales and Hithadhoo (-10, -3.33%) and Kulhudhuffushi (-8, -9.76%) offset the increase in W's unit sales."
    elif docpart == 'CustomerChains':
        speech = "From September 2016 to September 2017, Other (156, 28.62%), Chain 1 (138, 44.23%), and Chain 4 (66, 28.45%) were the largest contributors to the increase in W's unit sales and Chain 2 (-63, -16.89%) and Chain 9 (-7, -33.33%) were the largest detractors from the increase in W's unit sales. The customer chains represent different shares of total W unit sales. In September 2017, W had a unit sales of 2,328. Other (701), which accounted for 30.11% of the unit sales of the contributors to the product group's unit sales, Chain 1 (450), which accounted for 19.33%, and Chain 2 (310), which accounted for 13.32%, were the largest contributors to the product group's unit sales and accounted for 62.76% of the unit sales of the contributors to its unit sales."
    elif docpart == 'ProductTypes':
        speech = "In September 2017, W had a unit sales of 2,328. GGL (608), which accounted for 26.12% of the unit sales of the contributors to the product group's unit sales, GGU (1,372), which accounted for 58.93%, GPL (85), which accounted for 3.65%, GPU (155), which accounted for 6.66%, and Other (108), which accounted for 4.64%, contributed to the product group's unit sales. From September 2016 to September 2017, GGU (268, 24.28%), GGL (114, 23.08%), GPL (24, 39.34%), Other (17, 18.68%), and GPU (10, 6.9%) drove the increase in the product group's unit sales. There are no detractors from the increase in the product group's unit sales."
    elif docpart == 'ProductVariants':
        speech = "The product variants can be used to explain the change in W unit sales. From September 2016 to September 2017, 0066 (338, 127.55%), 2066 (213, 178.99%), and Other (40, 14.55%) drove the increase in the product group's unit sales and 0070 (-120, -13.51%) and 2070 (-38, -10.92%) offset the increase in the product group's unit sales."
    elif docpart == 'ProductSurface':
        speech = "5 product surfaces included in the product group had a unit sales in September 2016 and 4 product surfaces had a unit sales in September 2017."
    elif docpart == 'ProductSize':
        speech = "The product group's unit sales increased by 433 (22.85%), from 1,895 in September 2016 to 2,328 in September 2017. In September 2017, 8 product sizes with a unit sales in September 2016 included in the product group had a unit sales. From September 2016 to September 2017, M (183, 22.18%), P (155, 37.35%), and C (103, 35.76%) were the largest contributors to the increase in the product group's unit sales and N (-24, -44.44%), + (-3, -33.33%), and 3 (-1, -25%) were the largest detractors from the increase in its unit sales."
    elif docpart == 'DUnitSales':
        speech = "From September 2016 to September 2017, D's unit sales increased by 142 (13.28%) to 1,211. Other (98, 30.63%), MHL (71, 133.96%), and RFL (25, 15.63%) drove the increase in D's unit sales and DKL (-40, -8.68%) and DFD (-12, -16%) offset the increase in D's unit sales. In September 2017, D had a unit sales of 1,211. DKL (421), which accounted for 34.76% of the unit sales of the contributors to the product group's unit sales, Other (418), which accounted for 34.52%, and RFL (185), which accounted for 15.28%, were the largest contributors to the product group's unit sales and accounted for 84.56% of the unit sales of the contributors to its unit sales."
    elif docpart == 'OtherUnitSales':
        speech = "F's unit sales decreased by 2 units (3.03%), from 66 units in September 2016 to 64 units in September 2017. T's unit sales increased by 1 unit (14.29%), from 7 units in September 2016 to 8 units in September 2017."        
    elif docpart == 'WholeDocument':
        speech = "Summary: In September 2017, 2 product groups were above the benchmark unit sales of 1,000 units. W (2,328 units), which accounted for 61.78% of the product groups' unit sales, generated the highest unit sales and T (8 units), which accounted for 0.21% of the product groups' unit sales, generated the lowest unit sales. Product comparisons: W generated much higher unit sales than D, which generated the second highest unit sales, did (by 1,117 units). W Unit Sales: W's unit sales increased by 433 units (22.85%), from 1,895 units in September 2016 to 2,328 units in September 2017. Geographically, Fuvahmulah (251, 64.03%), MalÃ© (157, 28.04%), and Other (43, 7.66%) drove the increase in W's unit sales and Hithadhoo (-10, -3.33%) and Kulhudhuffushi (-8, -9.76%) offset the increase in W's unit sales. Customer Chains: From September 2016 to September 2017, Other (156, 28.62%), Chain 1 (138, 44.23%), and Chain 4 (66, 28.45%) were the largest contributors to the increase in W's unit sales and Chain 2 (-63, -16.89%) and Chain 9 (-7, -33.33%) were the largest detractors from the increase in W's unit sales. The customer chains represent different shares of total W unit sales. In September 2017, W had a unit sales of 2,328. Other (701), which accounted for 30.11% of the unit sales of the contributors to the product group's unit sales, Chain 1 (450), which accounted for 19.33%, and Chain 2 (310), which accounted for 13.32%, were the largest contributors to the product group's unit sales and accounted for 62.76% of the unit sales of the contributors to its unit sales. Product Types: In September 2017, W had a unit sales of 2,328. GGL (608), which accounted for 26.12% of the unit sales of the contributors to the product group's unit sales, GGU (1,372), which accounted for 58.93%, GPL (85), which accounted for 3.65%, GPU (155), which accounted for 6.66%, and Other (108), which accounted for 4.64%, contributed to the product group's unit sales. From September 2016 to September 2017, GGU (268, 24.28%), GGL (114, 23.08%), GPL (24, 39.34%), Other (17, 18.68%), and GPU (10, 6.9%) drove the increase in the product group's unit sales. There are no detractors from the increase in the product group's unit sales. Product Variants: The product variants can be used to explain the change in W unit sales. From September 2016 to September 2017, 0066 (338, 127.55%), 2066 (213, 178.99%), and Other (40, 14.55%) drove the increase in the product group's unit sales and 0070 (-120, -13.51%) and 2070 (-38, -10.92%) offset the increase in the product group's unit sales. Product Surface: 5 product surfaces included in the product group had a unit sales in September 2016 and 4 product surfaces had a unit sales in September 2017. Product Size: The product group's unit sales increased by 433 (22.85%), from 1,895 in September 2016 to 2,328 in September 2017. In September 2017, 8 product sizes with a unit sales in September 2016 included in the product group had a unit sales. From September 2016 to September 2017, M (183, 22.18%), P (155, 37.35%), and C (103, 35.76%) were the largest contributors to the increase in the product group's unit sales and N (-24, -44.44%), + (-3, -33.33%), and 3 (-1, -25%) were the largest detractors from the increase in its unit sales. D Unit Sales: From September 2016 to September 2017, D's unit sales increased by 142 (13.28%) to 1,211. Other (98, 30.63%), MHL (71, 133.96%), and RFL (25, 15.63%) drove the increase in D's unit sales and DKL (-40, -8.68%) and DFD (-12, -16%) offset the increase in D's unit sales. In September 2017, D had a unit sales of 1,211. DKL (421), which accounted for 34.76% of the unit sales of the contributors to the product group's unit sales, Other (418), which accounted for 34.52%, and RFL (185), which accounted for 15.28%, were the largest contributors to the product group's unit sales and accounted for 84.56% of the unit sales of the contributors to its unit sales. Other Unit Sales: F's unit sales decreased by 2 units (3.03%), from 66 units in September 2016 to 64 units in September 2017. T's unit sales increased by 1 unit (14.29%), from 7 units in September 2016 to 8 units in September 2017."
    else:
        speech = "Sorry but I did not understand your request. What do you want me to do?"
        
    print("Summary:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        "source": "apiai-weather-webhook-sample"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
