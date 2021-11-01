import os
import re
from collections import defaultdict


RX_TOKEN_PATTERN = re.compile(r'\$\(([^\)]+)\)')


class TokensJarError(Exception):
    pass


class TokensJarBadInitTokensError(TokensJarError):
    def __init__(self):
        super().__init__('"init_tokens" argument must be a dictionary.')


class TokensJar:
    def __init__(self, init_tokens: dict={}):
        if not isinstance(init_tokens, dict):
            raise TokensJarBadInitTokensError()
        self.__init_tokens = init_tokens
        self.__jars = defaultdict(lambda: defaultdict(list))

    def __add_value(self, jar: str, name: str, value: str):
        self.__jars[jar][name].append(value)

    def __add__(self, other):
        for j, jar in other.__jars.items():
            for v, values in jar.items():
                self.__jars[j][v] += values
        return self

    def add_raw_value(self, name: str, value: str):
        """Add a raw value (a pure value without append or prepend strategy) for a token.

        Args:
            name (str): The name of the token.
            value (str): The new value for the token.
        """
        self.__add_value('raw', name, value)

    def add_append_value(self, name: str, value: str):
        """Append a value to the token selected. On interpretation, all the values will be
        separated by the OS standard separator (':' on Unix, ';' on Windows).

        Args:
            name (str): The name of the token.
            value (str): The value to append to the token.
        """
        self.__add_value('append', name, value)

    def add_prepend_value(self, name: str, value: str):
        """Prepend a value to the token selected. On interpretation, all the values will be
        separated by the OS standard separator (':' on Unix, ';' on Windows)

        Args:
            name (str): The name of the token.
            value (str): The value to prepend to the token.
        """
        self.__add_value('prepend', name, value)

    def __get_tokens(self):
        tokens = {}
        # FILL TOKENS DICT
        # Raw
        for t, t_values in self.__jars['raw'].items():
            tokens[t] = list(reversed(t_values))[0]
        # Prepend
        for t, t_values in self.__jars['prepend'].items():
            value = list(reversed(t_values))
            if t in self.__init_tokens:
                value += self.__init_tokens[t].split(os.pathsep)
            tokens[t] = os.pathsep.join(value)
        # Append
        for t, t_values in self.__jars['append'].items():
            value = t_values
            if t in self.__init_tokens:
                value = self.__init_tokens[t].split(os.pathsep) + value
            tokens[t] = os.pathsep.join(value)
        return tokens

    def interpret(self, expression: str) -> str:
        """Interpret the expression given in parameter."""
        tokens = self.__get_tokens()
        
        # Create dependency graph
        nodes = {n: set() for n in tokens.keys()}
        for t, value in tokens.items():
            dep_tokens = RX_TOKEN_PATTERN.findall(value)
            for token in dep_tokens:
                nodes[t].add(token)
        # Sort nodes
        from toposort import toposort_flatten
        tokens_sorted = reversed(toposort_flatten(nodes))
        for ts in tokens_sorted:
            expression = expression.replace(f'$({ts})', tokens[ts])
        return expression

    @property
    def tokens_interpreted(self) -> dict:
        """The dictionary of all tokens interpreted."""
        tokens = self.__get_tokens()
        for t, value in tokens.items():
            tokens[t] = self.interpret(value)
        return tokens
