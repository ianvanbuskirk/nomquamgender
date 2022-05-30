# nom quam gender

A simple package containing data and a few functions to support name-based gender-classification in scientific research.

## Installation

```
pip install nomquamgender
```

## Usage

```python
import nomquamgender as nqg
nqg.annotate('clara')
```

|    | given   | used   |   sources |   counts |   p(f) |
|---:|:--------|:-------|----------:|---------:|-------:|
|  0 | clara   | clara  |        31 |   492337 |  0.992 |

```python
nqg.annotate(['András','Jean','Mitsuko'])
```

|    | given   | used    |   sources |   counts |   p(f) |
|---:|:--------|:--------|----------:|---------:|-------:|
|  0 | András  | andras  |        24 |    13010 |  0.001 |
|  1 | Jean    | jean    |        31 |  2525377 |  0.477 |
|  2 | Mitsuko | mitsuko |        14 |      925 |  0.981 |

```python
import pandas as pd
name_data = nqg.dump()

df = pd.DataFrame([(n,c,p) for n,(s,c,p) in name_data.items()],
                              columns = ['name','counts','p(f)']).set_index('name')

df.sort_values(by='counts',ascending=False).head(10)
```

| name    |      counts |   p(f) |
|:--------|------------:|-------:|
| john    | 5.73712e+06 |  0.001 |
| robert  | 5.71833e+06 |  0     |
| james   | 5.71246e+06 |  0.001 |
| michael | 5.04746e+06 |  0.001 |
| david   | 4.88524e+06 |  0.001 |
| william | 4.6944e+06  |  0     |
| mary    | 4.5431e+06  |  0.98  |
| joseph  | 3.39841e+06 |  0.002 |
| daniel  | 3.2188e+06  |  0.016 |
| thomas  | 3.17053e+06 |  0.001 |
