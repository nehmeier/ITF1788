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

import dslparser
import testAST
import discovery
import lang
import os
import optparse
import re
from ast import literal_eval as makeTuple
import time
import ntpath
import textwrap


# inherit from OptionParser to overwrite format_epilog method
# this allows properly formatted multiline strings in help messages
class ConsoleParser(optparse.OptionParser):

        '''Handles the arguments passed to the program.'''
                
        def __init__(self):
            '''
            Define the valid options.
            '''
            super(ConsoleParser, self).__init__()
            self.add_option("-s", "--sourceDirectory", dest="sourceDir",
                     # TODO: check for operating systems other than linux
                     default='../ITL files',
                     help="Directory with DSL tests")

            self.add_option("-f", "--fileRegex", dest="fileRegex",
                            default='.*',
                            help="Regex for names of the desired DSL tests")

            self.add_option("-c", "--configurations", dest="configurations",
                            help="""Specify the plugin configurations.""")

            self.add_option("-o", "--outputDirectory", dest="outDir",
                            default="../output",
                            help="Output directory for generated files")
                            
            self.add_option("-v", "--verbose", action="store_true",
                            dest="verbose")
        
                     
        def processConsoleParameters(self):
            '''
            Read the passed arguments and process them.
            '''       
            (options, args) = self.parse_args()
            self._checkSrcDir(options)
            self._checkFileRegex(options)
            self.specList = self._buildSpecList(options)
            self.testFiles = self._buildTestFileList(options)
            self.outDir = options.outDir
            self.verbose = options.verbose
        
        def _buildSpecList(self, options):
            '''
            Use the passed arguments and build a list of he configurations that
            shall be generated.
            '''
            # if no specific configurations are given, generate tests for all
            # configurations
            if options.configurations is None or options.configurations == '*':
                return discovery.getSpecList()
            
            
            # regexes that are used to interpret the 'configurations'
            # console parameter
            identRegex = r"'[a-zA-Z][a-zA-Z0-9_]*'"
            wildcardRegex = r"'\*'"
            specListRegex = r"\s*\(\s*'.+'\s*,\s*'.+'\s*,\s*'.+'\s*\)\s*" + \
                            r"(\s*;\s*\(\s*'.+'\s*,\s*'.+'\s*,\s*'.+'\s*\)\s*)*"
            LTARegex = r"\s*\(\s*" + identRegex + r"\s*,\s*" + identRegex + \
                       r"\s*,\s*" + identRegex + r"\s*\)\s*"
            LTWRegex = r"\s*\(\s*" + identRegex + r"\s*,\s*" + identRegex + \
                       r"\s*,\s*" + wildcardRegex + r"\s*\)\s*"
            LWARegex = r"\s*\(\s*" + identRegex + r"\s*,\s*" + wildcardRegex + \
                       r"\s*,\s*" + identRegex + r"\s*\)\s*"
            LWWRegex = r"\s*\(\s*" + identRegex + r"\s*,\s*" + wildcardRegex + \
                       r"\s*,\s*" + wildcardRegex + r"\s*\)\s*"

            if re.match(specListRegex, options.configurations):
                # use configurations list parameter
                tmp = options.configurations.split(';')
                
                try:
                    tmp = [makeTuple(el.strip()) for el in tmp]
                    valid = True
                except:
                    valid = False
                if not valid:
                    raise IOError('Invalid specification list:' +\
                                    options.configurations +\
                                    '\nRun "python3 main.py --help" to see the\
                                    correct syntax.')

                specList = []

                for spec in tmp:
                    if re.match(LTARegex, str(spec)):
                        specList += [spec]
                    elif re.match(LTWRegex, str(spec)):
                        specList += \
                         discovery.getSpecListByLanguageAndTestLibrary(spec[0],
                                                                       spec[1])
                    elif re.match(LWARegex, str(spec)):
                        specList += \
                         discovery.getSpecListByLanguageAndArithmeticLibrary(spec[0],
                                                                             spec[2])
                    elif re.match(LWWRegex, str(spec)):
                        specList += discovery.getSpecListByLanguage(spec[0])

            else:
                raise IOError('Invalid configurations specification: ' +
                              options.configurations)
            return specList
            
        def _buildTestFileList(self, options):
            '''
            Assemble a list of all ITL tests corresponding to the passed
            parameter
            '''
            testFiles = [os.path.join(options.sourceDir, f)
                              for f in os.listdir(options.sourceDir)
                              if os.path.isfile(os.path.join(options.sourceDir,
                                                             f))
                              if re.match(options.fileRegex, f)]
            testFiles = list(filter(lambda f: f.endswith('.itl'), testFiles))
            return testFiles
            
        def _checkSrcDir(self, options):
            '''
            Check if the path to the source directory is well formed
            '''
            if not os.path.isdir(options.sourceDir):
                raise IOError('Invalid source directory: ' +\
                                options.sourceDir)
                
        def _checkFileRegex(self, options):
            '''
            Check if the file regex is valid
            '''
            try:
                re.compile(options.fileRegex)
                valid = True
            except:
                valid = False
            if not valid:
                raise IOError('Invalid file regex: ' + options.fileRegex)
            

        def format_epilog(self, formatter):
            '''
            Help message.
            '''
            return textwrap.dedent("""
                    Examples:
                    -- print help
                    python3 main.py -h
                    
                    -- run ITF1788 with default source and output folder
                    python3 main.py
                    
                    -- use verbose output
                    python3 main.py -v

                    -- generate tests for all source files in "../ITL files" and
                       all configurations
                    python3 main.py -s "../ITL files"

                    -- like above, but use only test files whose name starts
                       with 'test'
                    python3 main.py -s "../ITL files" -f "test.*"

                    -- use output directory "../outputs"
                    python3 main.py -s "../ITL files" -o "../outputs"

                    In the following examples, a wildcard denotes that every
                    available option for that position shall be used.

                    -- generate tests for C++ only
                    python3 main.py -s "../ITL files" -c "('cpp','*','*')"

                    -- generate tests for C++ and BOOST Test Library only
                    python3 main.py -s "../ITL files" -c "('cpp','BOOST','*')"

                    --generate tests for C++ and libieeep1788 only
                    python3 main.py -s "../ITL files" -c "('cpp','*','libieeep1788')"

                    --generate tests for C++, BOOST Test library and lib1
                    python3 main.py -s "../ITL files" -c "('cpp','BOOST','lib1')"

                    --generate tests for C++ and Octave only
                    python3 main.py -s "../ITL files" -c "('cpp','*','*');('octave','*','*')"
                    """)

