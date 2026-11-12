#!/usr/bin/env bash

export BUTLER_REPO={src.repo}
export MAIN_COLLECTION={src.collection}
export DATASET=Dataset/$MAIN_COLLECTION/{src.name}
export SCOPE={src.scope}

rucio whoami

cat <<EOF >rucio_register.cfg
rucio_rse: "{src.rucio_rse}"
scope: {src.scope}
rse_root: "{src.rse_root}"
dtn_url: "{src.dtn_url}"
EOF

export CONFIG_FILE=rucio_register.cfg

for dstype in {dataset_type_list}; do
  rucio-register data-products \
    --repo $BUTLER_REPO \
    --rucio-dataset $DATASET \
    --rucio-register-config $CONFIG_FILE \
    --collections $MAIN_COLLECTION \
    --dataset-type $dstype \
    --log-level DEBUG \
    --chunk-size 30
done

result1=$?
echo $result1
if [ "$result1" != "0" ]; then
    echo "Butler Command 1 Failed"
else
    echo "Successful Butler Command 1"
fi

rucio rule add --copies 2 --rses {src.rucio_rse}\|{dest.rucio_rse} $SCOPE:$DATASET

sleep 20

rucio replica list dataset $SCOPE:$DATASET

result2=$?
echo $result2

if [ "$result2" != "0" ]; then
    echo "Butler Command 2 Failed"
else
    echo "Successful Butler 2 Command"
fi

if  [ $result1  != "0"  -o  $result2  != "0" ]; then
        exit 1
fi

exit 0
