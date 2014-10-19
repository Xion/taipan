"""
Tests for the test stage decorators: ``@setUp``, ``@tearDown``, etc.
"""
from __future__ import print_function

import os

from taipan._compat import StringIO
from taipan.collections import lists
from taipan.strings import is_string
from taipan.testing._unittest import TestCase, TestLoader, TextTestRunner

import taipan.testing as __unit__


SETUP_CLASS_TEXT = "SETUP_CLASS"
SETUP_TEXT = "SETUP"

TEST_TEXT = "TEST"

TEARDOWN_TEXT = "TEARDOWN"
TEARDOWN_CLASS_TEXT = "TEARDOWN_CLASS"


class _StageDecorators(TestCase):
    """Base class for test cases for test stage decorators."""
    #: Stream used to record test output
    test_output = StringIO()

    class TestCase(__unit__.TestCase):
        """Base class for Taipan test cases that we'll be running
        and checking the results of.
        """
        def test_print(self):
            self._print(TEST_TEXT)

        @classmethod
        def _print(cls, text):
            """Print text to a text output stream
            that can be easily asserted upon ater.
            """
            print(text, file=_StageDecorators.test_output)

    # Utility functions

    def _run_tests(self, testcase_class=None):
        """Runs the tests from specified TestCase class
        and returns their output.
        """
        # run the tests, suppressing all the output that'd go to stdout/stderr
        testcase_class = testcase_class or self.TestCase
        suite = TestLoader().loadTestsFromTestCase(testcase_class)
        TextTestRunner(stream=StringIO(), verbosity=0).run(suite)

        # capture the "real" test output that was written to our stream
        self.test_output.seek(0)
        result = self.test_output.read()

        # empty the stream to prepare for the next run
        self.test_output.seek(0)
        self.test_output.truncate()

        return result

    def _lines(self, *args):
        """Concatenates lines of text into a single string."""
        lines = lists.flatten([arg] if is_string(arg) else arg
                              for arg in args)
        result = os.linesep.join(lines)
        if result:
            result += os.linesep
        return result


# Tests for decorators applied in isolation

