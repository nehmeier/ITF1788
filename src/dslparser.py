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

'''Lexer and Parser. Process the DSL test files and build an AST'''

import ply.lex as lex
from ply.lex import TOKEN
import ply.yacc as yacc
from testAST import *

#
# Lexer
#

# Defines language keywords.
# If an input token matches ID and the token is defined as a key,
# the token type will be assigned to the key's value.
reserved = {
    'testcase': 'TESTCASE',

    'trv': 'TRV',
    'def': 'DEF',
    'dac': 'DAC',
    'com': 'COM',
    'ill': 'ILL',

    'true': 'TRUE',
    'false': 'FALSE',

    "bothEmpty": "BOTHEMPTY",
    "firstEmpty": "FIRSTEMPTY",
    "secondEmpty": "SECONDEMPTY",
    "before": "BEFORE",
    "meets": "MEETS",
    "overlaps": "OVERLAPS",
    "starts": "STARTS",
    "containedBy": "CONTAINEDBY",
    "finishes": "FINISHES",
    "equal": "EQUAL",
    "finishedBy": "FINISHEDBY",
    "contains": "CONTAINS",
    "startedBy": "STARTEDBY",
    "overlappedBy": "OVERLAPPEDBY",
    "metBy": "METBY",
    "after": "AFTER"
}

#
# Every character defines a token.
# The parser may use these tokens as 'TOKEN', i.e. '{' or ';'
#
literals = "{};=<=_[].,"

#
# Multi character tokens
#
tokens = [
    "INT",
    "FLOAT",
    "STRING",
    "INF",
    "NAI",
    "EMPTY",
    "ENTIRE",
    "ID",
    "BLOCK_COMMENT",
    "LINE_COMMENT"
] + list(reserved.values())


#
# Define regexes for the symbols of the C99 'Integer constants' grammar,
# see www.open-std.org/jtc1/sc22/wg14/www/docs/n1124.pdf chapter 6.4.4
#
# They are used to build a regex for integer values -- they are split
# into multiple regexes to increase legibility.
#

sign = r"[+-]"

hexadecimalDigit = r"[0-9a-fA-F]"
hexadecimalPrefix = r"(0x|0X)"
hexadecimalConstant = hexadecimalPrefix + r"(" + hexadecimalDigit + r")+"

# Octal representation is currently not supported
#
# octalDigit = r"[0-7]"
# octalConstant = r"0(" + octalDigit + r")*"

nonZeroDigit = r"[1-9]"
digit = r"[0-9]"
decimalConstant = nonZeroDigit + r"(" + digit + r")*"

unsignedSuffix = r"[Uu]"
longSuffix = r"[Ll]"
longLongSuffix = r"((LL) | (ll))"
integerSuffix = r"(" + unsignedSuffix + longSuffix + r"?|" + \
    unsignedSuffix + longLongSuffix + r"|" +\
    longLongSuffix + unsignedSuffix + r"?|" + \
    longSuffix + unsignedSuffix + r"?)"

integerConstant = (sign + r"?(" + hexadecimalConstant + integerSuffix + r"?|" + 
    r"0" + integerSuffix + r"?|" + # octalConstant + integerSuffix + r"?|" + 
    decimalConstant + integerSuffix + r"?)" )


#
# Define regexes for the symbols of the C99 'Floating constants' grammar,
# see www.open-std.org/jtc1/sc22/wg14/www/docs/n1124.pdf chapter 6.4.4
#
# They are used to build a regex for floating point values -- they are split
# into multiple regexes to increase the legibility of this file only.
#

floatingSuffix = r"[FLfl]"

hexadecimalDigitSequence = r"(" + hexadecimalDigit + r"(" + hexadecimalDigit + \
    r")*)"
hexadecimalFractionalConstant = r"(" + hexadecimalDigitSequence + r"?\." + hexadecimalDigitSequence + \
                                r"|" + hexadecimalDigitSequence + r"\.)"

