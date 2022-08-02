<!-- omit in toc -->
# nomquamgender (nqg)

A simple package containing data and a few functions to support name-based gender classification in scientific research.

Conceptually, this method of classification does not reflect gender _identity_, _expression_ or a _perception_ of either but a structural dimension of gender: that is, how gender is likely to have structured an individual's life. Rather than fine-grained, anthropological accounts uniquely crafted to glimpse this gendering process our method provides only the possibility of tapping into a single, narrow stream of relatively inert data exhaust: names. As such, the classifications we offer are limited[^1]. How gender structures "social space" ([Bourdieu, 1989](https://www.jstor.org/stable/202060?seq=1)) will forever elude our attempts to "reduce human group life to variables and their relations" ([Blumer, 1956](https://www.jstor.org/stable/2088418?seq=1)). Thus, we name what we capture here nomquamgender: a nonsense name made of the French _nom_, Latin _quam_, and English _gender_. Fully translated to English as "name rather than gender", this signifies that what our method can offer is a reflection of the gendering process, a shadow of the way gender structures social space, but only that, and nothing more.

Computationally, this package provides access to name-gender association data that can be used to classify individuals into gendered groups. These gendered groups are best thought of as individuals likely to have been most typically gendered female and individuals likely to have been most typically gendered male. When discussing these classifications in practice one ought to use this language of _gendered female_ and _gendered male_ rather than more traditional sex/gender language[^2]. Classifications themselves are not made by our package, but rather the probability that a name belongs to an individual gendered female, p(gf), is provided. This method is comparable in performance to the most reliable paid name-based gender classification services ([Van buskirk, 2022](https://github.com/ianvanbuskirk/nbgc)).

---
<!-- omit in toc -->
## Contents

- [Install and Import](#install-and-import)
- [Annotate Names](#annotate-names)
- [Classify Names](#classify-names)
  - [Example 1](#example-1)
  - [Example 2](#example-2)
  - [Example 3](#example-3)
- [Taxonomize Names](#taxonomize-names)
- [Retrieve Reference Data](#retrieve-reference-data)
- [Use Additional Data](#use-additional-data)
  - [Combine and Replace](#combine-and-replace)
  - [Combine and Average](#combine-and-average)

---

## Install and Import

```console
pip install nomquamgender
```

```python
import nomquamgender as nqg
```

---

## Annotate Names

```python
model = nqg.NBGC()
model.annotate(['András Schiff', 'Mitsuko Uchida', 'Jean Rondeau'], as_df=True)
```

|    | given          | used    |   sources |   counts |   p(gf) |
|---:|:---------------|:--------|----------:|---------:|--------:|
|  0 | András Schiff  | andras  |        24 |    13010 |   0.001 |
|  1 | Mitsuko Uchida | mitsuko |        14 |      925 |   0.981 |
|  2 | Jean Rondeau   | jean    |        31 |  2525377 |   0.477 |

```python
model.annotate('Clara Wieck')
# [['Clara Wieck', 'clara', 31, 492337, 0.992]]
```

---

## Classify Names

```python
example_names = nqg.example_names
example_subset = example_names[:7]
# ['shoko', 'mark', 'andres', 'david', 'marian', 'luisa', 'moira']
```

### Example 1

```python
model = nqg.NBGC()
model.tune(example_names)
```

|  threshold  | .3   | .28   | .26   | .24   | .22   | .2   | .18   | .16   | .14   | .12   | .1   | .08   | .06   | .04   | .02   |
|:-----------|:-----|:------|:------|:------|:------|:-----|:------|:------|:------|:------|:-----|:------|:------|:------|:------|
| percentage | 94%  | 94%   | 93%   | 91%   | 90%   | 90%  | 90%   | 87%   | **86%**   | 84%   | 83%  | 82%   | 80%   | 76%   | 72%   |

max uncertainty threshold set to **0.14**, classifies **86%** of sample

```python
model.classify(example_subset)
# ['gf', 'gm', 'gm', 'gm', '-', 'gf', 'gf']
```

### Example 2

```python
model = nqg.NBGC()
model.get_pgf(example_subset)
# [0.899, 0.0, 0.0, 0.001, 0.634, 0.991, 0.991]
```

```python
model.tune(example_names, update=False, verbose=False)
```

max uncertainty threshold remains **0.1**, threshold of **0.14** would classify **86%** of sample

```python
model.classify(example_subset)
# ['-', 'gm', 'gm', 'gm', '-', 'gf', 'gf']
```

### Example 3

```python
model = nqg.NBGC()
model.tune(example_names, update=False, candidates=[.45,.35,.25,.15,.05])
```

|  threshold  | .45   | .35   | .25   | .15   | .05   |
|:-----------|:------|:------|:------|:------|:------|
| percentage | 98%   | 97%   | 92%   | **87%**   | 78%   |

max uncertainty threshold remains **0.1**, threshold of **0.15** would classify **87%** of sample

```python
model.threshold = .45
model.classify(example_subset)
# ['gf', 'gm', 'gm', 'gm', 'gf', 'gf', 'gf']
```

---

## Taxonomize Names

```python
nqg.taxonomize(nqg.example_names)
```

|                                  |   Low Coverage (c < 10) |   High Coverage |
|:---------------------------------|------------------------:|----------------:|
| Gendered (u ≤ 0.10)              |                      24 |             185 |
| Conditionally Gendered (country) |                       1 |              19 |
| Conditionally Gendered (decade)  |                       1 |               0 |
| Weakly Gendered                  |                       1 |              19 |
| No Data                          |                       0 |               0 |

---

## Retrieve Reference Data

```python
name_data = nqg.dump()
```

```python
import pandas as pd

df = pd.DataFrame([(n,c,p) for n,(s,c,p) in name_data.items()],
                              columns = ['name','counts','p(gf)']).set_index('name')

df.sort_values(by='counts',ascending=False).head(8)
```

| name    |      counts |   p(gf) |
|:--------|------------:|--------:|
| john    | 5.73712e+06 |   0.001 |
| robert  | 5.71833e+06 |   0     |
| james   | 5.71246e+06 |   0.001 |
| michael | 5.04746e+06 |   0.001 |
| david   | 4.88524e+06 |   0.001 |
| william | 4.6944e+06  |   0     |
| mary    | 4.5431e+06  |   0.98  |
| joseph  | 3.39841e+06 |   0.002 |

---

## Use Additional Data

```python
name_data = nqg.dump()
alternative = {'nomquam':[3,1,.4], 'jean':[10,1000,1]}
```

```python
model = nqg.NBGC(reference=name_data)
model.annotate(['nomquam','jean'], as_df=True)
```

|    | given   | used    |   sources |   counts |   p(gf) |
|---:|:--------|:--------|----------:|---------:|--------:|
|  0 | nomquam | nomquam |         0 |        0 | nan     |
|  1 | jean    | jean    |        31 |  2525377 |   0.477 |

### Combine and Replace

```python
model.reference = dict(name_data, **alternative)
model.annotate(['nomquam','jean'], as_df=True)
```

|    | given   | used    |   sources |   counts |   p(gf) |
|---:|:--------|:--------|----------:|---------:|--------:|
|  0 | nomquam | nomquam |         3 |        1 |     0.4 |
|  1 | jean    | jean    |        10 |     1000 |     1   |

### Combine and Average

```python
for n, v in alternative.items():
    d = name_data[n] if n in name_data.keys() else [0,0,-1]
    s = d[0] + v[0]
    model.reference[n] = [s, d[1] + v[1], (d[0]/s)*d[2] + (v[0]/s)*v[2]]
    
model.annotate(['nomquam','jean'], as_df=True)
```

|    | given   | used    |   sources |   counts |    p(gf) |
|---:|:--------|:--------|----------:|---------:|---------:|
|  0 | nomquam | nomquam |         3 |        1 | 0.4      |
|  1 | jean    | jean    |        41 |  2526377 | 0.604561 |

[^1]: An important aside: The core conceptual limitation of using names to reflect the dimension of gender we are interested in is not that classifications are constrained by a "gender binary", but that how gender structures our lives is complex, heterogeneous, variable across time, and interacts with other social forces, whether or not this structuring is best thought of in binary terms. It can be appealing to think that using name-gender _associations_ rather than binary _classifications_ somehow sidesteps an important issue and in some way captures that gender is "non-binary" (e.g. rather than act as if all Taylor's are gendered male, one works with the probability that someone with the name Taylor is gendered male: 0.64). While these continuous associations can be quantitatively useful, they do not offer a conceptual escape hatch to those troubled by binary classifications. Uncertainty does not a non-binary variable make, and in no way do the probabilities we estimate more meaningfully map onto identities, expressions, or lived experiences than their derivative classifications. It's instructive to think of how intentionally taking on a weakly gendered name, such as taylor, leslie, or kim, would (potentially) undermine the gender binary: in our current climate one would not be signaling something non-binary but rather partially obfuscate whatever gendered information names tend to convey. Thoughtfully using binary classifications in scientific research to study the structural dimension of gender need not conflict with our understanding and appreciation of gender in other contexts. As such, name-based gender classification can be an important part of a broader non-binary orientation, but if one wants to study non-binary gender identities, expressions, or experiences, a different kind of analysis altogether is needed.

[^2]: To expand: names reify fictions about how one's social position is derivative of real (or perceived) sex-related characteristics. That is, names are a way of gendering, of projecting social life onto something thought to be more natural and thus definitive. The somewhat strange locution that an individual is "gendered female" or "gendered male" is meant to capture the incoherence of the supposed "sex/gender" dichotomy and to convey that naming or classifying is always an active process, a process as strange as the social phenomena our name-based gender classification scheme is designed to study.
