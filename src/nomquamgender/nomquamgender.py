import importlib.resources
import json
import unidecode
import numpy as np
import pandas as pd


with importlib.resources.open_text("nomquamgender", "name_data.json") as file:
    name_data = json.load(file)

with importlib.resources.open_text("nomquamgender", "example_names.json") as file:
    example_names = json.load(file)
 

def bold_string(s):
    """Boldface string."""
    return '\033[1m' + str(s) + '\033[0m'


def compute_uncertainty(pgf):
    """Compute uncertainty associated with single p(gf) value or a numpy array of p(gf) values."""
    return .5 - np.abs(.5 - pgf)


def type_check_names(names):
    """Turn names into list if a numpy array or a single string."""
    if type(names) == np.ndarray:
        names = list(names)
    elif type(names) == str:
        names = [names]
    return names


class NBGC():
    """A name-based gender classification model.

    Parameters
    -------------------
    reference (optional): dict of name-gender data
        Each key should be a name. Each value should be a list: [# of sources, # of counts, p(gf)].
        If provided, this dictionary will be used in place of the name_data dictionary used by default.
        This option is useful in the event that one wants to combine the name_data dictionary, accessed via nqg.dump(), with additional name-gender data.
    threshold (optional): float in range [0, .49]
        Parameter controlling how informative of either gendered group a name must be to be classified.
        Names associated with p(gf) values more uncertain than this threshold are not classified.
        Technically, this value is a threshold on the following quantity: 0.5 - abs(.5 - p(gf)).
        By default this threshold is set to 0.1 meaning names with p(gf) values in the range (.1, .9) are not classified while names in the ranges [0, .1] and [.9, 1] are classified.
        This value may be set directly and the tune function can be used to help inform this choice.
        Note that calling the tune function will by default use a heuristic to update this parameter.
    """

    def __init__(self, reference = name_data, threshold = .1):
        self.reference = reference
        self.threshold = threshold


    def get_pgf(self, names):
        """Annotate names with given reference data and return a list of only the p(gf) for each name.
        """
        return [n[-1] for n in self.annotate(names)]


    def classify(self, names):
        """Use given reference data and set threshold to classify names.

        Parameters
        -------------------
        names: str or list of strings
            A name or list of names to be classified.
        
        Returns
        -------------------
        List of classifications with 'gm' representing names gendered male, 'gf' those gendered female, and '-' names not classified.
        """
        self.threshold = max(0, min(self.threshold, .49))
        pgf = np.array(self.get_pgf(names))
        uncertainties = compute_uncertainty(pgf)
        
        classifications = []
        for p, u in zip(pgf, uncertainties):
            if u <= self.threshold:
                classifications.append('gm' if p < .5 else 'gf')
            else:
                classifications.append('-')
        return classifications


    def _print_thresholds(self, candidates, classifiable, i):
        """Print out thresholds and the percentage of the dataset classifiable at that threshold."""
        candidates = [c[1:] for c in np.array(candidates).astype(str)]
        percentages = [s+'%' for s in (100*classifiable).astype(int).astype(str)]
        candidates[i] = bold_string(candidates[i])
        percentages[i] = bold_string(percentages[i])
        df = pd.DataFrame(percentages, index = candidates, columns=['percentage'])
        df.index.name = 'threshold'
        print('---')
        print(df.T.to_string())


    def tune(self, names, update = True, verbose = True, candidates = np.linspace(.3,.02,15).round(2)):
        """Heuristically update model max uncertainty threshold and print the percentage of sample classified with different thresholds.

        Parameters
        -------------------
        names: str or list of strings
            A name or list of names to be classified.
        verbose: bool
            If True, a sequence of threshold, percentage pairs are printed along with the heuristically selected threshold.
        update: bool
            If True, the model threshold is updated to take the value of the heuristically selected threshold.
        candidates: iterable of values in range [0, .49] sorted in descending order
            Sequence of candidate threshold values
        
        Returns
        -------------------
        None
        """
        candidates = np.sort(np.unique(np.clip(candidates,0.,.49)))[::-1]

        uncertainties = compute_uncertainty(np.array(self.get_pgf(names)))
        classifiable = np.array([np.mean(uncertainties <= t) for t in candidates])

        threshold = candidates[0]
        i = 0
        for t, p in zip(candidates[1:], classifiable[1:]):            
            if p < .85:
                break
            elif t < .1 and p < .9:
                break
            else:
                threshold = t
                i += 1
                
        if update is True:
            self.threshold = threshold
            print('max uncertainty threshold set to %s, classifies %s%% of sample'%(bold_string(threshold),
                                                                                    bold_string('%d'%(100*classifiable[i]))
                                                                                ))
        else:
            print('max uncertainty threshold remains %s, threshold of %s would classify %s%% of sample'%(
                                                                   bold_string(self.threshold),
                                                                   bold_string(threshold),
                                                                   bold_string('%d'%(100*classifiable[i]))
                                                                ))

        if verbose:
            self._print_thresholds(candidates, classifiable, i)

        

    def annotate(self, names, as_df = False):
        """Annotate names with name-gender data.

        Parameters
        -------------------
        names: str or list of strings
            A name or list of names. 
            If a single name is given, it will be converted to a list. 
            Each name will be cast to a string, made lowercase, and stripped of leading and trailing whitespaces. 
            Diacritics will also be removed.
            The full name will be used if found and if not found the name will be split on spaces and the first substring will be used.
        as_df (optional): bool
            False by default, if True annotations will be return as a pandas dataframe rather than a list of lists.
        
        Returns
        -------------------
        If as_df is False: a list of lists, with each list of the form [name given, string used, # of sources, # of counts, p(gf)]
        If as_df is True: a pandas DataFrame with one row for each name and the following columns: name given, string used, # of sources, # of counts, p(gf). 
        If a name is not found both # of sources and # of counts will be zero; p(gf) will be np.nan.
        See nqg.dump() documentation for further details on the name-gender data used to annotate names.
        """  
        names = type_check_names(names)
            
        annotations = []
        for name in names:
            parsed = unidecode.unidecode(str(name)).lower().strip()
            for used in [parsed, parsed.split(' ')[0]]:
                try:
                    info = self.reference[used]
                    break
                except:
                    info = [0, 0, np.nan, np.nan]
                
            annotations.append([name, used] + info[:3])
        if as_df:
            return pd.DataFrame(annotations,
                                columns=['given', 'used', 'sources', 'counts', 'p(gf)'])
        else:
            return annotations


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
    max_uncertainty: float in range [0.05, 0.45]
        Parameter controlling how informative of either gendered group a name must be to be classified as gendered.
        Names associated with p(gf) values more uncertain than this value are not classified as gendered.
        Technically, this value is a threshold on the absolute value of the distance of p(gf) from 0.5.
        By default this threshold is set to 0.1 meaning names with p(gf) values in the range (.1, .9) are not classified as gendered while names in the ranges [0, .1] and [.9, 1] are classified as gendered.
        The value should range from 0.05 to 0.45 and will be rounded down to the nearest increment of 0.05
    min_counts: int
        Parameter controlling how many observations of a name in the reference data are needed for a name to be classified as high coverage.
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
    df_labels = ['Gendered (u ≤ %.2f)'%(np.linspace(.05,.45,9)[max_u_id]),
                 'Conditionally Gendered (country)',
                 'Conditionally Gendered (decade)', 
                 'Weakly Gendered', 'No Data']

    names = type_check_names(names)
        
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