digitSequence = r"(" + digit + r"(" + digit + r")*)"

fractionalConstant = r"(" + digitSequence + r"?\." + digitSequence +\
                     r"|" + digitSequence + r"\.)"

binaryExponentPart = r"([pP]" + sign + r"?" + digitSequence + r")"
exponentPart = r"([eE]" + sign + r"?" + digitSequence + r")"

hexadecimalFloatingConstant = r"(" + hexadecimalPrefix + r"(" + \
    hexadecimalFractionalConstant + r"|" + hexadecimalDigitSequence + r")" + \
    binaryExponentPart + floatingSuffix + r"?)"

decimalFloatingConstant = r"((" + fractionalConstant + exponentPart + r"?" + \
    floatingSuffix + r"?)|(" + digitSequence + exponentPart + floatingSuffix + \
    r"?))"

floatingConstant = sign + r"?(" + hexadecimalFloatingConstant + r"|" + \
    decimalFloatingConstant + r")"

# other token regexes
ident = r"[a-zA-Z][a-zA-Z0-9_]*"
string = r'"([^\\\n]|(\\(.|\n)))*?\"'
# infinity may be float or double
inf = sign + r"?inf" + floatingSuffix + r"?"

# special intervals
nai = r"nai" + floatingSuffix + r"?"
empty = r"empty" + floatingSuffix + r"?"
entire = r"entire" + floatingSuffix + r"?"


#
# Map the regexes to the tokens
#
@TOKEN(floatingConstant)
def t_FLOAT(t):
    """Return the parsed float value."""
    return t


@TOKEN(integerConstant)
def t_INT(t):
    """Return the parsed int value."""
    return t


@TOKEN(string)
def t_STRING(t):
    """Return the parsed string value."""
    return t


@TOKEN(inf)
def t_INF(t):
    """Return the parsed infinity value."""
    return t

@TOKEN(nai)
def t_NAI(t):
    return t

@TOKEN(empty)
def t_EMPTY(t):
    return t

@TOKEN(entire)
def t_ENTIRE(t):
    return t


@TOKEN(ident)
def t_ID(t):
    """Check the type of the identifier and return the value of the type."""
    t.type = reserved.get(t.value, 'ID')
    return t


def t_BLOCK_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    return t


def t_LINE_COMMENT(t):
    r'//.*'
    return t


def t_IGNORED_BLOCK_COMMENT(t):
    r'\#\*(.|\n)*?\*\#'
    t.lexer.lineno += t.value.count('\n')
    pass


def t_IGNORED_LINE_COMMENT(t):
    r'\#.*'
    pass


#
# Special tokens
#

# ignore whitespace
t_ignore = " \t"


#
# ignore newlines but increment the lexers line count
#
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# error handling for an unknown token
def t_error(t):
    """Skip invalid tokens and print an error message."""
    print("Illegal character '%s' in line %d" % (t.value[0], t.lexer.lineno))
    t.lexer.skip(1)


# parse the input
lexer = lex.lex()

#
# Parser
#

def p_error(t):
    print("Illegal character '%s' in line %d" % (t.value[0], t.lexer.lineno))
    raise IOError("Syntax error")

def p_dsl_1(t):
    '''dsl : testcaseSequence'''
    t[0] = DSLNode(t[1])

def p_dsl_2(t):
    '''dsl : comment testcaseSequence'''
    t[0] = DSLNode(t[2])
    t[0].appendComment(t[1])


def p_testcaseSequence_1(t):
    '''testcaseSequence : testcaseSequence testcase'''
    t[0] = t[1] + [t[2]]


def p_testcaseSequence_2(t):
    '''testcaseSequence : testcase'''
    t[0] = [t[1]]


def p_testcase_1(t):
    '''testcase : TESTCASE qualident "{" testSequence "}"'''
    t[0] = TestcaseNode(t[2], t[4])


