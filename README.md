# tokensjar

`tokensjar` is a pure Python module dedicated to generate, manipulate and interpret expressions following environment variables creation rules. This module is really useful if you need to develop a tool that can prepare the session environment variables for a specific usage.

## Installation

`tokensjar` is available on [PyPi](https://pypi.org/project/tokensjar)

```
python -m pip install tokensjar
```

## Concept

A **token** must be considered as a simple variable where we can attach one value (a `raw` value) or multiple values (`append` or `prepend`). The main goal is to manipulate tokens with the same strategies than environment variables. 

## Examples

### Add values to the tokens

There are three methods to prepare the `TokensJar`:

- `add_raw_value`: Define the value for the token. Only the last value added will be kept.
- `add_prepend_value`: Allow to prepend a string to the token value. Each value will be separated by the OS standard separator (':' on Unix, ';' on Windows).
- `add_append_value`: Allow to append a string to the token value. Each value will be separated by the OS standard separator (':' on Unix, ';' on Windows).

```python
import os
from tokensjar import TokensJar


jar = TokensJar(init_tokens={
    'PATH': os.environ['PATH'],
    'LD_LIBRARY_PATH': os.environ['LD_LIBRARY_PATH']})

jar.add_raw_value('HELLO', 'Hello World!')
print(jar.tokens_interpreted['HELLO'])
# Output: HelloWorld!

jar.add_prepend_value('PATH', 'MyPrependPath')
print(jar.tokens_interpreted['PATH'])
# Output: MyPrependPath:[...environment PATHs...]

jar.add_append_value('LD_LIBRARY_PATH', 'MyAppendPath')
print(jar.tokens_interpreted['LD_LIBRARY_PATH'])
# Output: [...environment LD_LIBRARY_PATHs...]:MyAppendPath
```

### Interpret expressions

The strength of the `TokensJar` is the interpretation engine behind. You can add values that refers to other tokens as much as you want. An `interpret` method and `tokens_interpreted` property are exposed to compute/retrieve values.

```python
from tokensjar import TokensJar


jar = TokensJar()
jar.add_raw_value('T1', 'Token1')
jar.add_raw_value('T2', 'Token2')
jar.add_raw_value('T12', '$(T1)/$(T2)') # Note the usage of the syntax $()
jar.add_raw_value('HELLO': 'Hello: ')

print(jar.tokens_interpreted['T12'])
# Output: Token1/Token2

result = jar.interpret('Joe said: $(HELLO) $(T12)')
# Output: Joe said: Hello: Token1/Token2
```

 Take care to not introduce cyclic dependencies between tokens! The topological sort is handled by Eric V. Smith `toposort` Python package ([Link](https://pypi.org/project/toposort)).

 ```python
from tokensjar import TokensJar


jar = TokensJar()
jar.add_raw_value('T1', '$(T2)')
jar.add_raw_value('T2', '$(T1)')

jar.interpret('$(T1)')
# Raise toposort EXCEPTION: Cyclic dependency detected!
 ```

 # Contributions

 Feel free to open feature requests, issues or pull requests. Your help and vision are welcome!

 ## Tests

 Tests are written following `unittest` framework. Some dependencies are needed (`test-requirements.txt`). If you want to run tests, enter the following command at the root level of the package:

 ```
 python -m unittest discover
 ``` 

 ## Build the project

To perform the build, you need to install `dist-requirements.txt` list of packages, then run the following command. All the files will be located in `dist` directory.

```
python -m build
```

## Upload the project

The project can be uploaded using `twine` (listed in `dist-requirements.txt`) by running the following command:

```
python -m twine upload dist/*
```