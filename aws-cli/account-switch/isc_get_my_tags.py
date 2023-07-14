import boto3

import botocore.session

# Create a Botocore session
session = botocore.session.Session()

# Get the default profile name from the session
default_profile = session.get_config_variable('profile')

# Print the default profile
print("Default AWS Profile:", default_profile)

# Create a session using your AWS credentials
session = boto3.Session()

# Create an IAM client using the session
iam_client = session.client('iam')

# Get the current IAM user
user = iam_client.get_user()

# Extract the user's ARN
username = user['User']['UserName']

# Get the tags applied to the user
response = iam_client.list_user_tags(UserName=username)

# Extract the tags from the response
tags = response['Tags']

import re
assumable_roles=[]


from os.path import expanduser
home = expanduser("~")

profiles_for_append=''

with open(home+'/.aws/config') as aws_config:
    all_lines=aws_config.readlines()
    for tag in tags:
        try:
            match_re=re.search(r'(.*)_([0-9]+)_(.*)',tag['Key'])
            account_name=match_re.group(1)
            account_id=match_re.group(2)
            role_id=match_re.group(3)

            profile_generation=f"{default_profile}_{account_name}_{account_id}_{role_id}"
            profile_line=f'[profile {profile_generation}]'
            source_profile_line=f'source_profile={default_profile}'
            role_arn_line=f'role_arn=arn:aws:iam::{account_id}:role/{role_id}'
            exists=False
            for line in all_lines:
                if profile_line in line:
                    exists=True
                    break
            if not exists:
                profiles_for_append+=f"{profile_line}\n{source_profile_line}\n{role_arn_line}\n##DURATION##\n##MFA##\n\n"
        except:
            continue

if profiles_for_append != '':
    default_duration=''
    valid=False
    while not valid:
        default_duration=input('There are profiles that will be imported. What should be the default token duration(in hours)? ')
        try:
            default_duration=int(default_duration)*60*60
        except Exception as ex:
            print("Wrong input. It should be an int.")
        if isinstance(default_duration, int):
            valid=True
    profiles_for_append=profiles_for_append.replace('##DURATION##',f'duration_seconds = {default_duration}')

    mfas= iam_client.list_mfa_devices(
        UserName=username
    )['MFADevices']
    mfa_serial=''
    if len(mfas)==1:
        mfa_serial=mfas[0]['SerialNumber']
    else:
        print("List of mfa devices:")
        ind=0
        for mfa in mfas:
            print(f'{ind} ',mfa['SerialNumber'])
        chosen_index=int(input('Choose your index:'))
        mfa_serial=mfas[chosen_index]['SerialNumber']
    profiles_for_append=profiles_for_append.replace('##MFA##',f'mfa_serial = {mfa_serial}')

with open(home+'/.aws/config','a') as f:
    f.write(f"\n\n{profiles_for_append}")





