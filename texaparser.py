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
aggr_list = []
winrate_list = []
raise_list = []
ffold_list = []
fbets_list = []
vpip_list = []
for player in name_list:
    n_hand = 0 # hands played
    n_fold = 0 # hands folded preflop
    n_call = 0 # number of calls
    n_rais = 0 # number of raises
    n_bets = 0 # number of bets
    n_wins = 0 # played hands won
    n_pfrs = 0 # hands raised before flop
    n_flop = 0 # flops seen
    n_pofo = 0 # hands folded on flop
    n_chks = 0 # hands checked on flop
    n_flbt = 0 # hands bet on flop
    n_walk = 0 # number of wins uncontested
    n_vpip = 0 # number of times money was put in pot
    for h_info in hh_dict.values():
        # Initiate temporary counters:
        hand_call = 0
        hand_rais = 0
        hand_bets = 0
        # If player in hand:
        if any([player in i for i in h_info['summary']]):
            # Count hand:
            n_hand = n_hand + 1
            # Count hands folded without bets:
            if any([player in i and ('foldade innan Flopp (satsade inte)' in i or 'blind) foldade innan Flopp' in i) for i in h_info['summary']]):
                n_fold = n_fold + 1
            # Count wins:
            if any([player in i and 'vann' in i for i in h_info['summary']]):
                n_wins = n_wins + 1
            # Count total preflop calls and raises:
            hand_call = sum([1 for i in h_info['preflop'] if player + ': call ' in i])
            hand_rais = sum([1 for i in h_info['preflop'] if player + ': raise ' in i])
            # Count preflops raised:
            if hand_rais > 0: # if flop was waised at least once
                n_pfrs = n_pfrs + 1
            # Count flops:
            if 'flop' in h_info.keys():
                # Flatten flop list to increase effectiveness of later checks
                flat_flop = '\t'.join(h_info['flop'])
                if player in flat_flop:
                    n_flop = n_flop + 1
                    # Count flops folded:
                    if player + ': fold' in flat_flop:
                        n_pofo = n_pofo + 1
                    # Count flops checked on:
                    elif player + ': check' in flat_flop:
                        n_chks = n_chks + 1
                    # Count flops bet on:
                    elif player + ': bet ' in flat_flop:
                        n_flbt = n_flbt + 1
                    # Count total flop calls, bets and raises:
                    hand_call = sum([1 for i in h_info['flop'] if player + ': call ' in i]) + hand_call
                    hand_bets = sum([1 for i in h_info['flop'] if player + ': bet ' in i]) + hand_bets
                    hand_rais = sum([1 for i in h_info['flop'] if player + ': raise ' in i]) + hand_rais
                    if 'turn' in h_info.keys():
                        # Count total turn calls:
                        hand_call = sum([1 for i in h_info['turn'] if player + ': call ' in i]) + hand_call
                        hand_bets = sum([1 for i in h_info['turn'] if player + ': bet ' in i]) + hand_bets
                        hand_rais = sum([1 for i in h_info['turn'] if player + ': raise ' in i]) + hand_rais
                        if 'river' in h_info.keys():
                            # Count total river calls:
                            hand_call = sum([1 for i in h_info['river'] if player + ': call ' in i]) + hand_call
                            hand_bets = sum([1 for i in h_info['river'] if player + ': bet ' in i]) + hand_bets
                            hand_rais = sum([1 for i in h_info['river'] if player + ': raise ' in i]) + hand_rais
            else: # if no flop
                # Check if pot was won uncontested as big blind:
                walk_bools = []
                for entry in h_info['summary']:
                    if entry.startswith('Plats') and player not in entry:
                        walk_bools = walk_bools + [('foldade innan Flopp (satsade inte)' in entry) or ('blind) foldade innan Flopp' in entry)]
                    elif player in entry:
                        walk_bools = walk_bools + [player + ' (big blind)' in entry]
                if all(walk_bools):
                    n_walk = n_walk + 1
                    n_wins = n_wins - 1 # remove win since it is a walk
            # Check if money was put into pot voluntarily:
            if (hand_call + hand_rais + hand_bets) > 0:
                n_vpip = n_vpip + 1
            # Add temporary counts to player counts:
            n_call = n_call + hand_call
            n_rais = n_rais + hand_rais
            n_bets = n_bets + hand_bets

    # Calculate vpip:
    n_actual = n_hand - n_walk # number of hands not won on walk
    vpip_list = vpip_list + [col_num(round(n_vpip / n_actual, 2)) + ' (' + str(n_vpip) + '/' + str(n_actual) + ')'] if n_actual > 0 else vpip_list + [str(0.0) + ' (0/0)']
    # Calculate aggression:
    n_aggr = n_bets + n_rais
    aggr_list = aggr_list + [col_num(round(n_aggr / n_call, 2)) + ' (' + str(n_aggr) + '/' + str(n_call) + ')'] if n_call > 0 else aggr_list + [str(0.0) + ' (0/0)']
    # Calculate winrate:
    # wins / (hands -walks -folds)
    n_active = n_actual - n_fold # number of hands not folded and not won on walk
    winrate_list = winrate_list + [col_num(round(n_wins / n_active, 2), 'high') + ' (' + str(n_wins) + '/' + str(n_active) + ')'] if n_active > 0 else winrate_list + [str(0.0) + ' (0/0)']
    # Calculate how many preflops were raised (rather than checked or limped):
    # raises / (hands -walks -folds)
    raise_list = raise_list + [col_num(round(n_pfrs / n_active, 2), 'high') + ' (' + str(n_pfrs) + '/' + str(n_active) + ')'] if n_active > 0 else raise_list + [str(0.0) + ' (0/0)']
    # Calculate how many flops were folded when the choice was given:
    ffold_list = ffold_list + [col_num(round(n_pofo / n_flop, 2), 'low') + ' (' + str(n_pofo) + '/' + str(n_flop) + ')'] if n_flop > 0 else ffold_list + [str(0.0) + ' (0/0)']
    # Calculate how many flops were bet on when the choice was given:
    n_btab = n_chks + n_flbt # number of flops which could have been bet on
    fbets_list = fbets_list + [col_num(round(n_flbt / n_btab, 2), 'high') + ' (' + str(n_flbt) + '/' + str(n_btab) + ')'] if n_btab > 0 else fbets_list + [str(0.0) + ' (0/0)']

# Print output:
name_list = [i.replace(player_name, "\x1b[4;34;40m" + player_name + "\x1b[0m") for i in name_list]
name_list = [i.replace(',', '.') for i in name_list]
primed_names = [i + ' (' + str(round(chip_list[name_list.index(i)] / big_blind, 1)) + 'BB)' for i in name_list]
print(','.join([' Player:'] + primed_names))
# print(','.join([' Active:'] + activity_list))
print(','.join(['  VP$IP:'] + vpip_list))
print(','.join(['  Aggro:'] + aggr_list))
print(','.join(['Winrate:'] + winrate_list))
print(','.join(['Prfl RR:'] + raise_list))
print(','.join(['Pofl FR:'] + ffold_list))
print(','.join(['Pofl BR:'] + fbets_list))
# print(',,,,,,,,,,' + last_winner[0]) # print last hands winner
