#!/bin/bash

systemctl -l | grep ovs | awk '{print $1}' | xargs systemctl stop

rm -rf /var/log/ovs
rm -rf /mnt/db/*
rm -rf /opt/OpenvStorage
rm -rf /etc/avahi/services/ovs_cluster.service
rm -rf /usr/bin/ovs

rm -rf /var/lib/rabbitmq/mnesia/*
rm -rf /usr/lib/systemd/system/ovs-*
pushd /etc/systemd/system
   find . -name "ovs-*" | xargs rm -rf
popd

systemctl -l | grep ovs- | awk '{print $1}' | xargs systemctl reset-failed

systemctl daemon-reload
