import re
import boto3
client=boto3.client('iam')

username='filip.novovic'
aws_config_path='/home/filip/.aws/'
managed_user_policies = client.list_attached_user_policies(UserName=username)
inline_user_policies = client.list_user_policies(UserName=username)
groups_call = client.list_groups_for_user(
    UserName=username
)



mfas= client.list_mfa_devices(
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

profile_id=0
groups=groups_call['Groups']
for group in groups:
    group_name=group['GroupName']
    group_policies = client.list_group_policies(
        GroupName=group_name
    )
    for group_policy in group_policies['PolicyNames']:
        group_policy_body = client.get_group_policy(
            GroupName=group_name,
            PolicyName=group_policy
        )
        for statement in group_policy_body["PolicyDocument"]["Statement"]:
            if "sts:AssumeRole" in statement["Action"] and statement["Effect"]=="Allow":
                print(statement)
                for role_arn in statement["Resource"]:
                    print(role_arn)
                    title_search = re.search("::(\d+):role\/(.*)", role_arn)
                    account_id=''
                    role_name=''
                    if title_search:
                        account_id=title_search.group(1).replace('-','_')
                        role_name=title_search.group(2).replace('-','_')
                    profile_template=f'''\n
[profile profile_{account_id}_{role_name}]
source_profile=default
role_arn={role_arn}
mfa_serial = {mfa_serial}'''
                    profile_id+=1
                    #print(profile_template)
                    with open(aws_config_path+'config', "a") as f:
                        f.write(profile_template)

        #print(group_policy_body)

