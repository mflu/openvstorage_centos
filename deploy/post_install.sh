#!/bin/bash

cur_dir=`dirname $0`
cur_dir=`realpath $cur_dir`

source $cur_dir/config

for i in core webapps
do
  /bin/bash -x $cur_dir/openvstorage-${i}.postinst
done
