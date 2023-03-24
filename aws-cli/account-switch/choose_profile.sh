profiles=$(aws configure list-profiles)

set -o noglob         # See special Note, below.
IFS=$'\n' profiles_br=($profiles)
set +o noglob
select profile in "${profiles_br[@]}"; do
    echo "You have chosen $profile"
    export AWS_PROFILE=$profile
    break
done