def main():            
    # measure run time
    startTime = time.clock()
    
    # parse console parameters
    optParser = ConsoleParser()
    optParser.processConsoleParameters()
    specList = optParser.specList
    testFiles = optParser.testFiles
    outDir = optParser.outDir

    # Assemble source files
    for testfile in testFiles:
        # parse the current ITL file and build an abstract syntax tree
        ast = dslparser.parse(testfile)
        
        # iterate over configurations
        for language, testlib, arithlib in specList:
            spec = discovery.getSpecification(language, testlib, arithlib)
            out = lang.OutputSpecification(spec[0], spec[1], spec[2])
            cbPath = discovery.getCbPath(language)
            
            # paths to output directory and output file
            writeDir = '/'.join([outDir, language, testlib, arithlib])
            writeFile = '.'.join(ntpath.basename(testfile).split('.')[:-1]) + \
                        out.lang_extension
            
            if optParser.verbose:
                print('Generating', writeFile, 'for specification',
                      str((language, testlib, arithlib)), '...')    
            
            # generate output content by visiting the AST
            v = testAST.ASTVisitor(out, cbPath)
            (content, warnings) = ast.accept(v)           

            # create output directory if it does not exist
            if not os.path.exists(writeDir):
                os.makedirs(writeDir)

            # write content
            open(writeDir + '/' + writeFile, 'w+').write(content)
            if optParser.verbose:
                for warn in warnings:
                    print(warn)
                print('Done.\n')
            
    endTime = time.clock()
    if optParser.verbose:
        print('-'*80)
        print('Generated output for', len(testFiles), 'testfiles in',
              "%.2f" % round(endTime - startTime, 2), 'seconds.')

# Run main method if this script is called directly
if __name__ == '__main__':
    main()
