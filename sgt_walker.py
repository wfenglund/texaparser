print('Welcome to Sgt Walker - The Texas (Holdem Starting Hand) Ranger')

with open('walker_data.csv') as walker_input:
    counter = 0
    walker_data = {}
    for line in walker_input:
        if counter == 0:
            counter = 1
            continue
        else:
            walker_data[line.split('\t')[0]] = [line.split('\t')[1], line.split('\t')[2]]

player_pos = input('Position> ')

if player_pos in walker_data.keys():
    range_list = walker_data[player_pos][1].replace('"', '').split(';')
    if len(range_list) == 2:
        print(f'{player_pos}:\n{range_list[0]}\n{range_list[1]}')
    if len(range_list) == 3:
        print(f'{player_pos}:\n{range_list[0]}\n{range_list[1]}\n{range_list[2]}')
    if len(range_list) == 4:
        print(f'{player_pos}:\n{range_list[0]}\n{range_list[1]}\n{range_list[2]}\n{range_list[3]}')
