#
#                              ITF1788
#
#   Interval Test Framework for IEEE 1788 Standard for Interval Arithmetic
#
#
#   Copyright 2014
#
#   Marco Nehmeier (nehmeier@informatik.uni-wuerzburg.de)
#   Maximilian Kiesner (maximilian.kiesner@stud-mail.uni-wuerzburg.de)
#
#   Department of Computer Science
#   University of Wuerzburg, Germany
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

class OutputSpecification(object):

    """
    Wraps a (lang, testLib, arithLib) specification as an object.

    It contains the values of a lang.yaml, a test.yaml and an arith.yaml file
    as attributes, i.e. attributes with the name of the key in the yaml file
    prefixed with 'lang_', 'test_' or 'arith_' depending on the file.
    """

    def __init__(self, langSpec, testSpec, arithSpec):
        """
        Initialize an OutputSpecification.

        Arguments:
        langSpec -- specification dictionary of the language
        testSpec -- specficiation dictionary of the test library
        arithSpec -- specification dictionary of the interval library
        """
        # set the entries of the dictionaries as attributes with corresponding
        # prefix
        for el in langSpec:
            setattr(self, 'lang_' + el, langSpec[el])
        for el in testSpec:
            setattr(self, 'test_' + el, testSpec[el])
        for el in arithSpec:
            setattr(self, 'arith_' + el, arithSpec[el])
