# Copyright 2014 CloudFounders NV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
script to update files in the codebase:
- starting from root folder (argument after all options : /folder/ovs/)
- all .py files
-- option to specify other files (option --extensions="cfg,txt")
-- extensions without dot and comma separated, no spaces
-- "cfg,txt" OK
-- ".cfg, .txt" NOK
- check if it doesn't exist
- add to all files (but check first if it exists) (option --fix)
-- text: "license see http://www.openvstorage.com/licenses/opensource/"
    (second argument after folder : "license see... ")
only works for text files (no binary files)

call: script.py [--extensions="cfg,txt"] [--fix] /folder/ovs "license text"
help: script.py --help
"""

#define files and directories to skip checking
# relative paths to the root
skip_files = ['/webapps/frontend/index.html',
              '/config/gunicorn.cfg.py',
              '/config/django/django_gunicorn_ovs.cfg.py']
skip_dirs = ['/webapps/frontend/lib',
             '/webapps/api/static/rest_framework/css',
             '/webapps/frontend/css',
             '/webapps/api/static/rest_framework/js',
             '/.hg',
             '/scripts/',
             '/extensions/db/arakoon/']
#define files and directories to except from skip
# should be subdirectories of the skip directories
# or files inside the skip_dirs
except_skip_dirs = ['/webapps/frontend/lib/ovs', ]
except_skip_files = ['/webapps/frontend/css/ovs.css']

import getopt
import sys
import os
import codecs


def list_files(dir_, extensions=[]):
    """
    list all files in dir
    """
    print('\t\t processing directory: {0}'.format(dir_))
    files = []
    files_dirs = os.listdir(dir_)
    for file in files_dirs:
        path = os.path.join(dir_, file)
        if os.path.isfile(path):
            if extensions:
                for extension in extensions:
                    if path.endswith(extension):
                        files.append(path)
                        break
            else:
                files.append(path)
    return files


def list_dirs(dir_):
    """
    list all directories in dir
    """
    dirs = []
    files_dirs = os.listdir(dir_)
    for file in files_dirs:
        path = os.path.join(dir_, file)
        if os.path.isdir(path):
            dirs.append(path)
    return dirs


def get_all_files(root_folder, extensions=[]):
    """
    recursively get all files in root_folder
    """
    for skip_dir in skip_dirs:
        dirskip = False
        if skip_dir in root_folder:
            dirskip = True
            for except_skip_dir in except_skip_dirs:
                if skip_dir in except_skip_dir:
                    dirskip = False
                    break
            if dirskip:
                return []
    files_to_process = []
    if not os.path.exists(root_folder):
        raise ValueError('Root folder {0} does not exist'.format(root_folder))
    files_to_process.extend(list_files(root_folder, extensions))
    for dir_ in list_dirs(root_folder):
        dir_path = os.path.join(root_folder, dir_)
        files_to_process.extend(get_all_files(dir_path, extensions))
    return files_to_process


def get_comment_style(fextension):
    """
    get the comment style for the specific extension
    extension: (before, after)
    """
    comments = {'.py': ('#', ''),
                '.cfg': ('#', ''),
                '.js': ('//', ''),
                '.html': ('<!--', ' -->'),
                '.css': ('/*', '*/')}
    if not fextension in comments:
        print('[WARNING] Unkown extension {0} will assume comment style "#TEXT" '\
              .format(fextension))
    values = comments.get(fextension, ('#', ''))
    return values


def get_text(filename, text, lineend=False):
    """
    construct the license text line
    """
    _, fextension = os.path.splitext(filename)
    if lineend:
        if fextension in ('.html',):
            end = '\r\n'
        else:
            end = '\n'
    else:
        end = ""
    before, after = get_comment_style(fextension)
    return "{0} {1}{2}{3}".format(before, text, after, end)

def fix_lines(fix, lines):
    """
    add header to lines
    check for UTF8 BOM
    check for shebang
    """
    if fix:
        #insert new line after BOM
        if lines[0].startswith(codecs.BOM_UTF8):

            if lines[0].replace(codecs.BOM_UTF8, b'').startswith(b'#!'): #shebang
                print('fixed line with shebang and bom')
                lines.insert(1, get_text(file, text, True).encode('utf-8'))
            else:
                lines[0] = lines[0].replace(codecs.BOM_UTF8, b'')
                lines.insert(0, codecs.BOM_UTF8 + get_text(file, text, True)\
                             .encode('utf-8'))
        else:
            if lines[0].startswith(b'#!'):
                print('fixed line with shebang')
                lines.insert(1, get_text(file, text, True).encode('utf-8'))
            else:
                lines.insert(0, get_text(file, text, True).encode('utf-8'))
        f.seek(0)
        f.writelines(lines)
        print('fixed file {0}'.format(file))
    else:
        print('not fixing, file does not contain header {0}'.format(file))

# @TODO: This file needs to be updated to process the multiline license header
sys.exit(1)

short_options = ''
long_options = ['extensions=', 'fix', 'help']
opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
opts = dict(map(lambda opt: (opt[0].strip('--'), opt[1]), opts))

if 'help' in opts:
    print(__doc__)
    sys.exit(0)
#print(opts, args)
if len(args) != 2:
    raise ValueError('Expected root folder and text as arguments')

root_folder = args[0]
text = args[1]
_extensions = opts.get('extensions', '')
if _extensions:
    extensions = [ext for ext in _extensions.split(',') if ext != '']
else:
    extensions = ['py']

fix = 'fix' in opts

files_to_process = get_all_files(root_folder, extensions)
print('Total files to process (based on extensions {0}): {1}'\
      .format(str(extensions), len(files_to_process)))

for file in files_to_process:
    skip = False
    for skip_file in skip_files:
        if file.endswith(skip_file):
            print('skipping file {0}'.format(file))
            skip = True
            break
    for skip_dir in skip_dirs:
        dirskip = False
        if skip_dir in file:
            dirskip = True
            for except_skip_dir in except_skip_dirs:
                if except_skip_dir in file:
                    dirskip = False
                    break
            if dirskip:
                skip = True
                print('skipped file {0}'.format(file))
                break
    for except_skip_file in except_skip_files:
        if except_skip_file in file:
            skip = False
            break
    if not skip:
        with open(file, 'r+') as f:
            lines = f.readlines()
            if lines:
                if lines[0].strip().replace(codecs.BOM_UTF8, b'') == get_text(file, text):
                    pass
                elif lines[0].strip().replace(codecs.BOM_UTF8, b'').startswith(b'#!') and\
                    lines[1].strip().replace(codecs.BOM_UTF8, b'') == get_text(file, text):
                    pass
                else:
                    fix_lines(fix, lines)
            else:
                if fix:
                    print('fixed empty file {0}, no header'.format(file))
                    lines.insert(0, get_text(file, text, True))
                    f.seek(0)
                    f.writelines(lines)
                else:
                    print('not fixing, file does not contain header {0}'.format(file))

print('Done processing...')
