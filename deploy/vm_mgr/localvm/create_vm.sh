#!/bin/bash

#!/bin/bash

vm_name=$1
vm_vpool=$2

vm_img="/mnt/${vm_vpool}/${vm_name}.raw"
qemu-img create -f raw $vm_img 8G
virt-install \
     --name $vm_name \
     --ram 2000 \
     --disk path=$vm_img,format=raw \
     --accelerate \
     --network network=default,model=virtio \
     --cdrom /tmp/CentOS-6.5-x86_64-minimal.iso \
     --boot cdrom \
     --vnc \
     --vnclisten=0.0.0.0
