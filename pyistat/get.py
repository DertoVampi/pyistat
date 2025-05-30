# -*- coding: utf-8 -*-
"""
Created on Tue May 27 17:01:35 2025

@author: DiMartino
"""

import pandas as pd
import requests
import xml.etree.ElementTree as ET
from .search import deep_search
from .errors import DimensionsOrKwargsError, NotAListError, TooManyDimensionsError, DifferentDimensionValueError, KwargsError, OtherResponseCodeError, WrongFormatError
from datetime import datetime

def get_data(dataflow_id, dimensions=[], force_url=False, start_period="", end_period="", updated_after="", returned="dataframe", **kwargs):
    """
    

    Parameters
    ----------
    dataflow_id : String, 
        the dataflow id of the dataset.
    dimensions : List, 
        an ordered list of strings of the dimensions. Make sure to leave it null if you use kwargs. The default is [].
    force_url : Bool, 
        used to force the URL request even if the they were not checked against the allowed dimensions. The default is False.
    start_period : Int, 
        used to filter for start period. The default is "".
    end_period : Int, 
        used to filter for end period. The default is "".
    updated_after : Int, 
        used to filter for update period. The default is "".
    returned : String, 
        "dataframe" or "csv", the format to be returned. The default is "dataframe".
    **kwargs : Key=value, 
        each kwarg will be used in place of the keys of the URL. Can't be used together with the dimensions list. Usage: freq="Q", correz="W"...


    Returns
    -------
    df : Returns a pandas DataFrame with all the dataflows if you choose the dataframe.
    csv file: Creates a csv file in the path of your code if you choose the csv.

    """
    if returned != "dataframe" and returned != "csv":
        raise WrongFormatError()
    if dimensions and kwargs:
        print("Warning: either pass a list that is ordered following the order you can find with get_dimensions, or pass args. You cannot pass both.")
        raise DimensionsOrKwargsError
    elif not dimensions and not kwargs:
        dimensions = ["all"]
    elif not isinstance(dimensions, list):
        raise NotAListError
        return None
    elif not force_url and dimensions:
        # Sometimes url checker can bug out for undiscovered reasons, in this case you are free to force the program to request data
        dimensions_dict = deep_search(dataflow_id, get=True)
        if len(dimensions) != len(dimensions_dict.keys()):
            raise TooManyDimensionsError(dimensions, dimensions_dict)
        
        for user_dim, dataflow_dim in zip(dimensions, dimensions_dict.values()):
            if user_dim not in dataflow_dim and user_dim != "":
                raise DifferentDimensionValueError(user_dim, dataflow_dim)
                
    elif not force_url and kwargs:
        dimensions_df = get_dimensions(dataflow_id)
        dimensions_dict = deep_search(dataflow_id, get=True)
        # Check how many dimensions there are
        for _ in range(len(dimensions_dict.keys())):
            dimensions.append("")
        for key, value in kwargs.items():
            check = False
            while not check:
                for index, row in dimensions_df.iterrows():
                    if key.casefold() == row["dimension_id"].casefold():
                        if value.casefold() == row["dimension_value"].casefold():
                            dimensions[row["order"]-1] = value
                            check = True
                if check:
                    break
                raise KwargsError()
    # Checking if time periods are formatted right and building the strings
    dim_string = '.'.join(dimensions)
    if start_period=="" and end_period=="":
        period_string = "all?"
    elif end_period=="" and isinstance(start_period, int):
        period_string = f"all?startPeriod={start_period}"
    elif start_period=="" and isinstance(end_period, int):
        period_string = f"all?endPeriod={end_period}"
    elif start_period=="" and isinstance(end_period, int) and end_period=="" and isinstance(start_period, int):
        period_string = f"all?startPeriod={start_period}&endPeriod={end_period}"
    else:
        print("Warning: variables start_period and end_period are not an int or ''. Removed the period_string.")
        period_string=""
    if updated_after != "" and isinstance(updated_after,int):
        period_string.append(f"&updatedAfter={updated_after}")
    elif updated_after == "":
        easter_egg = "You've been blessed! Hello!"
    else:
        print("Warning: updated_after is not an int. Skipped.")
       
    api_url = rf"https://esploradati.istat.it/SDMXWS/rest/data/{dataflow_id}/{dim_string}/{period_string}"
    response = requests.get(api_url)
    response_code = response.status_code
    if response_code != 200:
        raise OtherResponseCodeError(response_code)
    elif response.status_code == 200:
        response = response.content.decode('utf-8-sig')
        tree = ET.ElementTree(ET.fromstring(response)) 
        namespaces = {
            'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
            'generic': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
            'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
        }
        
        data = []
        for series in tree.findall('.//generic:Series', namespaces):
            series_key = {}
            series_key_element = series.find('generic:SeriesKey', namespaces)
            if series_key_element is not None:
                for value in series_key_element.findall('generic:Value', namespaces):
                    key_id = value.get('id')
                    value_text = value.get('value')
                    series_key[key_id] = value_text


            for obs in series.findall('generic:Obs', namespaces):
                obs_data = series_key.copy()
                obs_dimension = obs.find('generic:ObsDimension', namespaces)
                if obs_dimension is not None:
                    obs_data['TIME_PERIOD'] = obs_dimension.get('value')

                obs_value = obs.find('generic:ObsValue', namespaces)
                if obs_value is not None:
                    obs_data['OBS_VALUE'] = obs_value.get('value')

                data.append(obs_data)

        df = pd.DataFrame(data)

        if df.empty:
            print("No data retrieved. Open a request on GitHub, please.")
            return None
        else:
            if returned == "dataframe":
                return df
            elif returned == "csv":
                df.to_csv(f"{dataflow_id}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)
            

def get_dimensions(dataflow_id, lang="en", get=False, returned="dataframe"):
    """
    

    Parameters
    ----------
    dataflow_id : String, 
        the dataflow id of the dataset.
    lang : String, 
        "en" or "it", the language the search will be performed in. The default is "en".
    get : Bool, 
        used only when called by the function get_dataframe() with force_url=False. The default is False.
    returned : String, 
        "dataframe" or "csv", the format to be returned. The default is "dataframe".

    Returns
    -------
    df : Returns a pandas DataFrame with all the dataflows if you choose the dataframe.
    csv file: Creates a csv file in the path of your code if you choose the csv.

    """
    if returned != "dataframe" and returned != "csv":
        raise WrongFormatError()
    namespaces = {
        'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
        'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
        'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }
    data_url = f"https://esploradati.istat.it/SDMXWS/rest/availableconstraint/{dataflow_id}/?references=all&detail=full"

    response = requests.get(data_url)
    codelist_list = []
    response_code = response.status_code
    if response_code != 200:
        raise OtherResponseCodeError(response_code)
            
    response = response.content.decode('utf-8-sig')
    tree = ET.ElementTree(ET.fromstring(response))
    cube_region = tree.find('.//structure:CubeRegion', namespaces)
    key_values = cube_region.findall('.//common:KeyValue', namespaces)

    codelist_list = []

    for codelist in tree.findall(".//structure:Codelist", namespaces):
        codelist_id = codelist.get('id')[3:]  # Rimuovi il prefisso "CL_"
        codelist_name = codelist.find(f'.//common:Name[@xml:lang="{lang}"]', namespaces).text

        for code in codelist.findall('.//structure:Code', namespaces):
            code_id = code.get('id')
            code_name = code.find(f'.//common:Name[@xml:lang="{lang}"]', namespaces).text

            for idx, key_value in enumerate(key_values):
                for value in key_value.findall('common:Value', namespaces):
                    if value.text == code_id:
                        codelist_list.append({
                            'dimension_id': codelist_id,
                            'dimension_name': codelist_name,
                            'dimension_value': code_id,
                            'value_explanation': code_name,
                            'order': idx + 1
                        })
                        break

    if not get:
        df = pd.DataFrame(codelist_list)
        if returned == "dataframe":
            return df
        elif returned == "csv":
            df.to_csv(f"{dataflow_id}_dimensions")
    else:
        return codelist_list
    