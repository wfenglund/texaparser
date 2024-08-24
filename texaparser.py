import sys
import os
import re

# Get hand history path and file:
player_name = sys.argv[1]
hand_history_path = sys.argv[2]
hand_history_file = hand_history_path + '/' + sys.argv[3]

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

# Color number function:
def col_num(number, target = 'low'):
    if target == 'low':
        if number > 0.75:
            number = str(number)
            return '\x1b[0;31;40m' + number + '\x1b[0m'
        elif number > 0.50:
            number = str(number)
            return '\x1b[0;33;40m' + number + '\x1b[0m'
        elif number > 0.25:
            number = str(number)
            return number
        else:
            number = str(number)
            return '\x1b[0;36;40m' + number + '\x1b[0m'
    else:
        if number < 0.25:
            number = str(number)
            return '\x1b[0;31;40m' + number + '\x1b[0m'
        elif number < 0.50:
            number = str(number)
            return '\x1b[0;33;40m' + number + '\x1b[0m'
        elif number < 0.75:
            number = str(number)
            return number
        else:
            number = str(number)
            return '\x1b[0;36;40m' + number + '\x1b[0m'

# Get players of last hand:
name_list = []
chip_list = []
small_blind = 1 # placeholder
big_blind = 1 # placeholder
for entry in hh_dict[hand]['prehand']:
    if entry.startswith('Plats'):
        name = re.sub(r'Plats [1-9]: ', '', entry)
        name = re.sub(r' \(.+ i marker\)', '', name)
        name = re.sub(r' står över', '', name)
        name = re.sub(r' ute ur handen \(flyttade från annat bord till small blind\)', '', name)
        name_list.append(name.strip())
        chip_count = re.sub(r'.+ \(', '', entry)
        chip_count = re.sub(r' i marker\).*', '', chip_count) # remove 'i marker' and more if the player is sitting it out
        chip_list.append(int(chip_count))
    elif 'lägger small blind' in entry:
        small_blind = int(re.sub(r'.+: lägger small blind ', '', entry)) # not used at the moment
    elif 'lägger big blind' in entry:
        big_blind = int(re.sub(r'.+: lägger big blind ', '', entry))
last_winner = [i for i in hh_dict[hand]['summary'] if ' vann ' in i]

# Sort players (put user first):
player_index = name_list.index(player_name)
name_list = name_list[player_index:] + name_list[:player_index]
chip_list = chip_list[player_index:] + chip_list[:player_index]

# Get hand inactivity and winrate:
activity_list = []
winrate_list = []
raise_list = []
for player in name_list:
    n_hand = 0
    n_fold = 0
    n_wins = 0
    n_rais = 0
    for h_info in hh_dict.values():
        if any([player in i for i in h_info['summary']]):
            n_hand = n_hand + 1
            if any([player in i and ('foldade innan Flopp (satsade inte)' in i or 'blind) foldade innan Flopp' in i) for i in h_info['summary']]):
                n_fold = n_fold + 1
            else:
                if any([player in i and 'vann' in i for i in h_info['summary']]):
                    n_wins = n_wins + 1
            # Count preflop raises:
            if player + ': raise ' in '\t'.join(h_info['preflop']):
                n_rais = n_rais + 1
    n_acti = n_hand - n_fold
    activity_list = activity_list + [col_num(round(n_acti / n_hand, 2)) + ' (' + str(n_acti) + '/' + str(n_hand) + ')'] if n_hand > 0 else activity_list + [str(0.0) + ' (0/0)']
    winrate_list = winrate_list + [col_num(round(n_wins / n_acti, 2), 'high') + ' (' + str(n_wins) + '/' + str(n_acti) + ')'] if n_acti > 0 else winrate_list + [str(0.0) + ' (0/0)']
    raise_list = raise_list + [col_num(round(n_rais / n_acti, 2), 'high') + ' (' + str(n_rais) + '/' + str(n_acti) + ')'] if n_acti > 0 else raise_list + [str(0.0) + ' (0/0)']

# Print output:
name_list = [i.replace(player_name, "\x1b[4;34;40m" + player_name + "\x1b[0m") for i in name_list]
name_list = [i.replace(',', '.') for i in name_list]
primed_names = [i + ' (' + str(round(chip_list[name_list.index(i)] / big_blind, 1)) + 'BB)' for i in name_list]
print(','.join(['  Player: '] + primed_names))
print(','.join(['  Active:'] + activity_list))
print(','.join([' Winrate:'] + winrate_list))
print(','.join(['Prefl RR:'] + raise_list))
# print(',,,,,,,,,,' + last_winner[0]) # print last hands winner

# Ideas:
# flop  bets
# turn bets
# river bets
