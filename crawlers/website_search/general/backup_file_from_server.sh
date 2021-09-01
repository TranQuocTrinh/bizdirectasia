#!/bin/bash
# loop forever
for (( ; ; ))
do
  scp -i /home/tqtrinh/wslab_key.pem ubuntu@13.212.62.93:/home/ubuntu/general/data_website/korea/* korea/
done

