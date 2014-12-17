#!/bin/bash

cur_dir=`dirname $0`
cur_dir=`realpath $cur_dir`

source $cur_dir/config

chmod 1777 /run/lock

yum install -y coreutils

# support development tools
yum groupinstall -y "Development tools"
yum install -y zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel

# install python 2.7

yum install -y python python-devel

# install pip
python $cur_dir/ez_setup.py --download-base=http://pypi.douban.com/packages/source/s/setuptools/
easy_install pip

# configure pip
mkdir -p ~/.pip

rsync -arl $cur_dir/pip.conf ~/.pip
rsync -arl $cur_dir/.pydistutils.cfg ~

# install other requirements
yum install -y ntp

# install components

for c in core webapps
do
  for i in `cat $cur_dir/${c}-dirs`;do mkdir -p $i;done
  /bin/bash $cur_dir/openvstorage-${c}.preinst
done