class SetUpClass(_StageDecorators):

    def test_setUpClass_one(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUpClass
            def print_setUpClass_text(cls):
                cls._print(SETUP_CLASS_TEXT)

        self.assertEquals(self._lines(SETUP_CLASS_TEXT, TEST_TEXT),
                          self._run_tests(TestCase))

    def test_setUpClass_many(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUpClass
            def one(cls):
                cls._print(SETUP_CLASS_TEXT + '1')
            @__unit__.setUpClass
            def two(cls):
                cls._print(SETUP_CLASS_TEXT + '2')
            @__unit__.setUpClass
            def three(cls):
                cls._print(SETUP_CLASS_TEXT + '3')

        setup_class_texts = [SETUP_CLASS_TEXT + str(i + 1) for i in range(3)]
        self.assertEquals(self._lines(setup_class_texts, TEST_TEXT),
                          self._run_tests(TestCase))

class SetUp(_StageDecorators):

    def test_setUp_one(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUp
            def print_setUp_text(self):
                self._print(SETUP_TEXT)

        self.assertEquals(self._lines(SETUP_TEXT, TEST_TEXT),
                          self._run_tests(TestCase))

    def test_setUp_many(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUp
            def one(self):
                self._print(SETUP_TEXT + '1')
            @__unit__.setUp
            def two(self):
                self._print(SETUP_TEXT + '2')
            @__unit__.setUp
            def three(self):
                self._print(SETUP_TEXT + '3')

        setup_texts = [SETUP_TEXT + str(i + 1) for i in range(3)]
        self.assertEquals(self._lines(setup_texts, TEST_TEXT),
                          self._run_tests(TestCase))


class TearDown(_StageDecorators):

    def test_tearDown_one(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.tearDown
            def print_tearDown_text(self):
                self._print(TEARDOWN_TEXT)

        self.assertEquals(self._lines(TEST_TEXT, TEARDOWN_TEXT),
                          self._run_tests(TestCase))

    def test_tearDown_many(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.tearDown
            def one(self):
                self._print(TEARDOWN_TEXT + '1')
            @__unit__.tearDown
            def two(self):
                self._print(TEARDOWN_TEXT + '2')
            @__unit__.tearDown
            def three(self):
                self._print(TEARDOWN_TEXT + '3')

        teardown_texts = [TEARDOWN_TEXT + str(i + 1) for i in range(3)]
        self.assertEquals(self._lines(TEST_TEXT, teardown_texts),
                          self._run_tests(TestCase))


class TearDownClass(_StageDecorators):

    def test_tearDownClass_one(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.tearDownClass
            def print_tearDownClass_text(cls):
                cls._print(TEARDOWN_CLASS_TEXT)

        self.assertEquals(self._lines(TEST_TEXT, TEARDOWN_CLASS_TEXT),
                          self._run_tests(TestCase))

    def test_tearDownClass_many(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.tearDownClass
            def one(cls):
                cls._print(TEARDOWN_CLASS_TEXT + '1')
            @__unit__.tearDownClass
            def two(cls):
                cls._print(TEARDOWN_CLASS_TEXT + '2')
            @__unit__.tearDownClass
            def three(cls):
                cls._print(TEARDOWN_CLASS_TEXT + '3')

        teardown_class_texts = [TEARDOWN_CLASS_TEXT + str(i + 1)
                                for i in range(3)]
        self.assertEquals(self._lines(TEST_TEXT,  teardown_class_texts),
                          self._run_tests(TestCase))


# Tests for couple different decorators used in conjuction

class SetUpBoth(_StageDecorators):

    def test_one_each(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUpClass
            def print_setUpClass_text(cls):
                cls._print(SETUP_CLASS_TEXT)
            @__unit__.setUp
            def print_setUp_text(self):
                self._print(SETUP_TEXT)

        self.assertEquals(self._lines(SETUP_CLASS_TEXT, SETUP_TEXT, TEST_TEXT),
                          self._run_tests(TestCase))

    def test_many__setUpClass(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUpClass
            def one(cls):
                cls._print(SETUP_CLASS_TEXT + '1')
            @__unit__.setUpClass
            def two(cls):
                cls._print(SETUP_CLASS_TEXT + '2')
            @__unit__.setUp  # in between, just to try to mess a bit
            def print_setUp_text(self):
                self._print(SETUP_TEXT)
            @__unit__.setUpClass
            def three(cls):
                cls._print(SETUP_CLASS_TEXT + '3')

        setup_class_texts = [SETUP_CLASS_TEXT + str(i + 1) for i in range(3)]
        self.assertEquals(
            self._lines(setup_class_texts, SETUP_TEXT, TEST_TEXT),
            self._run_tests(TestCase))

    def test_many__setUp(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUpClass
            def print_setUpClass_text(cls):
                cls._print(SETUP_CLASS_TEXT)
            @__unit__.setUp
            def one(self):
                self._print(SETUP_TEXT + '1')
            @__unit__.setUp
            def two(self):
                self._print(SETUP_TEXT + '2')
            @__unit__.setUp
            def three(self):
                self._print(SETUP_TEXT + '3')

        setup_texts = [SETUP_TEXT + str(i + 1) for i in range(3)]
        self.assertEquals(
            self._lines(SETUP_CLASS_TEXT, setup_texts, TEST_TEXT),
            self._run_tests(TestCase))


class SetUpAndTearDown(_StageDecorators):

    def test_one_each(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUp
            def print_setUp_text(self):
                self._print(SETUP_TEXT)
            @__unit__.tearDown
            def print_tearDown_text(self):
                self._print(TEARDOWN_TEXT)

        self.assertEquals(self._lines(SETUP_TEXT, TEST_TEXT, TEARDOWN_TEXT),
                          self._run_tests(TestCase))

    def test_many__setUp(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.tearDown  # teardown first, because why not?
            def print_tearDown_text(self):
                self._print(TEARDOWN_TEXT)
            @__unit__.setUp
            def one(self):
                self._print(SETUP_TEXT + '1')
            @__unit__.setUp
            def two(self):
                self._print(SETUP_TEXT + '2')
            @__unit__.setUp
            def three(self):
                self._print(SETUP_TEXT + '3')

        setup_texts = [SETUP_TEXT + str(i + 1) for i in range(3)]
        self.assertEquals(
            self._lines(setup_texts, TEST_TEXT, TEARDOWN_TEXT),
            self._run_tests(TestCase))

    def test_many__tearDown(self):
        class TestCase(_StageDecorators.TestCase):
            @__unit__.setUp
            def print_setUp_text(self):
                self._print(SETUP_TEXT)
            @__unit__.tearDown
            def one(self):
                self._print(TEARDOWN_TEXT + '1')
            @__unit__.tearDown
            def two(self):
                self._print(TEARDOWN_TEXT + '2')
            @__unit__.tearDown
            def three(self):
                self._print(TEARDOWN_TEXT + '3')

        teardown_texts = [TEARDOWN_TEXT + str(i + 1) for i in range(3)]
        self.assertEquals(self._lines(SETUP_TEXT, TEST_TEXT, teardown_texts),
                          self._run_tests(TestCase))
