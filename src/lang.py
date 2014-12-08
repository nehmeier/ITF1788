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
