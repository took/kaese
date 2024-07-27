# Use "coverage run -m unittest discover" instead!
# Use "coverage report" to get coverage report!

import doctest
import unittest

# DocTests
# Import the modules that contain doctests
import kaese.ai.stupid_ai
import kaese.ai.random_ai
import kaese.gameboard.box
from tests.test_savegames import TestSavegames

# Create a test suite and add the modules
test_suite = doctest.DocTestSuite(kaese.ai.stupid_ai)
test_suite.addTest(doctest.DocTestSuite(kaese.ai.random_ai))
test_suite.addTest(doctest.DocTestSuite(kaese.gameboard.box))

# Create a test runner and run the suite
test_runner = unittest.TextTestRunner()
test_runner.run(test_suite)

# UnitTests
# Import your test modules
from test_ais import TestAIs
from test_stupid_ai import TestStupidAI
from test_box import TestBox

# Create a test suite
test_suite = unittest.TestSuite()

# Add the test cases to the suite
test_suite.addTest(unittest.makeSuite(TestAIs))
test_suite.addTest(unittest.makeSuite(TestStupidAI))
test_suite.addTest(unittest.makeSuite(TestBox))
test_suite.addTest(unittest.makeSuite(TestSavegames))

# Create a test runner and run the suite
test_runner = unittest.TextTestRunner()
test_runner.run(test_suite)