def p_testcase_2(t):
    '''testcase : comment TESTCASE qualident "{" testSequence "}"'''
    t[0] = TestcaseNode(t[3], t[5])
    t[0].appendComment(t[1])


def p_testSequence_1(t):
    '''testSequence : testSequence test'''
    t[0] = t[1] + [t[2]]


def p_testSequence_2(t):
    '''testSequence : test'''
    t[0] = [t[1]]


def p_test_comment(t):
    '''test : comment test'''
    t[2].appendComment(t[1])
    t[0] = t[2]


def p_test_1(t):
    '''test : opName inputs tightestOutputs accurateOutputs ";"'''
    t[0] = TestNode(t[1], t[2], t[3], t[4])


def p_test_2(t):
    '''test : opName inputs tightestOutputs ";"'''
    t[0] = TestNode(t[1], t[2], t[3], None)


def p_test_3(t):
    '''test : opName inputs accurateOutputs ";"'''
    t[0] = TestNode(t[1], t[2], None, t[3])


def p_test_4(t):
    '''test : opName tightestOutputs accurateOutputs ";"'''
    t[0] = TestNode(t[1], None, t[2], t[3])


def p_test_5(t):
    '''test : opName tightestOutputs ";"'''
    t[0] = TestNode(t[1], None, t[2], None)


def p_test_6(t):
    '''test : opName accurateOutputs ";"'''
    t[0] = TestNode(t[1], None, None, t[2])


def p_opName(t):
    '''opName : identifier'''
    t[0] = OperationNameNode(t[1])


def p_qualident_1(t):
    '''qualident : identifier'''
    t[0] = QualidentNode(t[1].val)


def p_qualident_2(t):
    '''qualident : qualident "." identifier'''
    t[1].appendIdentifier(t[3].val)
    t[0] = t[1]


def p_inputs(t):
    '''inputs : literalSequence'''
    t[0] = InputsNode(t[1])


def p_tightestOutputs(t):
    '''tightestOutputs : "=" literalSequence'''
    t[0] = TightestOutputsNode(t[2])


def p_accurateOutputs(t):
    '''accurateOutputs : "<" "=" literalSequence'''
    t[0] = AccurateOutputsNode(t[3])


def p_literalSequence_1(t):
    '''literalSequence : literalSequence literal'''
    t[0] = t[1] + [t[2]]


def p_literalSequence_2(t):
    '''literalSequence : literal'''
    t[0] = [t[1]]


def p_literal(t):
    '''literal : intervalLiteral
               | integerLiteral
               | numberLiteral
               | stringLiteral
               | booleanLiteral
               | overlapLiteral'''
    t[0] = t[1]


def p_interval_1(t):
    '''intervalLiteral : notAnInterval
                       | emptyInterval
                       | bareInterval'''
    t[0] = t[1]


def p_interval_2(t):
    '''intervalLiteral : bareInterval "_" decorationLiteral'''
    t[1].setDecoration(t[3])
    t[0] = t[1]


def p_bareInterval(t):
    '''bareInterval : infSupInterval
                    | entireInterval'''
    t[0] = t[1]

def p_infSupInterval_2(t):
    '''infSupInterval : "[" numberLiteral "," numberLiteral "]"'''
    t[0] = InfSupIntervalNode(t[2], t[4])

def p_emptyInterval(t):
    '''emptyInterval : "[" EMPTY "]"'''
    t[0] = EmptyIntervalNode()
    suffix = t[2][-1]
    if suffix == 'F':
        t[0].setType('interval<float>')
    elif suffix == 'L':
        t[0].setType('interval<long_double>')
    else:
        t[0].setType('interval<double>')

def p_entireInterval(t):
    '''entireInterval : "[" ENTIRE "]"'''
    t[0] = EntireIntervalNode()
    suffix = t[2][-1]
    if suffix == 'F':
        t[0].setType('interval<float>')
    elif suffix == 'L':
        t[0].setType('interval<long_double>')
    else:
        t[0].setType('interval<double>')


