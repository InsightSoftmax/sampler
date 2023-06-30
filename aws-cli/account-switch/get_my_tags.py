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
print(user['User'])
# Extract the user's ARN
username = user['User']['UserName']





# Get the tags applied to the user
response = iam_client.list_user_tags(UserName=username)

# Extract the tags from the response
tags = response['Tags']

import re

# Print the tags
assumable_roles=[]


from os.path import expanduser
home = expanduser("~")

profiles_for_append='\n\n'

with open(home+'/.aws/config') as aws_config:
    all_lines=aws_config.readlines()
    for tag in tags:
        print(f"Key: {tag['Key']}, Value: {tag['Value']}")
        match_re=re.search(r'(.*)_([0-9]+)_(.*)',tag['Key'])
        account_name=match_re.group(1)
        account_id=match_re.group(2)
        role_id=match_re.group(3)

        profile_generation=f"{default_profile}_{account_name}_{account_id}_{role_id}"
        profile_line=f'[profile {profile_generation}]'
        source_profile_line=f'source_profile={default_profile}'
        role_arn_line=f'role_arn=arn:aws:iam::{account_id}:role/{role_id}'
        print(all_lines[82])
        exists=False
        for line in all_lines:
            if profile_line in line:
                exists=True
                break
        if not exists:
            profiles_for_append+=f"{profile_line}\n{source_profile_line}\n{role_arn_line}\n##MFA##\n\n"
        print(profile_line)


print(profiles_for_append)
if profiles_for_append != '':
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
    #print(mfa_serial)
    profiles_for_append=profiles_for_append.replace('##MFA##',f'mfa_serial = {mfa_serial}')
print(profiles_for_append)    

with open(home+'/.aws/config','a') as f:
    f.write(profiles_for_append)





