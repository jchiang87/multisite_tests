source /sdf/group/rubin/sw/htcondor.d/k8s_frdf/env.sh
source /sdf/group/rubin/sw/w_latest/loadLSST.bash
setup lsst_distrib -t w_latest

setup -r /sdf/data/rubin/user/jchiang/CM/multisite_tests -j

eups list | grep LOCAL

set -o physical
cd .

PS1="\[\033]0;\w\007\][`hostname` w_latest] "
