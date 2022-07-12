import importlib.resources
import json
import unidecode
import numpy as np
import pandas as pd


with importlib.resources.open_text("nomquamgender", "name_data.json") as file:
    name_data = json.load(file)

taxonomy_labels = ['Gendered', 'Conditionally Gendered (country)',
                   'Conditionally Gendered (decade)', 'Weakly Gendered', 'No Data'] 


def annotate(names, reference = None):
    """Annotate names with name-gender data.

    Parameters
    -------------------
    names: str or list of strings
        A name or list of names. 
        If a single name is given, it will be converted to a list. 
        Each name will be cast to a string, made lowercase, and stripped of leading and trailing whitespaces. 
        Diacritics will also be removed.
        The full name will be used if found and if not found the name will be split on spaces and the first substring will be used.
    reference (optional): dict of name-gender data
        Each key should be a name. Each value should be a list: [# of sources, # of counts, p(gf)].
        If provided, this dictionary will be used in place of the name_data dictionary we provide by default.
        This option is useful in the event that one wants to combine our data, accessed via nqg.dump(), with additional name-gender data.
    
    Returns
    -------------------
    A pandas DataFrame with one row for each name and the following columns: name given, string used, # of sources, # of counts, p(gf). 
    If a name is not found both # of sources and # of counts will be zero; p(gf) will be np.nan.
    See nqg.dump() documentation for further details on the name-gender data used to annotate names.
    """  
    if type(names) != list:
        names = [names]
        
    annotations = []
    for name in names:
        parsed = unidecode.unidecode(str(name)).lower().strip()
        for used in [parsed, parsed.split(' ')[0]]:
            try:
                info = reference[used] if reference else name_data[used]
                break
            except:
                info = [0, 0, np.nan, np.nan]
            
        annotations.append([name, used] + info[:3])
            
    return pd.DataFrame(annotations,
                        columns=['given', 'used', 'sources', 'counts', 'p(gf)'])


def dump():
    """Returns dictionary of name-gender data. 

    Each key is a name. Each value is a list: [# of sources, # of counts, p(gf)]. 
    # of sources reflects the number of data sources with data on this name.
    # of counts reflects the number of empirical observations these data sources collectively have for this name. It is possible for this value to be zero, as some sources give an estimate without referencing explicit empirical observations.
    p(gf) is an estimate of how strongly a name is gendered female and by extension an estimate of the probability that an individual with this name is typically gendered female.
    """
    return {n:info[:3] for n, info in name_data.items()}


def compute_uncertainty_id(u):
    """Compute the index corresponding to uncertainty threshold."""
    return max(0, min(int((u + 1e-6)//.05) - 1, 8))


def taxonomize(names, max_uncertainty = 0.1, min_counts = 10):
    """Use taxonomy to show overall composition of sample in terms of coverage and degree gendered.

    Parameters
    -------------------
    names: str or list of strings
        A name or list of names. 
        If a single name is given, it will be converted to a list. 
        Each name will be cast to a string, made lowercase, and stripped of leading and trailing whitespaces. 
        Diacritics will also be removed.
        The full name will be used if found and if not found the name will be split on spaces and the first substring will be used.
    max_uncertainty: parameter controlling how informative of either gendered group a name must be to be classified as gendered.
        The value should range from 0.05 to 0.45 and will be rounded down to the nearest increment of 0.05
        Technically, this value is a threshold on the absolute value of the distance of p(gf) from 0.5.
        Names with a p(gf) whose absolute value from 0.5 is greater than or equal to the threshold are considered gendered.
        The default max_uncertainty is 0.1.
    min_counts: parameter controlling how many observations of a name in the reference data are needed for a name to be classified as high coverage.
        Names with greater than or equal to this number of observations (counts) are high coverage, all others low coverage.
        The default min_counts is 10.
    
    Returns
    -------------------
    A pandas DataFrame that reflects how many names of those given fall into each of 10 leaves of the taxonomy used.
    The names are split into Low Coverage and High Coverage, constituting the columns and reflecting the number of observations on each name.
    The rows correspond to how gendered names are, with Gendered hosting the most informative names.
    Conditionally Gendered names (either given country or decade) are only gendered if additional information is used to subset the reference data.
    Weakly Gendered names fall above the max_uncertainty threshold.
    No Data names are those that do not appear in the reference data.
    """
    max_u_id = compute_uncertainty_id(max_uncertainty)
    df_labels = taxonomy_labels
    df_labels[0] = 'Gendered (u ≤ %.2f)'%(np.linspace(.05,.45,9)[max_u_id])

    if type(names) != list:
        names = [names]
        
    categories = np.zeros((5,2)).astype(int)
    for name in names:
        parsed = unidecode.unidecode(str(name)).lower().strip()
        for used in [parsed, parsed.split(' ')[0]]:
            try:
                info = name_data[used]
                if type(info[-1]) is list:
                    category = info[-1][max_u_id]
                else:
                    category = info[-1]

                classification = (category+1, int(info[1] >= min_counts))
                break
            except:
                classification = (0, 0)
        categories[classification] += 1

    return pd.DataFrame(categories[::-1],
                        index = df_labels, columns = ['Low Coverage (c < %d)'%min_counts, 'High Coverage'])