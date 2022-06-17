# nomquamgender

A simple package containing data and a few functions to support name-based gender-classification in scientific research.

Conceptually, this method of classification does not reflect gender _identity_, _expression_ or a _perception_ of either but a structural dimension of gender: that is, how gender is likely to have structured an individual's life. Rather than fine-grained, anthropological accounts uniquely crafted to glimpse this gendering process our method provides only the possibility of tapping into a single, narrow stream of relatively inert data exhaust: names. As such, the classifications we offer are limited[^1]. How gender structures "social space" ([Bourdieu, 1989](https://www.jstor.org/stable/202060?seq=1)) will forever elude our attempts to "reduce human group life to variables and their relations" ([Blumer, 1956](https://www.jstor.org/stable/2088418?seq=1)). Thus, we name what we capture here nomquamgender: a nonsense name made of the French _nom_, Latin _quam_, and English _gender_. Fully translated to English as "name rather than gender", this signifies that what our method can offer is a reflection of the gendering process, a shadow of the way gender structures social space, but only that, and nothing more.

Computationally, this package provides access to name-gender association data that can be used to classify individuals into gendered groups. These gendered groups are best thought of as individuals likely to have been most typically gendered female and individuals likely to have been most typically gendered male. When discussing these classifications in practice one ought to use this language of _gendered female_ and _gendered male_ rather than more traditional sex/gender language[^2]. Classifications themselves are not made by our package, but rather the probability that a name belongs to an individual gendered female, p(gf), is provided. This method is comparable in performance to the most reliable paid name-based gender-classification services ([Van buskirk, 2022](https://www.overleaf.com/project/60ba2dd89d76914725831610)).

## Installation

```
pip install nomquamgender
```

## Usage

### Annotate a single name

```python
import nomquamgender as nqg
nqg.annotate('clara')
```

|    | given   | used   |   sources |   counts |   p(gf) |
|---:|:--------|:-------|----------:|---------:|--------:|
|  0 | clara   | clara  |        31 |   492337 |   0.992 |
---

### Annotate a list of names

```python
nqg.annotate(['András Schiff', 'Mitsuko Uchida', 'Jean Rondeau'])
```

|    | given          | used    |   sources |   counts |   p(gf) |
|---:|:---------------|:--------|----------:|---------:|--------:|
|  0 | András Schiff  | andras  |        24 |    13010 |   0.001 |
|  1 | Mitsuko Uchida | mitsuko |        14 |      925 |   0.981 |
|  2 | Jean Rondeau   | jean    |        31 |  2525377 |   0.477 |
---

### Retrieve and use name-gender data

```python
import pandas as pd

name_data = nqg.dump()

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

### Use alternative name-gender data

```python
nqg.annotate(['nomquam','jean'])
```

|    | given   | used    |   sources |   counts |   p(gf) |
|---:|:--------|:--------|----------:|---------:|--------:|
|  0 | nomquam | nomquam |         0 |        0 | nan     |
|  1 | jean    | jean    |        31 |  2525377 |   0.477 |

```python
# combine and replace
reference = dict(name_data, **alternative)
nqg.annotate(['nomquam', 'jean'], reference)
```

|    | given   | used    |   sources |   counts |   p(gf) |
|---:|:--------|:--------|----------:|---------:|--------:|
|  0 | nomquam | nomquam |         3 |        1 |     0.5 |
|  1 | jean    | jean    |         3 |     1000 |     1   |

```python
# combine and average
reference = {**name_data}
for n, v in alternative.items():
    d = name_data[n] if n in name_data.keys() else [0,0,-1]
    s = d[0] + v[0]
    reference[n] = [s, d[1] + v[1], (d[0]/s)*d[2] + (v[0]/s)*v[2]]
    
nqg.annotate(['nomquam','jean'],reference)
```

|    | given   | used    |   sources |   counts |    p(gf) |
|---:|:--------|:--------|----------:|---------:|---------:|
|  0 | nomquam | nomquam |         3 |        1 | 0.5      |
|  1 | jean    | jean    |        34 |  2526377 | 0.523147 |

[^1]: An important aside: The core limitation of using names to reflect the dimension of gender we are interested in is not that classifications are constrained by a "gender binary", but that how gender structures our lives is complex, heterogeneous, variable across time, and interacts with other social forces, whether or not this structuring is best thought of in binary terms. It can be appealing to think that using name-gender associations rather than binary classifications somehow sidesteps an important issue and in some way captures that gender is "non-binary" (e.g. rather than act as if all Taylor's are gendered male, one works with the probability that someone with the name Taylor is gendered male: 0.64). While these continuous associations can be quantitatively useful, they do not offer a conceptual escape hatch to those troubled by binary classifications. Uncertainty does not a non-binary variable make, and in no way do the probabilities we estimate more meaningfully map onto identities, expressions, or lived experiences than their derivative classifications. It's instructive to think of how intentionally taking on a weakly gendered name, such as taylor, leslie, or kim, would (potentially) undermine the gender binary: in our current climate one would not be signaling something non-binary but rather partially obfuscate whatever gendered information names tend to convey. Thoughtfully using binary classifications in scientific research to study the structural dimension of gender need not conflict with our understanding and appreciation of gender in other contexts. As such, name-based gender-classification can be an important part of a broader non-binary orientation, but if one wants to study non-binary gender identities, expressions, or experiences, a different kind of analysis altogether is needed.

[^2]: To expand: names reify fictions about how one's social position is derivative of real (or perceived) sex-related characteristics. That is, names are a way of gendering, of projecting social life onto something thought to be more natural and thus definitive. The somewhat strange locution that an individual is "gendered female" or "gendered male" is meant to capture the incoherence of the supposed "sex/gender" dichotomy and to convey that naming or classifying is always an active process, a process as strange as the social phenomena our name-based gender-classification scheme is designed to study.
