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
    if req.get("result").get("action") != "yahooWeatherForecast":
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
    
    if docpart == 'summary':
        speech = "Summary In September 2017, 2 product groups were above the benchmark unit sales of 1,000 units. W (2,328 units), which accounted for 61.78% of the product groups' unit sales, generated the highest unit sales and T (8 units), which accounted for 0.21% of the product groups' unit sales, generated the lowest unit sales."
    elif docpart == 'W Unit Sales':
        speech = "W's unit sales increased by 433 units (22.85%), from 1,895 units in September 2016 to 2,328 units in September 2017. Geographically. Fuvahmulah (251, 64.03%), MalÃ© (157, 28.04%), and Other (43, 7.66%) drove the increase in W's unit sales and Hithadhoo (-10, -3.33%) and Kulhudhuffushi (-8, -9.76%) offset the increase in W's unit sales."      
    elif docpart == "D Unit Sales':
        speech = "From September 2016 to September 2017, D's unit sales increased by 142 (13.28%) to 1,211. Other (98, 30.63%), MHL (71, 133.96%), and RFL (25, 15.63%) drove the increase in D's unit sales and DKL (-40, -8.68%) and DFD (-12, -16%) offset the increase in D's unit sales. Option 1. The 5 product types included in D are DKL, which has unit sales of 9,708, Other, which has unit sales of 6,577, RFL, which has unit sales of 2,071, MHL, which has unit sales of 1,694, and DFD, which has unit sales of 1,505. Option 2. In September 2017, D had a unit sales of 1,211. DKL (421), which accounted for 34.76% of the unit sales of the contributors to the product group's unit sales, Other (418), which accounted for 34.52%, and RFL (185), which accounted for 15.28%, were the largest contributors to the product group's unit sales and accounted for 84.56% of the unit sales of the contributors to its unit sales." 
    else:
        speech = "You have not selected a correct part of the report. Please try again"
        
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
