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
        name = re.sub(r' \(.+ i marker.*', '', name)
        name = re.sub(r' står över', '', name)
        name = re.sub(r' ute ur handen \(flyttade från annat bord till small blind\)', '', name)
        name_list.append(name.strip())
        chip_count = re.sub(r'.+ \(', '', entry)
        chip_count = re.sub(r' i marker.*', '', chip_count) # remove 'i marker' and more if the player is sitting it out
        chip_list.append(float(chip_count.replace('$', '')))
    elif 'lägger small blind' in entry:
        small_blind = float(re.sub(r'.+: lägger small blind ', '', entry).replace(' och är all-in', '').replace('$', '')) # not used at the moment
    elif 'lägger big blind' in entry:
        big_blind = float(re.sub(r'.+: lägger big blind ', '', entry).replace(' och är all-in', '').replace('$', ''))
last_winner = [i for i in hh_dict[hand]['summary'] if ' vann ' in i]

# Sort players (put user first):
player_index = name_list.index(player_name)
name_list = name_list[player_index:] + name_list[:player_index]
chip_list = chip_list[player_index:] + chip_list[:player_index]

# Get hand inactivity and winrate:
activity_list = []
winrate_list = []
raise_list = []
ffold_list = []
fbets_list = []
for player in name_list:
    n_hand = 0 # hands played
    n_muck = 0 # hands thrown before flop
    n_wins = 0 # played hands won
    n_rais = 0 # hands raised before flop
    n_flop = 0 # flops seen
    n_fold = 0 # hands folded on flop
    n_chks = 0 # hands checked on flop
    n_bets = 0 # hands bet on flop
    for h_info in hh_dict.values():
        # If player in hand:
        if any([player in i for i in h_info['summary']]):
            # Count hand:
            n_hand = n_hand + 1
            # Count mucks:
            if any([player in i and ('foldade innan Flopp (satsade inte)' in i or 'blind) foldade innan Flopp' in i) for i in h_info['summary']]):
                n_muck = n_muck + 1
            else:
                # Count wins:
                if any([player in i and 'vann' in i for i in h_info['summary']]):
                    n_wins = n_wins + 1
            # Count preflop raises:
            if player + ': raise ' in '\t'.join(h_info['preflop']):
                n_rais = n_rais + 1
            # Count flops:
            if 'flop' in h_info.keys() and player in '\t'.join(h_info['flop']):
                n_flop = n_flop + 1
                # Count flops folded:
                if player + ': fold' in '\t'.join(h_info['flop']):
                    n_fold = n_fold + 1
                # Count flops checked on:
                elif player + ': check' in '\t'.join(h_info['flop']):
                    n_chks = n_chks + 1
                # Count flops bet on:
                elif player + ': bet ' in '\t'.join(h_info['flop']):
                    n_bets = n_bets + 1
    n_acti = n_hand - n_muck
    activity_list = activity_list + [col_num(round(n_acti / n_hand, 2)) + ' (' + str(n_acti) + '/' + str(n_hand) + ')'] if n_hand > 0 else activity_list + [str(0.0) + ' (0/0)']
    winrate_list = winrate_list + [col_num(round(n_wins / n_acti, 2), 'high') + ' (' + str(n_wins) + '/' + str(n_acti) + ')'] if n_acti > 0 else winrate_list + [str(0.0) + ' (0/0)']
    raise_list = raise_list + [col_num(round(n_rais / n_acti, 2), 'high') + ' (' + str(n_rais) + '/' + str(n_acti) + ')'] if n_acti > 0 else raise_list + [str(0.0) + ' (0/0)']
    ffold_list = ffold_list + [col_num(round(n_fold / n_flop, 2), 'low') + ' (' + str(n_fold) + '/' + str(n_flop) + ')'] if n_flop > 0 else ffold_list + [str(0.0) + ' (0/0)']
    n_btab = n_chks + n_bets # number of flops which could have been bet on
    fbets_list = fbets_list + [col_num(round(n_bets / n_btab, 2), 'high') + ' (' + str(n_bets) + '/' + str(n_btab) + ')'] if n_btab > 0 else fbets_list + [str(0.0) + ' (0/0)']

# Print output:
name_list = [i.replace(player_name, "\x1b[4;34;40m" + player_name + "\x1b[0m") for i in name_list]
name_list = [i.replace(',', '.') for i in name_list]
primed_names = [i + ' (' + str(round(chip_list[name_list.index(i)] / big_blind, 1)) + 'BB)' for i in name_list]
print(','.join([' Player: '] + primed_names))
print(','.join([' Active:'] + activity_list))
print(','.join(['Winrate:'] + winrate_list))
print(','.join(['Prfl RR:'] + raise_list))
print(','.join(['Pofl FR:'] + ffold_list))
print(','.join(['Pofl BR:'] + fbets_list))
# print(',,,,,,,,,,' + last_winner[0]) # print last hands winner

# Ideas:
# flop  bets
# turn bets
# river bets
