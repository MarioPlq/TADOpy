# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 12:16:28 2022

@author: Mario Ploquin
"""

import requests
import ijson
import pandas as pd
from requests.structures import CaseInsensitiveDict

class TADO_pilot:
    
    def __init__(self,username,password):
        url_token     = 'https://auth.tado.com/oauth/token'
        client_secret = 'wZaRN7rpjn3FoNyF5IFuxg9uMzYJcvOoQ8QWiIqS3hfk6gLhVlG57j5YNoZL2Rtc'
        data_token    = {'client_id': 'tado-web-app',\
                         'grant_type': 'password','scope': 'home.user',\
                         'username': username,\
                         'password': password,\
                         'client_secret': client_secret}
        try:
            #token recovery
            response_request = requests.post(url_token, data = data_token)
            response_parse   = ijson.parse(response_request.text)
            self.token       = self.read_json(response_parse,data_type='string',what='access_token')[0]
            
            #home id recovery
            url_homeId  = 'https://my.tado.com/api/v1/me'
            headers_homeId                  = CaseInsensitiveDict()
            headers_homeId["Authorization"] = f"Bearer {self.token}"
            response_request = requests.get(url_homeId, headers = headers_homeId)
            response_parse   = ijson.parse(response_request.text)
            self.homeId      = self.read_json(response_parse,data_type='int',what='homeId')[0]
        except:
            print('error : verify your password or username')

    #to read a json 
    def read_json(self,json,data_type,what=''):
        answer = []
        for prefix, event, value in json:
            #if we want setpoint temperature
            if data_type == 'TC':
                if ((prefix == 'settings.dataIntervals.item.value.power') | (prefix == 'settings.dataIntervals.item.value.temperature.celsius')):
                    if ((value == 'ON') | (prefix == 'settings.dataIntervals.item.value.temperature.celsius')):
                        if prefix == 'settings.dataIntervals.item.value.temperature.celsius':
                            answer.append(float(value))
                    elif value == 'OFF':
                        answer.append(float(10.0)) 
            #else search what we want
            elif prefix==what:
                if   data_type == 'string':
                    answer.append(value)
                elif data_type == 'float':
                    answer.append(float(value))
                elif data_type == 'int':
                    answer.append(int(value))
                elif data_type == 'date':
                    answer.append(pd.to_datetime(value))
        return answer

    #to put a setpoint for a special zone
    def put_setpoint(self,zone,setpoint_temp_in_degree):
        
        url_put = f"https://my.tado.com/api/v2/homes/{self.homeId}/zones/{zone}/overlay"
        headers_put = CaseInsensitiveDict()
        headers_put["Authorization"] = f"Bearer {self.token}"
        headers_put["Content-Type"]  = "application/json;charset=utf-8"
        
        setpoint_temp_in_fahrenheit = (setpoint_temp_in_degree*9/5) + 32. 
        
        data_put = '{"setting":{"type":"AIR_CONDITIONING",\
                     "power":"ON",\
                     "mode":"COOL",\
                     "temperature":{"celsius":%s,"fahrenheit":%d}},\
                     "termination":{"type":"MANUAL"}}'% (setpoint_temp_in_degree,setpoint_temp_in_fahrenheit)

        response_request = requests.put(url_put,headers=headers_put,data=data_put)
        print(response_request.text)
