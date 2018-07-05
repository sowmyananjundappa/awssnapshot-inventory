#!/usr/bin/python
#coding=utf-8
import os
import sys
import json
import csv
import pickle
import subprocess
import re
from botocore.exceptions import ClientError
from slackclient import SlackClient
prof = sys.argv[1]
owner = sys.argv[2]
volume = ""
volume_id = ""

# To get slack token as environment variable"
slack_token = os.environ["SLACK_API_TOKEN"] 

# To provide slack token directly
slack_token = "************************"

#Slack function call
sc = SlackClient(slack_token)
def slack_msg(message):
    sc.api_call("chat.postMessage", channel="#test", text=message)
    
 #To check if volume exists
def vol_exists(volume_id):
    if not volume_id: return ''
    try:
        volume_inuse = os.system("aws ec2 describe-volumes --volume-id %(volume_id)s --profile %(prof)s  --output json  --region "region" > /var/lib/jenkins/jobs/snapshot/volume_inuse.json" % globals())
        with open('/var/lib/jenkins/jobs/snapshot/volume_inuse.json') as vol_file:
            vol_data = json.load(vol_file)
            for vol_index in range(len(vol_data['Volumes'])):
                volume_id1 = str(vol_data['Volumes'][vol_index]['VolumeId'])
                if(volume_id == volume_id1):
                    return True
    except ClientError:
        return False
        
#To check if Isntance exists     
def instance_exists(instance_id):
    if not instance_id: return ''
    try:
        ec2_instance_details = os.system("aws ec2 describe-instances --profile %(prof)s --output json --instance-ids %(instance_id)s --region "region" > /var/lib/jenkins/jobs/snapshot/ec2_details.json" % globals())
        with open('/var/lib/jenkins/jobs/snapshot/ec2_details.json') as ec2_details_file:
            ec2_details_data = json.load(ec2_details_file)
            for ec2_detail_index in range(len(ec2_details_data['Reservations'][0]['Instances'])):
                val = ec2_details_data['Reservations'][0]['Instances'][0]['InstanceId']
                if(instance_id == val):
                    return True
    except (ValueError, ClientError, IndexError):
        return False

#To check AMI exists
def image_exists(image_id):
    if not image_id: return ''
    try:
        requestObj = os.system("aws ec2 describe-images --profile %(prof)s --output json --image-ids %(image_id)s --region "region" > /var/lib/jenkins/jobs/snapshot/image_details.json" % globals())
        with open('/var/lib/jenkins/jobs/snapshot/image_details.json') as image_file:
            image_data = json.load(image_file)
            for image_index in range(len(image_data['Images'])):
                images = image_data['Images'][0]['ImageId']
                if not image_data["Images"]:
                    return False
                return True
    except (ValueError, ClientError, IndexError):
      return False
      
#Regex format to match the snapshot id
def parse_description(description):
    regex = r"^Created by CreateImage\((.*?)\) for (.*?) "
    matches = re.finditer(regex, description, re.MULTILINE)
    for matchNum, match in enumerate(matches):
        return match.groups()
    return '', ''

# Main script to pull the inventory
snapshot_report = os.system("aws ec2 describe-snapshots --profile %(prof)s --owner-ids %(owner)s --output json  --region "region" > /var/lib/jenkins/jobs/snapshot/snapshots_metadata.json" % globals())
with open('/var/lib/jenkins/jobs/snapshot/snapshots_metadata.json') as snapshot_file:
    snap_data = json.load(snapshot_file)
    null_files = os.system(">/var/lib/jenkins/workspace/snapshot/snapshot_data_"+prof+".csv")
    csvfile = open("/var/lib/jenkins/workspace/snapshot/snapshot_data_"+prof+".csv", "a")
    writer = csv.writer(csvfile)
    writer.writerow(['snapshot id','description','started','size,volume','volume exists','instance','instance exists','ami','ami exists'])
    for snap_index in range(len(snap_data['Snapshots'])):
        instance_id, image_id = parse_description(snap_data['Snapshots'][snap_index]['Description'])
        writer.writerow([
            str(snap_data['Snapshots'][snap_index]['SnapshotId']),
            str(snap_data['Snapshots'][snap_index]['Description']),
            str(snap_data['Snapshots'][snap_index]['StartTime']),
            str(snap_data['Snapshots'][snap_index]['VolumeSize']),
            vol_exists(str(snap_data['Snapshots'][snap_index]['VolumeId'])),
            instance_id,
            str(instance_exists(instance_id)),
            image_id,
            str(image_exists(image_id)),
        ])
