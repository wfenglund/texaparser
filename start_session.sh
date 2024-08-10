hh_dir='/home/william/.wine/drive_c/users/william/AppData/Local/PokerStars.SE/HandHistory/GoldKruger'
hh_fle=`ls $hh_dir | tail -n 1`

while true
do
	clear
	python texaparser.py "$hh_dir" "$hh_fle" | column -t -s ','
	sleep 10
done
