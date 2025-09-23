# -*- coding: utf-8 -*-
"""
Created on Tue May 27 17:01:35 2025

@author: DiMartino
"""
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from .errors import DimensionsOrKwargsError, NotAListError, TooManyDimensionsError, TooManyDimensionsError2, DifferentDimensionValueError, KwargsError, OtherResponseCodeError, WrongFormatError
from datetime import datetime

def get_data(dataflow_id, dimensions=[], force_url=False, start_period="", end_period="", updated_after="", returned="dataframe", select_last_edition=True, debug_url=False, **kwargs):
    """
    

    Parameters
    ----------
    dataflow_id : String, 
        the dataflow id of the dataset.
    dimensions : List, 
        an ordered list of strings of the dimensions. Make sure to leave it null if you use kwargs. The default is [].
    force_url : Bool, 
        used to force the URL request even if the they were not checked against the allowed dimensions. The default is False.
     debug_url : Bool, 
         used to obtain the generated URL for manual debugging. The default is False.
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
    def fetch_dimensions_df():
        nonlocal dimensions_df
        if dimensions_df.empty:
            dimensions_df = get_dimensions(dataflow_id)
        return dimensions_df

    dimensions = [string.upper() for string in dimensions]
    dimensions_df = pd.DataFrame() # Initialize to avoid using complex syntax to check if it exists
    if returned != "dataframe" and returned != "csv":
        raise WrongFormatError()
    if dimensions and kwargs:
        raise DimensionsOrKwargsError
    elif not dimensions and not kwargs:
        dimensions = ["all"]
    elif not isinstance(dimensions, list):
        raise NotAListError
        return None
    elif not force_url and dimensions:
        # Sometimes url checker can bug out for undiscovered reasons, in this case you are free to force the program to request data
        dimensions_df = fetch_dimensions_df()
        if len(dimensions) != (len(dimensions_df["dimension_id"].unique())):
            raise TooManyDimensionsError(dimensions, (len(dimensions_df["dimension_id"].unique())))
        
        counter = 0
        for _, user_dim in enumerate(dimensions):
            user_dim = user_dim.upper()
            if user_dim != "":
                counter_dim_df = dimensions_df[dimensions_df["order"] == counter+1]
                if user_dim in counter_dim_df["dimension_value"].tolist():
                    counter += 1
                else:
                    raise DifferentDimensionValueError(user_dim, counter_dim_df["dimension_id"].unique(), counter_dim_df["dimension_value"].tolist())
            else:
                counter += 1 
                
    elif kwargs: # The check must be done even if force_url==True as the program needs to fetch the positioning for dimension values.
        dimensions_df = fetch_dimensions_df()
        # Check how many dimensions there are
        for _ in range(len(dimensions_df["dimension_id"].unique())):
            dimensions.append("")
        for key, value in kwargs.items():
            check = False
            while not check:
                for index, row in dimensions_df.iterrows():
                    if key.casefold() == row["dimension_id"].casefold():
                        if value.casefold() == row["dimension_value"].casefold():
                            dimensions[row["order"]-1] = value # Order-1 is needed as order row starts from 1, order for lists starts from 0
                            check = True
                if check:
                    break
                raise KwargsError(key, value)
    
    # Important part: this feature allows users to always select the latest edition ISTAT has for the dataflow.
    # It uses the function find_last_edition to iter and find the last edition and automatically fills it for the user.
    # It won't work if an edition is manually added via kwargs or dimensions. It also checks whether the correct number of dimensions was added in order to gracefully fail.
    # There are multiple checks: 
    # Check if dimensions_df is already fetched from the controlo before to avoid another call;
    # Check if kwargs are used and t_bis is not defined;
    # Check if the dimensions are less than the order position for the dimensions.
    if select_last_edition==True:
        if dimensions_df.empty:
            dimensions_df = fetch_dimensions_df()
        last_edition = find_last_edition(dimensions_df)
        if last_edition is not None:
            filtered_df = dimensions_df.loc[dimensions_df['dimension_id'] == 'T_BIS', 'order']
            order_values = filtered_df.tolist()
            order = int(order_values[0])-1
            if kwargs and "t_bis" in kwargs:
                print("Warning: you passed an edition value 't_bis=x' with select_last_edition set on True. Remove the t_bis variable if you want the module to automatically fetch the last edition.")
                pass
            if order >= len(dimensions):
                raise TooManyDimensionsError2(dimensions, (len(dimensions_df["dimension_id"].unique())))
            if dimensions[order] != "":
                print("Warning: you passed an edition value for the edition in the dimensions provided, with select_last_edition set on True. Remove the t_bis variable if you want the module to automatically fetch the last edition.")
                pass
            else:
                try:
                    dimensions[order] = last_edition
                except TooManyDimensionsError as e:
                    print(e)
        else:
            print("Edition dimension not found. Skipping auto-fetching.")
    # Checking if time periods are formatted right and building the strings
    dim_string = '.'.join(dimensions)
    if start_period=="" and end_period=="":
        period_string = "all?"
    elif end_period=="":
        period_string = f"all?startPeriod={start_period}"
    elif start_period=="":
        period_string = f"all?endPeriod={end_period}"
    elif start_period=="" and end_period=="" and isinstance(start_period, int):
        period_string = f"all?startPeriod={start_period}&endPeriod={end_period}"
        period_string=""
    if updated_after != "":
        if period_string:
            period_string.append(f"&updatedAfter={updated_after}")
        else:
            period_string = f"all=updatedAfter={updated_after}"
    elif updated_after == "":
        easter_egg = "You've been blessed! Hello, pleased to meet you!"
    
    # Build the string and make the request: if the response is 200, then keep going.
    api_url = rf"https://esploradati.istat.it/SDMXWS/rest/data/{dataflow_id}/{dim_string}/{period_string}"
    if debug_url==True:
        print(api_url)
    response = requests.get(api_url, timeout=30)
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


def find_last_edition(df):
    try:
        edition_df = df[df["dimension_id"] == "T_BIS"]
    except:
        return None

    edition_list = edition_df["dimension_value"].tolist()
    date_info = []

    for edition in edition_list:
        year = int(edition[0:4])
        month_start = edition.find("M") + 1
        month_end = month_start + 2 if edition[month_start:month_start + 2].isdigit() else month_start + 1
        month = int(edition[month_start:month_end])

        if "G" in edition:
            day_start = edition.find("G") + 1
            day_end = day_start + 2 if edition[day_start:day_start + 2].isdigit() else day_start + 1
            day = int(edition[day_start:day_end])
            date_part = f"{year}{str(month).zfill(2)}{str(day).zfill(2)}"
        else:
            day = ""
            date_part = f"{year}{str(month).zfill(2)}"

        suffix = ""
        if "_" in edition:
            suffix_pos = edition.find("_")
            suffix = edition[suffix_pos:]

        date_info.append((int(date_part), suffix))

    if not date_info:
        return None

    date_info.sort(reverse=True, key=lambda x: x[0])
    last_date, last_suffix = date_info[0]

    last_date_str = str(last_date)
    year = last_date_str[0:4]
    yearless = last_date_str[4:]

    if "G" in edition_list[0]:
        month = yearless[0:2] if yearless[0] != "0" else yearless[1:2]
        day = yearless[-2:] if yearless[-2] != "0" else yearless[-1]
        chosen_edition = f"{year}M{month}G{day}{last_suffix}"
    else:
        month = yearless[0:2] if yearless[0] != "0" else yearless[1:2]
        chosen_edition = f"{year}M{month}{last_suffix}"

    return chosen_edition

    
            

def get_dimensions(dataflow_id, lang="en", returned="dataframe", debug_url=False):
    """
    

    Parameters
    ----------
    dataflow_id : String, 
        the dataflow id of the dataset.
    lang : String, 
        "en" or "it", the language the search will be performed i n. The default is "en".
    get : Bool, 
        used only when called by the function get_dataframe() with force_url=False. The default is False.
    returned : String, 
        "dataframe" or "csv", the format to be returned. The default is "dataframe".
    debug_url: Bool, 
        Set to True if you want the URL the request is being sent to printed to the console.

    Returns
    -------
    df : Returns a pandas DataFrame with all the dataflows if you choose the dataframe.
    csv file: Creates a csv file in the path of your code if you choose the csv.

    """
    if "," in dataflow_id:        
        parts = dataflow_id.split(",")
        dataflow_id = parts[1]
        
    if returned != "dataframe" and returned != "csv":
        raise WrongFormatError()
    namespaces = {
        'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
        'structure': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure',
        'common': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common',
        'xml': 'http://www.w3.org/XML/1998/namespace'
    }
    data_url = f"https://esploradati.istat.it/SDMXWS/rest/availableconstraint/{dataflow_id}/?references=all&detail=full"
    if debug_url == True:
        print(data_url)

    response = requests.get(data_url, timeout=30)
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
        codelist_id = codelist.get('id')[3:]  # The prefix "CL_" must be removed as it is internal
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

    key_values = cube_region.findall('.//com:KeyValue', namespaces)

    for idx, key_value in enumerate(key_values):
        dimension_name = key_value.get('id')
        if dimension_name is None:
            continue  # skip if no id attribute
        # Find all Value elements under this KeyValue
        values = key_value.findall('com:Value', namespaces)
        for value in values:
            if value.text is not None:
                codelist_list.append({
                    'dimension_name': dimension_name,
                    'dimension_value': value.text.strip(),
                    'order': idx + 1
                })
        
        
    df = pd.DataFrame(codelist_list)
    if returned == "dataframe":
        return df
    elif returned == "csv":
        df.to_csv(f"{dataflow_id}_dimensions")