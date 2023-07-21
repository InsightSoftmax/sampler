# # Get the tags applied to the user
# response = iam_client.list_user_tags(UserName=username)

# # Extract the tags from the response
# tags = response['Tags']

import re
import sys


base_profile=sys.argv[1]

# Print the tags
assumable_roles=[]

from os.path import expanduser
home = expanduser("~")

profiles_for_append='\n\n'

roles=[]
with open(home+'/.aws/config') as aws_config:
    all_lines=aws_config.readlines()
    for line in all_lines:
        match_re=re.search(r'\[(.*)\]',line)
        try:
            profile=match_re.group(1)
            #print(profile,"  ",f"profile isc_{base_profile}_")
            if profile.startswith(f"profile isc_{base_profile}_"):
                roles.append(profile.split(" ")[1])
        except Exception as ex:
            continue
    print('\n'.join(roles))

    




