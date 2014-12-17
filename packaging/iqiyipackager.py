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
Packager module
"""

from optparse import OptionParser
from iqiyisourcecollector import IqiyiSourceCollector
from debian import DebianPackager

if __name__ == '__main__':
    parser = OptionParser(description='Open vStorage packager')
    parser.add_option('-d', '--target', dest='target', default='master')
    parser.add_option('-r', '--revision', dest='revision', default='HEAD')
    parser.add_option('-s', '--suffix', dest='suffix', default='test')
    options, args = parser.parse_args()

    # 1. Collect sources
    source_metadata = IqiyiSourceCollector.collect(target=options.target, revision=options.revision, suffix=options.suffix)

    if source_metadata is not None:
        # 2. Build packages
        #    - CentOS
        DebianPackager.package(source_metadata)
