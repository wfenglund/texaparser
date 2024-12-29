player='GoldKruger'
hh_dir='/home/william/.wine/drive_c/users/william/AppData/Local/PokerStars.SE/HandHistory/GoldKruger'
hh_fle=`ls -t $hh_dir | head -n 1`

# Parse previous hand histories (comment out if undesirable):
python texaprimer.py "$hh_dir" "$hh_fle"

while true
do
	clear
	python texaparser.py "$player" "$hh_dir" "$hh_fle" | column -t -s ','
	sleep 10
done
