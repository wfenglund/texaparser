import os
import re

# Get hand history path:
hand_history_dir = '/home/william/.wine/drive_c/users/william/AppData/Local/PokerStars.SE/HandHistory/GoldKruger'
hand_history_file = hand_history_dir + '/' + os.listdir(hand_history_dir)[-1]

# Parse hand history data:
hh_dict = {}
hand = ''
state = ''

with open(hand_history_file) as hh_file:
    for row in hh_file:
        row = row.strip()
        if 'PokerStars hand nr' in row:
            hand = row
            hh_dict[hand] = {}
            state = 'prehand'
            hh_dict[hand][state] = []
        elif row.startswith('*** HÅLKORT ***'):
            state = 'preflop'
            hh_dict[hand][state] = []
        elif row.startswith('*** FLOPP ***'):
            state = 'flop'
            hh_dict[hand][state] = []
        elif row.startswith('*** TURN ***'):
            state = 'turn'
            hh_dict[hand][state] = []
        elif row.startswith('*** RIVER ***'):
            state = 'river'
            hh_dict[hand][state] = []
        elif row.startswith('*** VISNING ***'):
            state = 'showdown'
            hh_dict[hand][state] = []
        elif row.startswith('*** SAMMANFATTNING ***'):
            state = 'summary'
            hh_dict[hand][state] = []
        elif hand in hh_dict.keys():
            hh_dict[hand][state] = hh_dict[hand][state] + [row]

# Get players of last hand:
name_list = []
for entry in hh_dict[hand]['prehand']:
    if entry.startswith('Plats'):
        name = re.sub(r'Plats [1-9]: ', '', entry)
#         name = re.sub(r' \([1-9]+ i marker\)', '', name)
        name = re.sub(r' \(.+ i marker\)', '', name)
        name = re.sub(r' står över', '', name)
        name = re.sub(r' ute ur handen \(flyttade från annat bord till small blind\)', '', name)
        name_list.append(name.strip())

# Get hand inactivity and winrate:
activity_list = []
winrate_list = []
for player in name_list:
    n_hand = 0
    n_fold = 0
    n_wins = 0
    for h_info in hh_dict.values():
        if any([player in i for i in h_info['summary']]):
            n_hand = n_hand + 1
            if any([player in i and ('foldade innan Flopp (satsade inte)' in i or 'blind) foldade innan Flopp' in i) for i in h_info['summary']]):
                n_fold = n_fold + 1
            else:
                if any([player in i and 'vann' in i for i in h_info['summary']]):
                    n_wins = n_wins + 1
    n_acti = n_hand - n_fold
    activity_list = activity_list + [str(round(n_acti / n_hand, 2)) + ' (' + str(n_acti) + '/' + str(n_hand) + ')'] if n_hand > 0 else activity_list + [str(0.0) + ' (0/0)']
    winrate_list = winrate_list + [str(round(n_wins / n_acti, 2)) + ' (' + str(n_wins) + '/' + str(n_acti) + ')'] if n_acti > 0 else winrate_list + [str(0.0) + ' (0/0)']


# Print output:
print(','.join([' Player: '] + name_list))
print(','.join([' Active:'] + activity_list))
print(','.join(['Winrate:'] + winrate_list))

# Ideas:
# preflop bets
# flop  bets
# turn bets
# river bets
