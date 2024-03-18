

`ipynb_tools` is easy to reload module of .py or .ipynb.

Firstly, import it.

```python
from ipynb_tools import ipynb_importer

# if you have a module named "abc.ipynb" or "abc.py"
import abc
```



You can reload module once you rewrite it.

```python
abc = ipynb_import.reload_module(abc)
```

