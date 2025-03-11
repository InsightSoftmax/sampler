# sampler
public infrastructure tools


## Overview

This repository provides a Bash script 
(`get-aws-subaccount-session.sh`) to establish 
an AWS CLI session with a subaccount using 
role assumption. It allows users to securely 
switch AWS accounts using MFA authentication, 
ensuring temporary access without storing 
permanent credentials.

The script:
* Assumes an IAM role in a subaccount using 
AWS STS.
* Requires MFA authentication to generate 
temporary session tokens.
* Supports manual or automated MFA entry 
(if a TOTP secret is stored).
* Ensures AWS credentials persist in the 
terminal session.

### Prerequisites

Before using this script, ensure that:
* You have AWS CLI installed and configured 
with your base account credentials.
* Your IAM user has permissions to assume 
a role in the subaccount.
* You have an MFA device registered for 
authentication.

### Usage
1. Make the Script Executable (Only Once)
```bash
chmod +x aws-cli/get-aws-subaccount-session.sh
```
2. Run the Script (Must Be Sourced)
```bash
. aws-cli/get-aws-subaccount-session.sh
```
Important: Using `.` (dot-space) ensures 
the session credentials persist in your terminal.

3. Enter MFA Code
When prompted, enter your MFA token to 
authenticate.

4. Verify the Session
After running the script, check if your AWS 
CLI session is active:
```bash
aws sts get-caller-identity
```
If successful, you should see the assumed
role and account ID.

#### Handling Session Expiration

AWS STS tokens expire after a set duration. 
If your session expires:
1. Unset the old session credentials:
```bash
unset AWS_SESSION_TOKEN AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID
```
2. Re-run the script to assume the role again:
```
. aws-cli/get-aws-subaccount-session.sh
```
#### Customization Options

You can modify the script to adjust the 
following settings:

* **Session duration:** Change the `aws_target_subaccount_session_seconds` variable 
to increase or decrease the session time 
(default is 3600 seconds).
* **Target AWS account:** Update 
`aws_target_subaccount_id` to switch to a 
different subaccount.
* **IAM Role:** Change `aws_target_subaccount_role` 
if your organization uses different role names.

These values can be found in the "AWS CLI Config Import" section inside the script.

#### Automated MFA Entry (Optional)

If you want to automate MFA token entry, save 
your MFA secret key in the file:
```bash
~/.aws/mfa/isc-login_totp
```
Then, modify the script to use oathtool for 
TOTP generation.

### Additional Notes
* AWS credentials are temporary and expire 
after the defined session duration.
* You can modify the target subaccount, role,
and session time inside the script.
* This script does not modify AWS CLI 
configuration files—it only sets temporary 
environment variables.
