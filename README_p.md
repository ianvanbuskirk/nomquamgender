# nomquamgender (nqg)

A simple package containing data and a few functions to support name-based gender classification in scientific research. See [github](https://github.com/ianvanbuskirk/nomquamgender) for details and examples.

---

## Install

```console
pip install nomquamgender
```

---

## Annotate Names

```python
import nomquamgender as nqg
```

```python
model = nqg.NBGC()
model.annotate(['András Schiff', 'Mitsuko Uchida', 'Jean Rondeau'], as_df=True)
```

|    | given          | used    |   sources |   counts |   p(gf) |
|---:|:---------------|:--------|----------:|---------:|--------:|
|  0 | András Schiff  | andras  |        24 |    13010 |   0.001 |
|  1 | Mitsuko Uchida | mitsuko |        14 |      925 |   0.981 |
|  2 | Jean Rondeau   | jean    |        31 |  2525377 |   0.477 |
