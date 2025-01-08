player='GoldKruger'
hh_dir='/home/william/.wine/drive_c/users/william/AppData/Local/PokerStars.SE/HandHistory/GoldKruger'
hh_fle=`ls -t $hh_dir | head -n 1`

# Get current type of tournament for filtering:
lst_col=`echo $hh_fle | wc -w`
snd_lst=$((lst_col - 1))
thd_lst=$((lst_col - 2))
flt_trm=`echo $hh_fle | cut -d' ' -f$thd_lst,$snd_lst,$lst_col`

# Parse previous hand histories (comment out if undesirable):
python texaprimer.py "$hh_dir" "$hh_fle" "$flt_trm"

while true
do
	clear
	python texaparser.py "$player" "$hh_dir" "$hh_fle" | column -t -s ','
	echo ''
	echo 'Current tournament: '$hh_fle
	sleep 10
done
