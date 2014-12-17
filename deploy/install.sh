#!/bin/bash

cur_dir=`dirname $0`
cur_dir=`realpath $cur_dir`
base_dir=`dirname $cur_dir`

source $cur_dir/config

for i in core webapps
do
   while read line
   do
      src=`echo $line | awk '{print $1}'`
      dest=`echo $line | awk '{print $2}'`
      rsync -arl $base_dir/$src /"$dest"
   done < $cur_dir/openvstorage-${i}.install
   chmod +x /usr/bin/ovs
done
