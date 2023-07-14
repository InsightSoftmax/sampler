current_wd=$(pwd)/.
current_directory=$(basename "$current_wd")
sudo cp -a -r $current_wd /usr/bin/
