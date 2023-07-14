# # Get the tags applied to the user
# response = iam_client.list_user_tags(UserName=username)

# # Extract the tags from the response
# tags = response['Tags']

import re

# Print the tags
assumable_roles=[]

from os.path import expanduser
home = expanduser("~")

profiles_for_append='\n\n'

base_profiles=[]
with open(home+'/.aws/credentials') as aws_credentials:
    all_lines=aws_credentials.readlines()
    for line in all_lines:
        match_re=re.search(r'\[(.*)\]',line)
        try:
            profile=match_re.group(1)
            base_profiles.append(profile)
        except Exception as ex:
            continue
            #print(ex)
    base_profiles.append('None of the above (configure)')
    print('\n'.join(base_profiles))

    




