import importlib.resources
import json
import unidecode
import numpy as np
import pandas as pd


with importlib.resources.open_text("nomquamgender", "name_data.json") as file:
    name_data = json.load(file)  


def annotate(names):
    """Annotate names with name-gender data.

    Parameters
    -------------------
    names: str or list of strings
        A name or list of names. 
        If a single name is given, it will be converted to a list. 
        Each name will be cast to a string, made lowercase, and stripped of leading and trailing whitespaces. 
        Diacritics will also be removed.
        If a name contains spaces it will be split on spaces and the first substring will be used.
    
    Returns
    -------------------
    A pandas DataFrame with one row for each name and the following columns: name given, string used, # of sources, # of counts, p(f). 
    If a name is not found both # of sources and # of counts will be zero; p(f) will be np.nan.
    See dump() documentation for further details on the name-gender data used to annotate names.
    """  
    if type(names) != list:
        names = [names]
        
    annotations = []
    for name in names:
        used = unidecode.unidecode(str(name)).lower().strip().split(' ')[0]
        
        try:
            info = name_data[used]
        except:
            info = [0, 0, np.nan]
            
        annotations.append([name, used] + info)
            
    return pd.DataFrame(annotations,
                        columns=['given', 'used', 'sources', 'counts', 'p(f)'])


def dump():
    """Returns dictionary of name-gender data. 

    Each key is a name. Each value is a list: [# of sources, # of counts, p(f)]. 
    # of sources reflects the number of data sources with data on this name.
    # of counts reflects the number of empirical observations these data sources collectively have for this name. It is possible for this value to be zero, as some sources give an estimate without reference to explicit empirical observations.
    p(f) is an estimate of how strongly a name is gendered female and by extension an estimate of the probability that an individual with this name is typically gendered female.
    """
    return name_data