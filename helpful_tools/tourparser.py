import os
import re

tourn_hist_dir = '/home/william/.wine/drive_c/users/william/AppData/Local/PokerStars.SE/TournSummary/GoldKruger/'
tourn_filt = ''
player = 'GoldKruger'

tourn_list = os.listdir(tourn_hist_dir)
tourn_list_filt = [i for i in tourn_list if tourn_filt in i]

tourn_dict = {}
for tourn in tourn_list_filt:
    counter = 0
    with open(tourn_hist_dir + '/' + tourn) as cur_tourn:
        for line in cur_tourn:
            if line.strip() == 'Supersatellit':
                continue
            counter = counter + 1
            if counter == 2:
                tourn_name = line.strip()
                cost_raw = re.sub(r'.+: \$', '', tourn_name)
                cost_list = re.sub(r' .+', '', cost_raw).split('/$')
                cost = sum([float(i) for i in cost_list])
            elif counter == 3:
                tourn_name = tourn_name + ' ' + line.strip()
                if tourn_name not in tourn_dict.keys():
                    tourn_dict[tourn_name] = [cost, 1, 0, 0] # cost, number played, ITM placements, total winnings
                else:
                    tourn_dict[tourn_name][1] = tourn_dict[tourn_name][1] + 1
            if player in line and '$' in line:
                prize_raw = re.sub(r'.+\$', '', line)
                prize_string = re.sub(r' \(.+', '', prize_raw)
                prize_float = float(prize_string.replace(',', '.'))
                tourn_dict[tourn_name][2] = tourn_dict[tourn_name][2] + 1
                tourn_dict[tourn_name][3] = tourn_dict[tourn_name][3] + prize_float

for tournament in tourn_dict.keys():
    tourn_stats = tourn_dict[tournament]
    print(tournament + ':')
    print(f'Number played: {tourn_stats[1]}, ITM: {tourn_stats[2]}, Ratio: {round(tourn_stats[2] / tourn_stats[1], 3)}.')
    total_cost = tourn_stats[0] * tourn_stats[1]
    print(f'Spent: {round(total_cost, 3)}, Winnings: {round(tourn_stats[3], 3)}, Ratio: {round(tourn_stats[3] / total_cost, 3)}.')
    print()

