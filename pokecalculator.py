import numpy as np

# load Pokemon base stats
baseStats = np.genfromtxt('gen_1_base_stats.txt', str, delimiter='\t', skip_header=2, usecols=1)
labels = baseStats   # pokemon
del baseStats

baseStats = np.genfromtxt('gen_1_base_stats.txt', delimiter='\t', skip_header=2, usecols=(2,3,4,5,6,7,0))
HP = baseStats[:, 0]       # HP
Atk = baseStats[:, 1]      # Attack
Def = baseStats[:, 2]      # Defense
SpAtk = baseStats[:, 3]    # Sp. Attack
SpDef = baseStats[:, 4]    # Sp. Defense
Spd = baseStats[:, 5]      # Speed
inds = baseStats[:, 6]     # indices of pokemon
del baseStats

# load CP multiplier
CPM = np.genfromtxt('cp_multiplier_by_level.txt', dtype=np.float32, delimiter='\t', skip_header=1)

# load Power Up Costs
costsByLevel = np.genfromtxt('cost_by_level.txt', dtype=np.uint16, delimiter='\t', skip_header=1)

###############################################################
# Info from Pokemon
label = 'Dratini1'     # str, name of pokemon
ind = 147            # int, # of pokemon, range 1-151
CP = 556              # int, current CP
user_HP = 56                # int, current max HP
CP_per_powerup = 2500  # int, stardust cost of a power up
powered = True           # False for not powered it up
###############################################################

if any(label in i for i in labels):
    ind = np.where(labels==label)[0][0]
    print '{:<16} {:<4} {:<8}'.format('Inquiry', ind+1, label)
elif ind < len(labels):
    label = labels[ind-1]
    print '{:<16} {:<4} {:<8}'.format('Inquiry', ind, label)
    ind -= 1
else:
    raise ValueError('Pokemon not found.')

print '{:<16} {:<16}'.format('CP', CP)
print '{:<16} {:<16}'.format('HP', user_HP)
print '{:<16} {:<16}'.format('Stardust Cost', CP_per_powerup)

# base values
baseAtk = 2 * np.around((Atk * SpAtk) ** .5 + Spd ** .5)  # Base Attack
baseDef = 2 * np.around((Def * SpDef) ** .5 + Spd ** .5)  # Base Defense
baseSta = 2 * HP                                          # Base Stamina

# Max CP
maxCP = (baseAtk + 15) * (baseDef + 15) ** .5 * (baseSta + 15) ** .5 * CPM[-1][-1] ** 2 /10  

maxCP_sorted = np.uint16(np.sort(maxCP)[::-1])
maxCP_sortedInd = np.argsort(-maxCP)
label_sorted = labels[maxCP_sortedInd]
ind_sorted = np.uint8(inds[maxCP_sortedInd])
BestPossibleCP = np.uint16(maxCP[ind])

def get_level(CP_per_powerup):
    cost_ind = np.where(costsByLevel==CP_per_powerup)[0]
    if len(cost_ind) == 0:
        raise ValueError('Invalid stardust cost of a power up.')
    possible_pokemonLevel = []
    CPMs = []
    for i in [0, .5, 1, 1.5]:
        pokemonLevel = costsByLevel[cost_ind, 0][0] + i
        if (pokemonLevel >= 1) & (pokemonLevel <= 40):
            possible_pokemonLevel.append(pokemonLevel)
            CPM_ind = np.where(CPM==costsByLevel[cost_ind, 0][0] + i)
            CPMs.append(CPM[CPM_ind,1][0][0]) 
    return zip(possible_pokemonLevel, CPMs)

def check_HP(HP, baseSta, indSta, cpm):
    calculated_HP = np.maximum(np.floor((baseSta + indSta) * cpm), 10)
    return calculated_HP == HP

def check_CP(CP, baseAtk, indAtk, baseDef, indDef, baseSta, indSta, cpm):
    Atk_temp = baseAtk + indAtk
    Def_temp = baseDef + indDef
    Sta_temp = baseSta + indSta
    calculated_CP = np.floor(Atk_temp * Def_temp ** .5 * Sta_temp ** .5 * cpm ** 2 / 10)
    return np.maximum(10, calculated_CP) == CP

def calculate_max_CP(baseAtk, indAtk, baseDef, indDef, baseSta, indSta, cpm):
    Atk_temp = baseAtk + indAtk
    Def_temp = baseDef + indDef
    Sta_temp = baseSta + indSta
    max_CP = Atk_temp * Def_temp ** .5 * Sta_temp ** .5 * cpm ** 2 / 10
    return max_CP

# IV calculation
possible_IV = []
for indSta in range(0, 16):
    for lv, cpm in get_level(CP_per_powerup):
        HP_check_result = check_HP(user_HP, baseSta[ind], indSta, cpm)
        if HP_check_result:
            for indAtk in range(0, 16):
                for indDef in range(0, 16):
                    CP_check_result = check_CP(CP, baseAtk[ind], indAtk, baseDef[ind], indDef, baseSta[ind], indSta, cpm)
                    if CP_check_result:
                        max_cp = calculate_max_CP(baseAtk[ind], indAtk, baseDef[ind], indDef, baseSta[ind], indSta, CPM[-1][-1])
                        perfection = (indAtk + indDef + indSta) / 45.
                        possible_IV.append([lv, indAtk, indDef, indSta, max_cp, np.around(perfection, decimals=2)])

# Output    
print '\nAnalysis Result:'
print 'Best Possible CP:', BestPossibleCP, '\n'
print '{:<16} {:<16} {:<16} {:<16} {:<16} {:<16}'.format('Level', 'Attack', 'Defense', 'Stamina', 'CP', 'Perfection')
print '-----------------------------------------------------------------------------------------------'
if len(possible_IV) == 0:
    print 'Incorrect input data.'
else:
    # When you catch pokemon, it will never be a half-level.
    # This helps to narrow down the stats and give more precise information.
    if powered == False:
        for i in reversed(range(len(possible_IV))):
            level_temp = possible_IV[i][0]
            if np.mod(level_temp, 1) != 0:  # if level is not a whole number
                possible_IV.remove(possible_IV[i])
    for i in possible_IV:
        print '{:<16} {:<16} {:<16} {:<16} {:<16} {:<16}'.format(i[0], np.uint8(i[1]), np.uint8(i[2]), np.uint8(i[3]), np.uint16(i[4]), i[5])

print '\n'
print '{:<4} {:<16} {:<16}'.format('#', 'Pokemon', 'Best Possible CP')
print '--------------------------------------'
for i in range(len(labels)):
    print '{:<4} {:<16} {:<16}'.format(ind_sorted[i], label_sorted[i], maxCP_sorted[i])
