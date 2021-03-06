#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  include.py
#
#  Copyright 2015 Christopher MacMackin <cmacmackin@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from __future__ import print_function
import re
import os.path
from codecs import open
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from pathlib import Path

INC_SYNTAX = re.compile(r'\{!\s*(.+?)\s*!\}')
# Alternative future include syntax
# [TBD] INC_LINK_SYNTAX = re.compile(r':\[\s*(.+?)\s*\]\(\s*(.+?)\s*\)')
HEADING_SYNTAX = re.compile( '^#+' )

'''
LINK [Title](link) / IMG: ![Title](link)
Group 1: Title
Group 2: Link
'''
LINK_SYNTAX = re.compile(r'\[\s*(.+?)\s*\]\(\s*(.+?)\s*\)')
IMG_SYNTAX = re.compile(r'!\[\s*(.+?)\s*\]\(\s*(.+?)\s*\)')

class MarkdownInclude(Extension):
    def __init__(self, configs={}):
        self.config = {
            'base_path': ['.', 'Root location from which to evaluate ' \
                'relative paths for the include statement.'],
            'encoding': ['utf-8', 'Encoding for included files.'],
            'headingOffset': [0, 'Increases heading depth by a specific ' \
                'amount (combines with _inheritHeadingDepth_ option).'],
            'inheritHeadingDepth': [False, 'Increases headings on included ' \
                'file by amount of previous heading (combines with '\
                '_headingOffset_ option).'],
            'relativeIncludes': [False, 'Allow includes to use paths relative to the including file.'],
            'throwException': [False, 'If the extension is unable to find an included file '\
                                'it will throw an exception.  '\
                                'Default behavior is to print a warning '\
                                'and continue parsing the file. ']
        }
        for key, value in configs.items():
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add(
            'include', IncludePreprocessor(md,self.getConfigs()),'_begin'
        )


class IncludePreprocessor(Preprocessor):
    '''
    This provides an "include" function for Markdown, similar to that found in
    LaTeX (also the C pre-processor and Fortran). The syntax is {!filename!},
    which will be replaced by the contents of filename. Any such statements in
    filename will also be replaced. This replacement is done prior to any other
    Markdown processing.
    '''
    def __init__(self, md, config):
        super(IncludePreprocessor, self).__init__(md)
        self.base_path = config['base_path']
        self.encoding = config['encoding']
        self.inheritHeadingDepth = config['inheritHeadingDepth']
        self.headingOffset = config['headingOffset']
        self.throwException = config['throwException']
        self.relativeIncludes = config['relativeIncludes']

    '''Web links can be ignored'''
    def ignore_link(self, link):
        return link.startswith(u"http") or link.startswith(u"#") or link.startswith(u"ftp") or link.startswith(
            u"www") or link.startswith(u"mailto")

    '''Return the location of the included file'''
    def get_dir_path(self, file):
        path = Path(file)
        return path.parent

    '''Remove yaml from the inclusion'''
    def excise_yaml(self, text):
        YAML_MARKS = ['...', '---']
        # Find the yaml marks
        indices = [i for i, s in enumerate(text) if any(code in s for code in YAML_MARKS)]
        # Delete everything between the first two marks
        del text[indices[0]:indices[1]]
        return text

    def run(self, lines):
        done = False
        bonusHeading = ''
        while not done:
            for loc, line in enumerate(lines):
                m = INC_SYNTAX.search(line)

                if m:
                    filename = m.group(1)
                    filename = os.path.expanduser(filename)
                    if not os.path.isabs(filename):
                        filename = os.path.normpath(
                            os.path.join(self.base_path,filename)
                        )
                    try:
                        with open(filename, 'r', encoding=self.encoding) as r:
                            text = r.readlines()
                            # Remove Yaml frontmatter
                            text = self.excise_yaml(text)
                            
                    except Exception as e:
                        if not self.throwException:
                            print('Warning: could not find file {}. Ignoring '
                                  'include statement. Error: {}'.format(filename, e))
                            lines[loc] = INC_SYNTAX.sub('',line)
                            break
                        else:
                            raise e

                    line_split = INC_SYNTAX.split(line)
                    if len(text) == 0:
                        text.append('')
                    for i in range(len(text)):
                        # Strip the newline, and optionally increase header depth
                        if self.inheritHeadingDepth or self.headingOffset:
                            if HEADING_SYNTAX.search(text[i]):
                                text[i] = text[i][0:-1]
                                if self.inheritHeadingDepth:
                                    text[i] = bonusHeading + text[i]
                                if self.headingOffset:
                                    text[i] = '#' * self.headingOffset + text[i]
                        else:
                            text[i] = text[i][0:-1]
                            
                    text[0] = line_split[0] + text[0]
                    text[-1] = text[-1] + line_split[2]
                    lines = lines[:loc] + text + lines[loc+1:]
                    break
                    
                else:
                    h = HEADING_SYNTAX.search(line)
                    if h:
                        headingDepth = len(h.group(0))
                        bonusHeading = '#' * headingDepth
                
            else:
                done = True
        return lines


def makeExtension(*args,**kwargs):
    return MarkdownInclude(kwargs)
