print('Welcome to Sgt Walker - The Texas (Holdem Starting Hand) Ranger')

with open('hand_data.csv') as walker_input:
    walker_data = {}
    for line in walker_input:
        walker_data[line.split(',')[0]] = line.split(',')[1:]

player_hand = input('Hand> ')

while player_hand != 'q':
    if len(player_hand) == 2:
        player_hand = player_hand.upper()
    if len(player_hand) == 3:
        player_hand = player_hand[:2].upper() + player_hand[2].lower()
    if player_hand in walker_data.keys():
        opt_moves = walker_data[player_hand]
        pos_names = walker_data['hand']
        pad = len(max(opt_moves + pos_names, key=len))
        pad_mve = [i.strip().ljust(pad + 1, ' ') for i in opt_moves]
        pad_pos = [i.strip().ljust(pad + 1, ' ') for i in pos_names]
        print(f'{player_hand}:')
        print(f'{''.join(pad_pos[:8])}\n{''.join(pad_mve[:8])}\n')
        print(f'{''.join(pad_pos[9:17])}\n{''.join(pad_mve[9:17])}\n')
        print(f'{''.join(pad_pos[18:26])}\n{''.join(pad_mve[18:26])}\n')
        print(f'{''.join(pad_pos[27:35])}\n{''.join(pad_mve[27:35])}\n')
    player_hand = input('Hand> ')
