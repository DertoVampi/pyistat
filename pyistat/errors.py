# -*- coding: utf-8 -*-
"""
Created on Fri May 30 12:37:57 2025

@author: DiMartino
"""

class DimensionsOrKwargsError(Exception):
    """
    Warning: Either use a dimensions list (make sure it is ordered, get the correct
    order from get_dimensions) or use kwargs, never both.
    """
    def __init__(self, message="Warning: either pass the dimensions in the correct order as a list or use kwargs."):
        self.message = message
        super().__init__(self.message)
        
class NotAListError(Exception):
    """
    Warning: the variable Dimensions must be a list or null. Remember that if you provide a list,
          you must also provide wildcard values with a void string like ''.
    """
    def __init__(self, message="""Warning: the variable Dimensions must be a list or null. Remember that if you provide a list,
          you must also provide wildcard values with a void string like ''."""):
        self.message = message
        super().__init__(self.message)
        
class TooManyDimensionsError(Exception):
    """
    The dimensions you chose are less or more than those required from the dataflow.
    """
    def __init__(self, dimensions, dimensions_dict, message=None):
        if message is None:
           message = f"""Warning: the dimensions you chose are {len(dimensions)}, while the dimensions
                 requested by the dataflow are {len(dimensions_dict.keys())}. If you believe
                 this is a mistake, you can force the url by adding force_url=True to the function call."""
        self.message = message
        super().__init__(self.message)
        
class DifferentDimensionValueError(Exception):
    """
    Different dimensions found.
    """
    def __init__(self, user_dim, dataflow_dim, message=None):
        if message is None:
            message = f"""Warning: the dimension value {user_dim} cannot be found in the possible values
                  for the dimension {dataflow_dim}. Check if the order of the dimensions is correct.
                  If you believe this is an error, you can force the url by adding
                  force_url=True to the function call."""
        self.message = message
        super().__init__(self.message)
        
class KwargsError(Exception):
    """
    Error while using arguments. Check the name and value of arguments or use a list.
    """
    def __init__(self, message="Error while using arguments. Check the name and value of arguments or use a list.."):
        self.message = message
        super().__init__(self.message)
        
class OtherResponseCodeError(Exception):
    """
    Different response code from 200 found.
    """
    def __init__(self, response_code, message=None):
        if message is None:
            message = f"""Error {response_code}. Check SDMX documentation and double check the dataflow id spelling."""
        self.message = message
        super().__init__(self.message)
        
        
class WrongFormatError(Exception):
    """
    Error while determining format.
    """
    def __init__(self, message="Wrong format requested. Choose either 'csv' or 'dataframe'."):
        self.message = message
        super().__init__(self.message)