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
inds = baseStats[:, 6]      # indices of pokemon
del baseStats

# load CP multiplier
CPM = np.genfromtxt('cp_multiplier_by_level.txt', delimiter='\t', skip_header=1)

# load Power Up Costs
costsByLevel = np.genfromtxt('cost_by_level.txt', dtype=np.uint16, delimiter='\t', skip_header=1)

# Info from Pokemon
label = 'Dratini'     # str, name of pokemon
ind = None            # int, # of pokemon, range 1-151
CP = 556              # int, current CP
user_HP = 56                # int, current max HP
CP_per_powerup = 2500  # int, stardust cost of a power up

if any(label in i for i in labels):
    ind = np.where(labels==label)[0][0]
    print '{:<16} {:<4} {:<8}'.format('Inquiry', ind+1, label)
elif ind < len(labels):
    label = labels[ind-1]
    print '{:<16} {:<4} {:<8}'.format('Inquiry', ind, label)
else:
    raise ValueError('Pokemon not found.')

print '{:<16} {:<16}'.format('CP', CP)
print '{:<16} {:<16}'.format('HP', user_HP)
print '{:<16} {:<16}'.format('Stardust Cost', CP_per_powerup)

# base values
baseAtk = 2 * np.around((Atk * SpAtk) ** .5 + Spd ** .5)  # Base Attack
baseDef = 2 * np.around((Def * SpDef) ** .5 + Spd ** .5)  # Base Defense
baseSta = 2 * HP                                 # Base Stamina

# Max CP
maxCP = (baseAtk + 15) * (baseDef + 15) ** .5 * (baseSta + 15) ** .5 * CPM[-1][-1] ** 2 /10
maxCP_sorted = np.uint16(np.sort(maxCP)[::-1])
maxCP_sortedInd = np.argsort(-maxCP)
label_sorted = labels[maxCP_sortedInd]
ind_sorted = np.uint8(inds[maxCP_sortedInd])
BestPossibleCP = np.uint16(maxCP[ind])

# estimate pokemon level and possible CP multipliers
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

# estimiate possible individual stamina
possible_indSta = []
possible_CPM = []
possible_IV = []
possible_indDef = range(1,16)
for i in range(len(CPMs)):
    indSta_temp = np.around(user_HP / np.asarray(CPMs[i]) - baseSta[ind])
    if (indSta_temp >= 1) & (indSta_temp <= 15):
        possible_indSta.append(indSta_temp)
        possible_CPM.append(CPMs[i])

if len(possible_indSta) == 0:
    raise ValueError('Invalid HP.')

# estimiate possible individual attack
for i in range(len(possible_indSta)):
    for j in range(len(possible_indDef)):  # indDef guesses
        indAtk_temp = (CP / ((baseDef[ind] + possible_indDef[j]) ** .5 * (baseSta[ind] + possible_indSta[i]) ** .5 * possible_CPM[i] ** 2 / 10)) - baseAtk[ind]
        indAtk_temp = np.around(indAtk_temp)
        if (indAtk_temp >= 1) & (indAtk_temp <= 15):
            # possible CP
            Atk_temp = baseAtk[ind] + indAtk_temp
            Def_temp = baseDef[ind] + possible_indDef[j]
            Sta_temp = baseSta[ind] + possible_indSta[i]
            CP_temp = Atk_temp * Def_temp ** .5 * Sta_temp ** .5 * CPM[-1][-1] ** 2 / 10
            # calculate perfection
            perfection = np.around((indAtk_temp + possible_indDef[j] + possible_indSta[i]) / 45, decimals=2)
            # combinations
            possible_IV.append([possible_pokemonLevel[i], indAtk_temp, possible_indDef[j], possible_indSta[i], np.maximum(10, CP_temp), perfection]) 

# Output    
print '\nAnalysis Result:'
print 'Best Possible CP:', BestPossibleCP, '\n'
print '{:<16} {:<16} {:<16} {:<16} {:<16} {:<16}'.format('Level', 'Attack', 'Defense', 'Stamina', 'CP', 'Perfection')
print '-----------------------------------------------------------------------------------------------'
for i in possible_IV:
    print '{:<16} {:<16} {:<16} {:<16} {:<16} {:<16}'.format(i[0], np.uint8(i[1]), np.uint8(i[2]), np.uint8(i[3]), np.uint16(i[4]), i[5])

print '\n'
print '{:<4} {:<16} {:<16}'.format('#', 'Pokemon', 'Best Possible CP')
print '--------------------------------------'
for i in range(len(labels)):
    print '{:<4} {:<16} {:<16}'.format(ind_sorted[i], label_sorted[i], maxCP_sorted[i])