def p_notAnInterval(t):
    '''notAnInterval : "[" NAI "]"'''
    t[0] = NotAnIntervalNode()
    suffix = t[2][-1]
    if suffix == 'F':
        t[0].setType('interval<float>')
    elif suffix == 'L':
        t[0].setType('interval<long_double>')
    else:
        t[0].setType('interval<double>')


def p_decorationLiteral(t):
    '''decorationLiteral : TRV
                         | DEF
                         | DAC
                         | COM
                         | ILL'''
    t[0] = DecorationLiteralNode(t[1])


def p_numberLiteral(t):
    '''numberLiteral : floatingPointNumberLiteral
                     | infinityLiteral'''
    t[0] = t[1]


def p_infinityLiteral(t):
    '''infinityLiteral : INF'''
    if t[1].startswith('-'):
        t[0] = InfinityLiteralNode('-')
    else:
        t[0] = InfinityLiteralNode('+')
    suffix = t[1][-1]
    if suffix == 'F':
        t[0].setType('float')
    elif suffix == 'L':
        t[0].setType('long_double')
    else:
        t[0].setType('double')


def p_floatingPointNumberLiteral(t):
    '''floatingPointNumberLiteral : FLOAT'''
    tmp = FloatingPointNode(t[1])

    suffix = t[1][-1]

    if suffix == 'F':
        dataType = 'float'
    elif suffix == 'L':
        dataType = 'long_double'
    else:
        dataType = 'double'

    tmp.setType(dataType)
    t[0] = tmp


def p_integerLiteral(t):
    '''integerLiteral : INT'''
    tmp = IntegerLiteralNode(t[1])

    # append zeros to avoid if statements because of ints with too few digits
    # this won't change the behaviour
    suffix = ('000' + t[1])[-3:]
    if 'u' in suffix:
        unsigned = True
    else:
        unsigned = False

    lCount = suffix.count('l') + suffix.count('L')

    if lCount == 0:
        dataType = 'int'
    elif lCount == 1:
        dataType = 'long'
    else:
        dataType = 'long_long'

    tmp.setUnsigned(unsigned)
    tmp.setType(dataType)

    t[0] = tmp


def p_stringLiteral(t):
    '''stringLiteral : STRING'''
    # strip "
    t[0] = StringLiteralNode(t[1])


def p_booleanLiteral(t):
    '''booleanLiteral : TRUE
                      | FALSE'''
    t[0] = BooleanLiteralNode(t[1])


def p_overlapLiteral(t):
    '''overlapLiteral : BOTHEMPTY
                       | FIRSTEMPTY
                       | SECONDEMPTY
                       | BEFORE
                       | MEETS
                       | OVERLAPS
                       | STARTS
                       | CONTAINEDBY
                       | FINISHES
                       | EQUAL
                       | FINISHEDBY
                       | CONTAINS
                       | STARTEDBY
                       | OVERLAPPEDBY
                       | METBY
                       | AFTER'''
    t[0] = OverlapLiteralNode(t[1])


def p_comment_1(t):
    '''comment : LINE_COMMENT'''
    t[0] = LineCommentNode(t[1])


def p_comment_2(t):
    '''comment : BLOCK_COMMENT'''
    t[0] = BlockCommentNode(t[1])


def p_identifier(t):
    '''identifier : ID'''
    t[0] = IdentifierNode(t[1])


yacc.yacc(debug=0, write_tables=0)


def parse(testFilePath):
    '''
    Return an AST for the test file.

    Arguments:
    testFilePath -- path to the file as a string
    '''
    global yacc
    contents = open(testFilePath).read().strip()
    ast = yacc.parse(contents)
    ast.setFileName(testFilePath.split('/')[-1])
    return ast
