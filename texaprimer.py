import sys
import os
import json

# Get hand history path and file names:
hand_history_path = sys.argv[1]
current_tournament = sys.argv[2]
filter_term = '' if len(sys.argv) == 3 else sys.argv[3]
hh_file_list = os.listdir(hand_history_path)

# Remove current tournament from hh_file_list:
hh_file_list = [i for i in hh_file_list if i != current_tournament]

# Sift out desired tournaments:
hh_file_list = [j for j in hh_file_list if filter_term in j]

# Parse hand history data:
hh_dict = {}
hand = ''
state = ''

for current_file in hh_file_list:
    with open(hand_history_path + '/' + current_file) as hh_file:
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

# Write hand history data to json-format:
with open('.hand_history.json' , 'w') as hh_out:
    hh_out.write(json.dumps(hh_dict))
