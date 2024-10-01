hh_folder="/home/william/.wine/drive_c/users/william/AppData/Local/PokerStars.SE/HandHistory/GoldKruger/"

last_hh=`ls -t $hh_folder | head -1`
last_hh=${last_hh//" "/"\\ "}
last_hh=${last_hh//"$"/"\\$"}
full_path=$hh_folder${last_hh//"'"/"\\'"}

echo $full_path | xargs	cat
