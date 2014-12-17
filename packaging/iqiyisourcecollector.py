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
IqiyiIqiyiSourceCollector module
"""

import os
import ConfigParser
import time
import re
from datetime import datetime
from subprocess import check_output


class IqiyiSourceCollector(object):
    """
    IqiyiSourceCollector class

    Responsible for creating a source archive which will contain:
    * All sources for that version
    * Versioning metadata
    * Full changelog
    It will also update the repo with all required versioning tags, if appropriate
    """

    repo = 'openvstorage'
    repo_path_metadata = '/tmp/repo_openvstorage_metadata'
    repo_path_code = '/tmp/repo_openvstorage_code'
    package_path = '/tmp/packages/openvstorage'

    def __init__(self):
        """
        Dummy init method, IqiyiSourceCollector is static
        """
        raise NotImplementedError('IqiyiSourceCollector is a static class')

    @staticmethod
    def collect(target=None, revision=None, suffix=None):
        """
        Executes the source collecting logic

        General steps:
        1. Figure out correct code commit, update code repo to that commit
        2. Generate changelog, if required
        3. Generate version schema
        4. Build 'upstream source package'
        5. Use this 'upstream source package' for building distribution specific packages

        @param target: Specifies the pacakging branch.
        @param revision: Specifies an exact target commit or tag
        @param suffix: A suffix for release packages (such as 'alpha', 'beta', 'rc1', 'rtm', ...)
        """

        print 'Collecting sources'

        if not os.path.exists(IqiyiSourceCollector.repo_path_code):
            os.makedirs(IqiyiSourceCollector.repo_path_code)
        if not os.path.exists(IqiyiSourceCollector.repo_path_metadata):
            os.makedirs(IqiyiSourceCollector.repo_path_metadata)
        if not os.path.exists(IqiyiSourceCollector.package_path):
            os.makedirs(IqiyiSourceCollector.package_path)

        # Update the metadata repo
        print '  Updating metadata'
        IqiyiSourceCollector._git_update_to(IqiyiSourceCollector.repo_path_metadata, 'master', 'HEAD')
        print '  Updating code'
        IqiyiSourceCollector._git_update_to(IqiyiSourceCollector.repo_path_code, target, revision)

        # Get current revision
        print '  Fetch current revision'
        current_revision = IqiyiSourceCollector._run(
            'git log -1', IqiyiSourceCollector.repo_path_code
        ).split('\n')[0].split(' ')[1].strip()[0:8]
        print '    Revision: {0}'.format(current_revision)

        # Get revision date
        revision_date = datetime.fromtimestamp(int(IqiyiSourceCollector._run("git log -1 --pretty=format:%ct",
                                              IqiyiSourceCollector.repo_path_code)))

        # Build version
        filename = '{0}/packaging/version.cfg'.format(IqiyiSourceCollector.repo_path_code)
        parser = ConfigParser.RawConfigParser()
        parser.read(filename)
        version = '{0}.{1}.{2}'.format(parser.get('main', 'major'),
                                       parser.get('main', 'minor'),
                                       parser.get('main', 'patch'))
        print '  Version: {0}'.format(version)

        # Load tag information
        tag_data = []
        print '  Loading tags'
        for raw_tag in IqiyiSourceCollector._run('git tag --list', IqiyiSourceCollector.repo_path_metadata).split('\n'):
            parts = raw_tag.split(' ')
            tag = parts[0]
            match = re.search('^(?P<version>[0-9]+?\.[0-9]+?\.[0-9]+?)(-(?P<suffix>.+)\.(?P<build>[0-9]+))?$', tag)
            if match:
                match_dict = match.groupdict()
                tag_version = match_dict['version']
                tag_build = match_dict['build']
                tag_suffix = match_dict['suffix']
                rev_number, rev_hash = parts[-1].split(':')
                tag_data.append({'version': tag_version,
                                 'build': tag_build,
                                 'suffix': tag_suffix,
                                 'rev_number': rev_number,
                                 'rev_hash': rev_hash})

        # Build changelog
        increment_build = True
        changes_found = False
        other_changes = False
        changelog = []
        changelog.append('Open vStorage (Used in IQIYI)')
        changelog.append('=============')
        changelog.append('')
        log = IqiyiSourceCollector._run("git log --no-merges --pretty=format:'* %ai - %s'", IqiyiSourceCollector.repo_path_code)
        for log_line in log.strip().split('\n'):
            changelog.append(log_line)


        # Build buildnumber
        print '  Generating build'
        builds = sorted(tag['build'] for tag in tag_data if tag['version'] == version and tag['suffix'] == suffix)
        if len(builds) > 0:
            build = int(builds[-1])
            if revision is None and increment_build is True:
                build += 1
            else:
                print '    No need to increment build'
        else:
            build = 1
        print '    Build: {0}'.format(build)

        # Save changelog
        if len(changelog) > 0:
            if increment_build is True:
                changelog.insert(5, '\n{0}{1}\n'.format(
                    version,
                    '-{0}.{1}'.format(suffix, build) if suffix is not None else ''
                ))
        with open('{0}/CHANGELOG.txt'.format(IqiyiSourceCollector.repo_path_code), 'w') as changelog_file:
            changelog_file.write('\n'.join(changelog))

        version_string = '{0}{1}'.format(
            version,
            '-{0}.{1}'.format(suffix, build) if suffix is not None else ''
        )
        print '  Full version: {0}'.format(version_string)

        # Building archive
        print '  Building archive'
        IqiyiSourceCollector._run(
            "tar -czf {0}/openvstorage_{1}.tar.gz --transform 's,^,openvstorage-{1}/,' scripts/install scripts/system config ovs webapps *.txt".format(
                IqiyiSourceCollector.package_path, version_string
            ), IqiyiSourceCollector.repo_path_code
        )
        IqiyiSourceCollector._run('rm -f CHANGELOG.txt', IqiyiSourceCollector.repo_path_code)
        print '    Archive: {0}/openvstorage_{1}.tar.gz'.format(IqiyiSourceCollector.package_path, version_string)

        print 'Done'

        distribution = 'iqiyi'

        return distribution, version, suffix, build, version_string, revision_date

    @staticmethod
    def _ignore_log(log_line):
        """
        Returns whether a mercurial log line should be ignored
        """
        if 'Added tag ' in log_line and ' for changeset ' in log_line:
            return True
        return False

    @staticmethod
    def _git_update_to(path, branch, commit):
        """
        Updates a given repo to a certain revision, cloning if it does not exist yet
        """
        if not os.path.exists('{0}/.git'.format(path)):
            IqiyiSourceCollector._run('git clone ssh://lumingfan@scm.qiyi.domain:29418/{0} {1}'.format(IqiyiSourceCollector.repo, path), path)
        IqiyiSourceCollector._run('git checkout {0}'.format(branch), path)
        IqiyiSourceCollector._run('git pull', path)
        IqiyiSourceCollector._run('git checkout {0}'.format(commit), path)

    @staticmethod
    def _run(command, working_directory):
        """
        Runs a comment, returning the output
        """
        print command
        print working_directory
        os.chdir(working_directory)
        return check_output(command, shell=True)
