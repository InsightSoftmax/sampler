# # Get the tags applied to the user
# response = iam_client.list_user_tags(UserName=username)

# # Extract the tags from the response
# tags = response['Tags']

import re
import sys


role_profile=sys.argv[1]

# Print the tags
assumable_roles=[]

from os.path import expanduser
home = expanduser("~")

profiles_for_append='\n\n'

roles=[]

pattern_to_change=''
all_text=''
with open(home+'/.aws/config') as aws_config:
    all_text=aws_config.read()

    match_re=re.search(role_profile+r'](.|\n)+?duration_seconds = (\d+)',all_text)
    #print(match_re)
    textual_match=match_re.group(0)
    pattern_to_change=textual_match
    token_time=match_re.group(2)
    #string_match=role_profile+']'+before_match+token_time
    #print(token_time)
    old_duration=int(token_time)/3600
    new_duration=0
    valid=False
    while not valid:
        new_duration=input(f'What should be the default token duration(in hours)? [{int(old_duration)}] ')
        if new_duration=='':
            break
        try:
            new_duration=int(new_duration)
        except Exception as ex:
            print("Wrong input. It should be an int.")
        if isinstance(new_duration, int):
            valid=True

if new_duration!='':
    with open(home+'/.aws/config','w') as aws_config:
        new_pattern_to_change=pattern_to_change.replace(f'duration_seconds = '+str(int(old_duration*3600)),'duration_seconds = '+str(int(new_duration*3600)))
        all_text=all_text.replace(pattern_to_change,new_pattern_to_change)
        aws_config.write(all_text)




