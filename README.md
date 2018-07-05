# awssnapshot-inventory
AWS Orphaned snapshot complete inventory

This is genertic script to pull the orphaned snapshot inventory for AWS and provide the details to Slack Channel

Works on Pip >= 2.7 for higher version check AWS SDK's for snapshot list or instance list.
1. Create a Slack Channel 
2. Get your slack token for your enterprise account or create Incoming webhook for the slack channel
3. Create profile which has AWS creditinals/ Define assume role
4. Create a bash script to check loop and check all the AWS accounts or if you have single account then we can run direct Python script
