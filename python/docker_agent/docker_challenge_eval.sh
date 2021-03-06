# Automation of validation and scoring
# Set environment variables in the `crontab -e` for synapse username and password
script_dir=$(dirname $0)
if [ ! -d "$script_dir/log" ]; then
  mkdir $script_dir/log
fi
if [ ! -d "$script_dir/output" ]; then
  mkdir $script_dir/output
fi
#---------------------
#Validate submissions
#---------------------
python $script_dir/docker_challenge.py --acknowledge-receipt --canCancel -u $SYNAPSE_USER -p $SYNAPSE_PASS --send-messages --notifications validate --all >> $script_dir/log/score.log 2>&1

#--------------------
#Score submissions
#--------------------
python $script_dir/docker_challenge.py --canCancel -u $SYNAPSE_USER -p $SYNAPSE_PASS --send-messages --notifications score --all >> $script_dir/log/score.log 2>&1

#--------------------
#Stop submissions
#--------------------
#python $script_dir/docker_challenge.py -u $SYNAPSE_USER -p $SYNAPSE_PASS --send-messages --notifications dockerstop --all >> $script_dir/log/score.log 2>&1