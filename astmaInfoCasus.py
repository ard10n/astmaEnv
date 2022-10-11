import pandas as pd
import numpy as np
import datetime

from bs4 import BeautifulSoup
import requests
import json
from geopy.distance import great_circle
import pandas as pd
#!pip install cbsodata
import cbsodata




def getLanLon(postcode):
    url = 'https://www.postcodezoekmachine.nl/'
    postcode = postcode.upper().replace(' ', '')
    URL = url + postcode
    try:
        page = requests.get(URL, timeout=(3.05, 27))
    except HTTPError as hp:
        print(hp)
    lat = 'not found'
    lon = lat
    soup = BeautifulSoup(page.content, "html.parser")
    try:
        result = soup.text.split('Garmin')[1].split('Supermarkt')[0]
        lat = result.split('Latitude\n')[1].split('\n')[0]
        lon = result.split('Longitude\n')[1].replace('\n', '')
        return float(lat), float(lon)
    except:
        print("An exception occurred")
    return 'not found', 'not found'


def haalHetWeerOpDatum(dag):
    def maakKolomSchoon(S):
        result = []
        for s in S:
            result.append(s.text.replace('<td>', '').replace('</td>', ''))
        return result

    keysToKeep = ['Windrichting', 'Gem. temperatuur', 'Windsnelheid (etmaal)', 'Zonneschijnduur', 'Globale straling',
                  'Neerslag duur', 'Som neerslag', 'Gem. luchtdruk', 'Gem. bewolking', 'Gem. relative vochtigheid']
    D = dict.fromkeys(keysToKeep)

    url = 'https://weerverleden.nl/' + str(dag.year) + str(dag.month).zfill(2) + str(dag.day).zfill(2) + '&all'
    try:
        page = requests.get(url, timeout=(3.05, 27))
    except HTTPError as hp:
        print(hp)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find('table', class_='weathersummary')
    for row in soup.select('tbody tr'):

        columns = row.find_all('td')
        if (columns != []):
            res = maakKolomSchoon(columns)
            if res[0] in keysToKeep:
                D[res[0]] = res[1]
    return D


def convertInput(dag, pc):
    # returns date in datetime format, latitude,longitude form postalcode
    seizoen = ['winter', 'lente', 'zomer', 'herfst', 'winter']
    dag = dag.replace('/', '-').replace('.', '/')
    dummy = [x.zfill(2) for x in dag.split('-')]
    dag = "-".join(dummy)

    dagResult = datetime.datetime.strptime(dag, '%d-%m-%Y')
    la, lo = getLanLon(pc)
    seizoenStart = np.asarray(
        [datetime.datetime.strptime(x + '-' + str(dagResult.year), '%d-%m-%Y').timetuple().tm_yday for x in
         ['20-3', '21-6', '22-9', '21-12']])
    mijnSeizoen = seizoen[len(np.where(seizoenStart < dagResult.timetuple().tm_yday)[0])]
    hetweer = haalHetWeerOpDatum(dagResult)
    result = {'dag': dagResult, 'seizoen': mijnSeizoen, 'hetWeer': hetweer, 'latitude': la, 'longitude': lo}
    return result

