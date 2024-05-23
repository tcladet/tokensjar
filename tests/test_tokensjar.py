import unittest
import os
from ddt import ddt, data, unpack
from src.tokensjar.tokensjar import TokensJar, TokensJarBadInitTokensError, TokensJarTokenNotDeclaredError


@ddt
class RawJarTestCase(unittest.TestCase):
    def setUp(self):
        self.jar = TokensJar()
        self.jar.add_raw_value('TEST', 'TestValue')
        self.jar.add_raw_value('ADIOS', 'Adios')
        self.jar.add_raw_value('SALUT', '$(TEST)/$(ADIOS)')

    @data(
        ('$(TEST)', 'TestValue'),
        ('Coucou$(TEST)Hello', 'CoucouTestValueHello'),
        ('Coucou$(SALUT)Hello', 'CoucouTestValue/AdiosHello'))
    @unpack
    def test_interpret(self, challenge, expected):
        result = self.jar.interpret(challenge)
        self.assertEqual(expected, result)

    def test_tokens_interpreted(self):
        expected = {
            'TEST': 'TestValue',
            'ADIOS': 'Adios',
            'SALUT': 'TestValue/Adios'
        }
        result = self.jar.tokens_interpreted
        self.assertEqual(expected, result)


class PrependJarTestCase(unittest.TestCase):
    def setUp(self):
        self.jar = TokensJar(init_tokens={'TOKEN': 'PreValue'})
        self.jar.add_prepend_value('TOKEN', 'Yolo1')
        self.jar.add_prepend_value('TOKEN', 'Yolo2')

    def test_tokens_interpreted(self):
        expected = {
            'TOKEN': 'Yolo2{sep}Yolo1{sep}PreValue'.format(sep=os.pathsep),
        }
        result = self.jar.tokens_interpreted
        self.assertEqual(expected, result)


class AppendJarTestCase(unittest.TestCase):
    def setUp(self):
        self.jar = TokensJar(init_tokens={'TOKEN': 'PreValue'})
        self.jar.add_append_value('TOKEN', 'Yolo1')
        self.jar.add_append_value('TOKEN', 'Yolo2')

    def test_tokens_interpreted(self):
        expected = {
            'TOKEN': 'PreValue{sep}Yolo1{sep}Yolo2'.format(sep=os.pathsep),
        }
        result = self.jar.tokens_interpreted
        self.assertEqual(expected, result)


class TestJarOperatorsTestCase(unittest.TestCase):
    def setUp(self):
        self.baseJar = TokensJar()
        self.baseJar.add_raw_value('RAW', 'MyRawValue')
        self.baseJar.add_append_value('APPEND', 'MyAppendValue')
        self.baseJar.add_prepend_value('PREPEND', 'MyPrependValue')

    def test_merge_raw(self):
        jar = TokensJar()
        jar.add_raw_value('RAW', 'MyNewRawValue')
        self.baseJar += jar
        expected = 'MyNewRawValue'
        result = self.baseJar.tokens_interpreted['RAW']
        self.assertEqual(expected, result)

    def test_merge_append(self):
        jar = TokensJar()
        jar.add_append_value('APPEND', 'MyNewAppendValue1')
        jar.add_append_value('APPEND', 'MyNewAppendValue2')
        self.baseJar += jar
        expected = 'MyAppendValue{sep}MyNewAppendValue1{sep}MyNewAppendValue2'.format(sep=os.pathsep)
        result = self.baseJar.tokens_interpreted['APPEND']
        self.assertEqual(expected, result)

    def test_merge_prepend(self):
        jar = TokensJar()
        jar.add_prepend_value('PREPEND', 'MyNewPrependValue1')
        jar.add_prepend_value('PREPEND', 'MyNewPrependValue2')
        self.baseJar += jar
        expected = 'MyNewPrependValue2{sep}MyNewPrependValue1{sep}MyPrependValue'.format(sep=os.pathsep)
        result = self.baseJar.tokens_interpreted['PREPEND']
        self.assertEqual(expected, result)


class TestMisusageTestCase(unittest.TestCase):
    def test_bad_init_tokens(self):
        with self.assertRaises(TokensJarBadInitTokensError):
            TokensJar(init_tokens="pouet")

    def test_token_not_declared_strict(self):
        jar = TokensJar()
        jar.add_raw_value('X', '$(TOKEN)_coucou')
        with self.assertRaises(TokensJarTokenNotDeclaredError):
            jar.interpret('$(X)')

    def test_token_not_declared_relaxed(self):
        jar = TokensJar()
        jar.add_raw_value('X', '$(TOKEN)_coucou')
        challenge = jar.interpret('$(X)', strict=False)
        self.assertEqual('$(TOKEN)_coucou', challenge)