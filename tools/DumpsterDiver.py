#!/bin/env python

import advancedSearch
import core
import os
import sys
import argparse
from termcolor import colored
from pwn import *


#Borrowed from https://bitbucket.org/ruamel/std.argparse
class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)



# please readme
def opening():
    title = """
    get iot weakpassword and hardcode
            """
    creds = "20180702"

    print(colored(title, 'magenta') )
    print(colored(creds, 'red') )
    print()
    print()


def set_key_characteristics(min_key, max_key, entropy):
    core.MIN_KEY_LENGTH = min_key
    core.MAX_KEY_LENGTH = max_key
    core.HIGH_ENTROPY_EDGE = entropy
def getresult():
    print (colored("all result details below:",'yellow'))
    i=0
    file = open("./results.json")
    for line in file:
        for name in line.split(','):
            if "File" in name:
                print(colored("%d : %s\n"%(i,name), 'yellow'))
                i+=1

    file.close()

if __name__ == '__main__':

    opening()
    parser = argparse.ArgumentParser(formatter_class=SmartFormatter)
    basic = parser.add_argument_group('BASIC USAGE')
    configuration = parser.add_argument_group('CONFIGURATION')
    basic.add_argument('-p', dest='local_path', required=True, 
        help="path to the folder containing files to be analyzed")
    basic.add_argument('-r', '--remove', action='store_true', 
        help="when this flag is set, then files which don't contain"
             + " any secret will be removed.")
    basic.add_argument('-a', '--advance', action='store_true', 
        help="when this flag is set, then all files will be additionally "
             + "analyzed using rules specified in 'rules.yaml' file.")
    basic.add_argument('-s', '--secret', action='store_true', 
        help="when this flag is set, then all files will be additionally "
             + "analyzed in search of hardcoded passwords.")    
    basic.add_argument('-l', '--level', type=int, choices=range(4), 
        metavar='[0,3]',help="R|0 - searches for short (20-40 bytes long) keys, \n"
                             "    e.g. AWS Access Key ID. \n"
                             "1 - (default) searches for typical (40-66 bytes long) keys, \n"
                             "    e.g. AWS Secret Access Key or Azure Shared Key. \n"
                             "2 - searches for long (66-1800 bytes long) keys, \n"
                             "    e.g. SSH private key\n"
                             "3 - searches for any key (20-1800 bytes long), \n"
                             "    careful as it generates lots of false positives\n\n")
    basic.add_argument('-o', dest='outfile', default='results.json', 
        help="output file in JSON format.")   

    configuration.add_argument('--min-key', dest='min_key', type=int, 
        help="specifies the minimum key length to be analyzed (default is 20).")
    configuration.add_argument('--max-key', dest='max_key', action='store', 
        type=int, help="specifies the maximum key length to be analyzed (default is 80).")
    configuration.add_argument('--entropy', action='store', type=float,
        help="specifies the edge of high entropy (default is 4.3).")
    configuration.add_argument('--min-pass', dest='min_pass', action='store', 
        type=int, help="specifies the minimum password length to be analyzed"
                       + " (default is 8). Requires adding '-s' flag to the "
                       + "syntax.")
    configuration.add_argument('--max-pass', dest='max_pass', action='store', 
        type=int, help="specifies the maximum password length to be analyzed"
                       + " (default is 12). Requires adding '-s' flag to the "
                       + "syntax.")
    configuration.add_argument('--pass-complex', dest='password_complexity', 
        type=int, choices=range(1,10), help="specifies the edge of password "
                       + "complexity between 1 (trivial passwords) to 9 (very "
                       + "complex passwords) (default is 8). Requires adding "
                       + "'-s' flag to the syntax.")
    configuration.add_argument('--grep-words', dest='grep_words', action='store', 
        nargs='+', help="specifies the grep words to look for. Multiple words should be "
                        + "separated by space. Wildcards are supported. Requires adding "
                        + "'-a' flag to the syntax.")

    try:
        arguments = parser.parse_args()
        # #print "get parms\n"
        # print arguments
        # print arguments.remove
        # print arguments.advance
        # print arguments.secret
        # print arguments.outfile
        # print "get parms over\n"
        core.REMOVE_FLAG = arguments.remove
        core.ADVANCED_SEARCH = arguments.advance
        core.PASSWORD_SEARCH = arguments.secret
        core.OUTFILE = arguments.outfile

        if arguments.local_path:

            if os.path.isdir(arguments.local_path):
                core.PATH = os.path.abspath(arguments.local_path)
                #print core.PATH
            else:
                print("The specified path '" + arguments.local_path 
                      + "' doesn't exist.")
                sys.exit()

        if arguments.level == 0:
            set_key_characteristics(20, 40, 3.2)

        if arguments.level == 1:
            set_key_characteristics(40, 66, 4.3)

        if arguments.level == 2:
            set_key_characteristics(66, 76, 5.0)

        if arguments.level == 3:
            set_key_characteristics(20, 1800, 3.2)


        if arguments.min_key: core.MIN_KEY_LENGTH = arguments.min_key
        if arguments.max_key: core.MAX_KEY_LENGTH = arguments.max_key
        if arguments.entropy: core.HIGH_ENTROPY_EDGE = arguments.entropy
        if arguments.min_pass: core.MIN_PASS_LENGTH = arguments.min_pass
        if arguments.max_pass: core.MAX_PASS_LENGTH = arguments.max_pass
        if arguments.password_complexity: core.PASSWORD_COMPLEXITY = arguments.password_complexity
        if arguments.grep_words: advancedSearch.GREP_WORDS = arguments.grep_words

        core.start_the_hunt()

        getresult()
            
    except IOError as msg:
        #print "222222\n"
        parser.error(str(msg))


