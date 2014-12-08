import os
import yaml

# path to plugin folder
PLUGIN_PATH = 'plugins'


def getSpecification(lang, testLib, arithLib):
    """
    Return a complete specification as a tuple of dictionaries.

    Arguments:
    lang -- the name of the language
    testLib -- the name of the test library
    arithLib -- the name of the interval library
    """
    langDict = getLanguageSpecification(lang)
    testLibDict = getTestLibSpecification(lang, testLib)
    arithLibDict = getArithLibSpecification(lang, arithLib)
    return (langDict, testLibDict, arithLibDict)


def getCbPath(lang):
    """
    Return the path to the callbacks.py module in python notation.

    For the language 'cpp' the function return 'plugins.cpp.callbacks.py'.
    Return None if no such module exists.

    Arguments:
    lang -- the name of the language
    """
    path = '/'.join([PLUGIN_PATH, lang, 'callbacks.py'])
    if not exists(path):
        return None
    modulePath = path.replace('/', '.')
    modulePathStrippedExt = '.'.join(modulePath.split('.')[:-1])
    return modulePathStrippedExt


def getLanguageSpecification(lang):
    """
    Return a dictionary which contains the specification of a language.

    Specifically, return the key-value pairs defined in the 'lang.yaml' file as
    a dictionary, i.e. for the language cpp return the contents of
    'plugins/cpp/lang.yaml'.
    Raise an IOError if the 'lang.yaml' file does not exist.

    Arguments:
    lang -- the name of the language
    """
    dirPath = '/'.join([PLUGIN_PATH, lang])
    if not exists(dirPath):
        raise IOError(dirPath + ' does not exist.')
    filePath = '/'.join([dirPath, 'lang.yaml'])
    if not exists(filePath):
        raise IOError('lang.yaml file not found for language ' + lang)
    return yaml.load(open(filePath).read().strip())


def getTestLibSpecification(lang, testLib):
    """
    Return a dictionary which contains the specification of the test library.

    Specifically, return the key-value pairs defined in the 'test.yaml' file as
    a dictionary, i.e. for the language cpp and the test library BOOST return
    the contents of 'plugins/cpp/test/BOOST/test.yaml'.
    Raise an IOError if the 'test.yaml' file does not exist.

    Arguments:
    lang -- the name of the language
    testLib -- the name of the test library
    """
    dirPath = '/'.join([PLUGIN_PATH, lang, 'test', testLib])
    if not exists(dirPath):
        raise IOError(lang + ' dir not found.')
    filePath = '/'.join([dirPath, 'test.yaml'])
    if not exists(filePath):
        raise IOError('test.yaml file not found for language ' + lang +
                      ', testlib ' + testLib)
    return yaml.load(open(filePath).read().strip())


def getArithLibSpecification(lang, arithLib):
    """
    Return a dictionary with the specification of the interval library.

    Specifically, return the key-value pairs defined in the 'arith.yaml' file
    as a dictionary, i.e. for the language cüü and the interval library lib1
    return the contents of 'plugins/cpp/arith/lib1/arith.yaml'.
    Raise an IOError if the file is not found.

    Arguments:
    lang -- the name of the language
    arithLib -- the name of the interval library
    """
    dirPath = '/'.join([PLUGIN_PATH, lang, 'arith', arithLib])
    if not exists(dirPath):
        raise IOError(lang + ' dir not found.')
    filePath = '/'.join([dirPath, 'arith.yaml'])
    if not exists(filePath):
        raise IOError('test.yaml file not found for language ' + lang +
                      ', arithlib ' + arithLib)
    return yaml.load(open(filePath).read().strip())


def getSpecList():
    """
    Return a list of all valid specifications.

    Specifically, return a list of tuples (language, testLib, intervalLib)
    where the elements of the tuples represent their names (rather than their
    content).
    """
    specs = []

    # assemble all languages
    langs = getSubLibs(PLUGIN_PATH)

    for lang in langs:
        arithPath = PLUGIN_PATH + "/" + lang + "/arith/"
        ariths = getSubLibs(arithPath)

        testPath = PLUGIN_PATH + "/" + lang + "/test/"
        tests = getSubLibs(testPath)

        for test in tests:
            for arith in ariths:
                specs += [(lang, test, arith)]
    return specs


def getSpecListByLanguageAndTestLibrary(lang, testLib):
    """
    Return a list of specifications by the language and test library names.

    Specifically, return a list of tuples (language, testLib, intervalLib)
    where the language and the test library are defined by the parameters and
    the interval library is variable.

    Arguments:
    lang -- the name of the language
    testLib -- the name of the test library
    """
    specs = []

    arithPath = PLUGIN_PATH + "/" + lang + "/arith/"
    ariths = getSubLibs(arithPath)

    for arith in ariths:
        print(arith)
        specs += [(lang, testLib, arith)]

    return specs


def getSpecListByLanguageAndArithmeticLibrary(lang, arithLib):
    """
    Return a list of specifications by language and interval library names.

    Specifically, return a list of tuples (language, testLib, intervalLib)
    where the language and the interval library are defined by the parameters
    and the test library is variable.

    Arguments:
    lang -- the name of the language
    arithLib -- the name of the interval library
    """
    specs = []

    testPath = PLUGIN_PATH + "/" + lang + "/test/"
    tests = getSubLibs(testPath)

    for test in tests:
        specs += [(lang, test, arithLib)]

    return specs


def getSpecListByLanguage(lang):
    """
    Return a list of specifications by the language.

    Specifically, return a list of tuples (language, testLib, intervalLib)
    where the language is defined by the parameter and the test library
    and the interval library are variable.

    Arguments:
    lang -- the name of the language
    """
    specs = []

    arithPath = PLUGIN_PATH + "/" + lang + "/arith/"
    ariths = getSubLibs(arithPath)

    testPath = PLUGIN_PATH + "/" + lang + "/test/"
    tests = getSubLibs(testPath)

    for test in tests:
        for arith in ariths:
            specs += [(lang, test, arith)]
    return specs


def getSubDirs(path):
    """
    Return a list of all immediate subdirectories of a path.

    Raise an IOError if path does not represent a directory.

    Arguments:
    path -- path to the directory
    """
    if not os.path.isdir(path):
        raise IOError(path + ' is not a directory')
    return [name for name in os.listdir(path)
            if os.path.isdir(os.path.join(path, name))]


def getSubLibs(path):
    """
    Return a list of immediate subdirectories without the __pycache__ folder.

    Raise an IOError if path does not exist.

    Arguments:
    path -- path to the directory
    """
    return list(filter(lambda x: x != '__pycache__', getSubDirs(path)))


def exists(path):
    """
    Checks if the absolute value of path is a valid directory.

    Arguments:
    path -- path to the directory
    """
    return os.path.exists(os.path.abspath(path))
