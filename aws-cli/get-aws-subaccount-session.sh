#!/bin/bash

## script: ISC AWS Subaccount Session Loader
## description: use this to establish an aws cli session to a subaccount using role assumption (switching roles). make sure to have your base aws cli setup with keys/secrets pointed at your primary login account
##
## make sure to use the sourcing "." in the script execution. otherwise, your session won't slurp the env vars created by the script.
## if you're using automated mfa input entry via option 2 down below, make sure to place the file /${HOME}/.aws/mfa/isc-login_totp in your local system. the file should be your aws mfa secret token text string, a 1 line file, with no empty lines after it
##
## usage: $ chmod +x ./get-aws-subaccount-session.sh
## usage: $ . ./get-aws-subaccount-session.sh

## general

app_title="** ISC AWS Subaccount Session Loader **"
app_subtitle="** Establish an AWS CLI session with MFA to an AWS subaccount using role assumption **"



## init

#### time

script_start_timestamp=$(date --iso-8601=seconds)

#### system

DEBIAN_FRONTEND=noninteractive

#### colors

cyan='\033[0;96m'
blue='\033[0;94m'
reset='\033[0m'

#### title

echo
echo -e "${cyan}${app_title}${reset}"
echo -e "${cyan}${app_subtitle}${reset}"
echo -e "${cyan}${app_disclaimer}${reset}"
echo



## import aws cli configs

echo Loading AWS CLI configs...
echo

#### alter the values below to your target subaccount and target role as needed ## 

export AWS_PROFILE=default
export aws_target_subaccount_name=gross-eng-dev
export aws_target_subaccount_id=235758441054
export aws_target_subaccount_role=isc-login_assumed-role_eng_power-users
export aws_target_subaccount_session_seconds=3600

##################################################################################

echo AWS CLI configs loaded.
echo



## preflight checks

echo Performing preflight checks...
echo

#### check env vars

if [[ -z ${AWS_PROFILE} ]]; then
  echo "Please set your AWS_PROFILE environment variable (\"default\" is fine)."
  return
fi
if [[ -z ${aws_target_subaccount_name} ]]; then
  echo "Please set your aws_target_subaccount_name environment variable."
  return
fi
if [[ -z ${aws_target_subaccount_id} ]]; then
  echo "Please set your aws_target_subaccount_id environment variable."
  return
fi
if [[ -z ${aws_target_subaccount_role} ]]; then
  echo "Please set the aws_target_subaccount_role environment variable."
  return
fi
if [[ -z ${aws_target_subaccount_session_seconds} ]]; then
  echo "Please set the aws_target_subaccount_session_seconds environment variable."
  return
fi

#### wipe previous terminal env vars set by this utility

if [ -n "${AWS_SESSION_TOKEN}" ]
then
  echo "Previous session token found. Deleting..."
  unset AWS_SESSION_TOKEN
fi
if [ -n "${AWS_SECRET_ACCESS_KEY}" ]
then
  echo "Previous session access key. Deleting..."
  unset AWS_SECRET_ACCESS_KEY
fi
if [ -n "${AWS_ACCESS_KEY_ID}" ]
then
  echo "Previous session access key id. Deleting..."
  unset AWS_ACCESS_KEY_ID
fi
echo

echo All preflight checks have cleared.
echo



## main

#### this content is sourced from https://github.com/sweharris/aws-cli-mfa/blob/master/get-aws-creds and has been modified a bit ##

# This uses MFA devices to get temporary (eg 12 hour) credentials.  Requires
# a TTY for user input.
#
# GPL 2 or higher

if [ ! -t 0 ]
then
  echo Must be on a tty >&2
  return
fi

if [ -n "$AWS_SESSION_TOKEN" ]
then
  echo "Session token found.  This can not be used to generate a new token.
   unset AWS_SESSION_TOKEN AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID
and then ensure you have a profile with the normal access key credentials or
set the variables to the normal keys.
" >&2
  return
fi

identity=$(aws sts get-caller-identity)
username=$(echo -- "$identity" | sed -n 's!.*"arn:aws:iam::.*:user/\(.*\)".*!\1!p')
if [ -z "$username" ]
then
  echo "Can not identify who you are.  Looking for a line like
    arn:aws:iam::.....:user/FOO_BAR
but did not find one in the output of
  aws sts get-caller-identity
$identity" >&2
  return
fi

echo -e "You are: ${blue}${username}${reset}" >&2

mfa=$(aws iam list-mfa-devices --user-name "$username")
device=$(echo -- "$mfa" | sed -n 's!.*"SerialNumber": "\(.*\)".*!\1!p')
if [ -z "$device" ]
then
  echo "Can not find any MFA device for you.  Looking for a SerialNumber
but did not find one in the output of
  aws iam list-mfa-devices --username \"$username\"
$mfa" >&2
  return
fi

echo -e "Your MFA device is: ${blue}${device}${reset}" >&2

## option 1: manual mfa token entry 
# echo -ne "Enter your MFA code now: ${blue}" >&2
# read code
# echo -e "${reset}" >&2

## option 2: automated mfa token entry
echo -ne "Automating MFA input... ${blue}" >&2
totp=$(cat /${HOME}/.aws/mfa/isc-login_totp)
code=$(oathtool -b --totp ${totp})
echo -e "${reset}" >&2
echo

tokens=$(aws sts get-session-token --serial-number "$device" --token-code $code)

secret=$(echo -- "$tokens" | sed -n 's!.*"SecretAccessKey": "\(.*\)".*!\1!p')
session=$(echo -- "$tokens" | sed -n 's!.*"SessionToken": "\(.*\)".*!\1!p')
access=$(echo -- "$tokens" | sed -n 's!.*"AccessKeyId": "\(.*\)".*!\1!p')
expire=$(echo -- "$tokens" | sed -n 's!.*"Expiration": "\(.*\)".*!\1!p')

if [ -z "$secret" -o -z "$session" -o -z "$access" ]
then
  echo "Unable to get temporary credentials.  Could not find secret/access/session entries
$tokens" >&2
  return
fi

echo Keys valid until $expire >&2

export AWS_PROFILE=$AWS_PROFILE
export AWS_SESSION_TOKEN=$session
export AWS_SECRET_ACCESS_KEY=$secret
export AWS_ACCESS_KEY_ID=$access

###################################################################################################################################

export $(printf "AWS_ACCESS_KEY_ID=%s AWS_SECRET_ACCESS_KEY=%s AWS_SESSION_TOKEN=%s" \
  $(aws sts assume-role \
  --role-arn arn:aws:iam::${aws_target_subaccount_id}:role/${aws_target_subaccount_role} \
  --role-session-name my-session-role \
  --query "Credentials.[AccessKeyId,SecretAccessKey,SessionToken]" \
  --output text \
  --duration-seconds ${aws_target_subaccount_session_seconds}) \
  )

echo -e "Role ${blue}${aws_target_subaccount_role}${reset} session established to account ${blue}${aws_target_subaccount_name}${reset}" >&2
echo -e "Session duraction set to ${blue}${aws_target_subaccount_session_seconds}${reset} seconds" >&2
echo
