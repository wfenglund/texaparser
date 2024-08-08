while true
do
	clear
	python texaparser.py | column -t -s ','
	sleep 10
done
