# -*- coding: utf-8 -*-
"""
Created on Tue May 27 14:08:35 2025

@author: DiMartino
"""

import pandas as pd
import requests
import xml.etree.ElementTree as ET
from .errors import DimensionsOrKwargsError, NotAListError, TooManyDimensionsError, DifferentDimensionValueError, KwargsError, OtherResponseCodeError, WrongFormatError

def get_all_dataflows(returned="dataframe"):
    """
    This function is used in the search_dataflows function to search for dataflows,
    but it can also be used alone to get all the possible dataflows.

    Returns
    -------
    df : Returns a pandas DataFrame with all the dataflows if you choose the dataframe.
    csv file: Creates a csv file in the path of your code if you choose the csv.

    """
    # This is the ISTAT url for all dataflows
    dataflow_url = "https://esploradati.istat.it/SDMXWS/rest/dataflow/ALL/ALL/LATEST"   
    response = requests.get(dataflow_url)
    response_code = response.status_code
    if response_code == 200:
        response = response.content.decode('utf-8-sig')
        tree = ET.ElementTree(ET.fromstring(response))
        # Namespaces for ISTAT' SDMX dataflows
        namespaces = {
            'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
            'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
            'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
        }
        data = []
        for dataflow in tree.findall('.//structure:Dataflow', namespaces):

            name_it = None
            name_en = None
            for name in dataflow.findall('.//common:Name', namespaces):
                lang = name.get('{http://www.w3.org/XML/1998/namespace}lang')
                if lang == 'it':
                    name_it = name.text
                elif lang == 'en':
                    name_en = name.text
            row = {
                'id': dataflow.get('id'),
                'agencyID': dataflow.get('agencyID'),
                'version': dataflow.get('version'),
                'isFinal': dataflow.get('isFinal'),
                'name_it': name_it,
                'name_en': name_en
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        if returned.casefold() == "dataframe" :  
            return df
        elif returned.casefold() == "csv":
            df.to_csv("all_dataflows_ISTAT.csv")
        else:
            raise WrongFormatError()
    else:
        raise OtherResponseCodeError(response_code)
        

def search_dataflows(search_term, mode="fast", lang="en", returned="dataframe"):
    """
    Allows searching for dataflows starting from strings passed. Can also accept a list.

    Parameters
    ----------
    search_term : String or list of strings, 
        is required to perform a search through the datasets.
    mode : String, 
        can be deep or fast. Deep search requires more requests but also gets the dimensions for datasets in a readable way. The default is "fast".
    lang : String, 
        "en" or "it", the language the search will be performed in. The default is "en".
    returned : String, 
        "dataframe" or "csv", the format to be returned. The default is "dataframe".
 
    Raises
    ------
    errors
        OtherResponseCodeError: when the code response from the API URL is not 200.

    Returns
    -------
    df : Returns a pandas DataFrame with all the dataflows if you choose the dataframe.
    csv file: Creates a csv file in the path of your code if you choose the csv.

    """
    if returned != "dataframe" and returned != "csv":
        raise WrongFormatError()
    # The function must accept either single words or lists
    if isinstance(search_term, str):
        search_term = [search_term]
    df = get_all_dataflows()
    if df.empty:
        print("Error: cannot retrieve dataflows from the ISTAT API. Open a request on Github.")
    
    # Initialize dataframe
    search_df = df.copy()
    search_df = search_df.iloc[:0]
    for term in search_term:
        if lang == "en":
            temp_df = df[df["name_en"].str.contains(term, case=False, na=False)]
            search_df = pd.concat([search_df, temp_df], ignore_index=True)
        elif lang == "it":
            temp_df = df[df["name_it"].str.contains(term, case=False, na=False)]
            search_df = pd.concat([search_df, temp_df], ignore_index=True)
        elif lang == "id":
            temp_df = df[df["id"].str.contains(term, case=False, na=False)]
            search_df = pd.concat([search_df, temp_df], ignore_index=True)
        else:
            print("Language not found.")
    if search_df.empty:
        print(f"Warning: the dataflow {term} could not be found.")
        return None
    if mode == "fast":
        if returned == "dataframe":
            return search_df
        elif returned == "csv":
            search_df.to_csv("requested_data.csv", index=False)
    if mode =="deep":
        deep_search_df = deep_search(search_df)
        if returned == "dataframe":
            return deep_search_df
        elif returned == "csv":
            deep_search_df.to_csv("requested_data.csv", index=False)
        


def deep_search(obj, lang="en", get=False):  
    """
    This function is used by the search_dataflows function if the selected mode is "deep".

    Parameters
    ----------
    obj : Can be a string or a DataFrame.
    lang : String, 
        used to select the language of the search. The default is "en".
    get : Bool, 
        used only when called by the function in get.py. The default is False.

    Raises
    ------
    errors
        OtherResponseCodeError: when the code response from the API URL is not 200.

    Returns
    -------
   df : normal return when used by search_dataflows.
   dict : return when used to count the keys by get.get_data.

    """

      
    namespaces = {
        'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
        'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
        'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common'
    }
    df = obj # Terrible, hopefully temporary workaround that must be resolved otherwise it doesn't work with the get functions.
    if not isinstance(obj, pd.DataFrame):
        df = pd.DataFrame({"id":[obj]})            
    codelist_list = []
    for index, row in df.iterrows():
        dataflow_id = row["id"]
        data_url = f"https://esploradati.istat.it/SDMXWS/rest/availableconstraint/{dataflow_id}/?references=all&detail=full"
    
        response = requests.get(data_url)
        response_code = response.status_code
        if response_code != 200:
            raise OtherResponseCodeError(response_code)
        
        response = response.content.decode('utf-8-sig')
        tree = ET.ElementTree(ET.fromstring(response))
        codelist_dict = {}
        codelist_full_dict = {}
        for key_value in tree.findall('.//common:KeyValue', namespaces):
            key_id = key_value.get('id')
            if not key_id == "TIME_PERIOD":
                values = [value.text for value in key_value.findall('common:Value', namespaces)]
                codelist_dict[key_id] = values
                formatted_dimensions = "; ".join([f"{key}: {', '.join(values)}" for key, values in codelist_dict.items()])
                codelist_full_dict.update(codelist_dict)
        codelist_list.append(formatted_dimensions)

    if get == False:
        df['Dimensions'] = codelist_list
        return df
    return codelist_full_dict
    
    
    