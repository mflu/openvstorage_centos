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
Generic platform module, executing statements on local node
"""

from subprocess import check_output

class Osdist(object):
    """
    Generic helper class
    """

    def __init__(self):
        """
        Dummy init method
        """
        _ = self

    @staticmethod
    def is_ubuntu(client=None):
        """
        Returns whether it is ubuntu
        """
        cmd = "python -c 'import platform;print \"Ubuntu\" in platform.platform();'"
        if client is None:
            return check_output(cmd, shell=True).strip() == "True"
        else:
            return client.run(cmd).strip() == "True"
