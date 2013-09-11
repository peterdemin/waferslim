import unittest
from . import execution


class ConventionsTestCase(unittest.TestCase):
    def test_lower_camel_case(self):
        self.assertEqual(
            execution.to_lower_camel_case('pythonic_case'),
            'pythonicCase'
        )
        self.assertEqual(
            execution.to_lower_camel_case('CamelCase'),
            'camelCase'
        )
        self.assertEqual(
            execution.to_lower_camel_case('camelCase'),
            'camelCase'
        )

    def test_upper_camel_case(self):
        self.assertEqual(
            execution.to_upper_camel_case('pythonic_case'),
            'PythonicCase'
        )
        self.assertEqual(
            execution.to_upper_camel_case('CamelCase'),
            'CamelCase'
        )
        self.assertEqual(
            execution.to_upper_camel_case('camelCase'),
            'CamelCase'
        )

    def test_pythonic_case(self):
        self.assertEqual(
            execution.to_pythonic('pythonicCase'),
            'pythonic_case'
        )
        self.assertEqual(
            execution.to_pythonic('CamelCase'),
            'camel_case'
        )
        self.assertEqual(
            execution.to_pythonic('camelCase'),
            'camel_case'
        )

    def test_aliases(self):
        self.assertEqual(
            execution.ExecutionContext.get_aliases([
                'pythonic_case',
                'CamelCase',
            ]),
            {
                'pythonic_case': 'pythonic_case',
                'pythonicCase': 'pythonic_case',
                'PythonicCase': 'pythonic_case',
                'CamelCase': 'CamelCase',
                'camelCase': 'CamelCase',
            }
        )


if __name__ == '__main__':
    unittest.main()
