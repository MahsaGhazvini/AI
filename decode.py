import random
import string
import copy
import math
import colorama
from colorama import Fore
import sys

NGEN = 400
STABLE_RESET = 50
MUTPB = 0.1
NUM = 100
RANK = 30

ngram_fitness_weight = {'TH': 2, 'HE': 1, 'IN': 1, 'ER': 1,'AN': 1,
                        'ED': 1, 'THE': 5, 'ING': 5,'AND': 5, 'EEE': -5}
freq = [[8.167,'A'], [1.492,'B'], [2.782,'C'],
        [4.253,'D'], [12.702,'E'], [2.228,'F'],
        [2.015,'G'], [6.094,'H'], [6.966,'I'],
        [0.153,'J'], [0.772,'K'], [4.025,'L'],
        [2.406,'M'], [6.749,'N'], [7.507,'O'],
        [1.929,'P'], [0.095,'Q'], [5.987,'R'],
        [6.327,'S'], [9.056,'T'], [2.758,'U'],
        [0.978,'V'], [2.360,'W'], [0.150,'X'],
        [1.974,'Y'], [0.074,'Z']]
freq.sort()
text_freq =[]

text = ""
with open('EncryptedText') as f:
    text = f.read()
    text = text.upper()

words = dict()
f = open('bigList.txt')
for word in f.read().splitlines():
    words[word] = True

# individual : ['S', ...]
letters = list(string.ascii_uppercase)


def random_range(start,end,text_freq):
    r = text_freq[start:end+1]
    random.shuffle(r)
    text_freq[start:end+1]=r


def make_text_freq():
    summ = 0;
    for c in letters:
        summ = summ + text.count(c)

    for c in letters:
        text_freq.append([text.count(c)*100.00/summ,c])
    text_freq.sort()

    for i in range(0,26):
        text_freq[i] = text_freq[i][1]
        freq[i] = freq[i][1]


def print_decode(encoded):
    trans_tab = string.maketrans(''.join(letters), ''.join(encoded))
    decoded_text = text.translate(trans_tab).lower()
    for line in decoded_text.splitlines():
        for word in line.split():
            word_t = ''.join(filter(str.isalpha, word))
            if word_t in words:
                sys.stdout.write(Fore.GREEN + word)
                sys.stdout.write(" ")
            else:
                sys.stdout.write(Fore.RED + word)
                sys.stdout.write(" ")
        print
    print

def random_bad_individual():
    base_individual = [l for l in letters]
    random.shuffle(base_individual)
    return base_individual

def random_individual():
    random_range(0,3,text_freq)
    random_range(4,6,text_freq)
    random_range(7,9,text_freq)
    random_range(10,12,text_freq)
    random_range(13,18,text_freq)
    random_range(19,22,text_freq)
    random_range(23,24,text_freq)
    individual = []
    for i in range(0,26):
        individual.append ([text_freq[i], freq[i]])
    individual.sort()
    for i in range(0,26):
        individual[i] = individual[i][1]
    return individual

def evaluate(individual):
    score = 0
    trans_tab = string.maketrans(''.join(letters), ''.join(individual))
    decoded = text.translate(trans_tab)
    for ngram, weight in ngram_fitness_weight.iteritems():
        score += decoded.count(ngram) * weight
    return score

def mutation(individual,probability):
    clone = copy.deepcopy(individual)
    rand = random.random()
    if rand < probability:
        x = random.randint(0, len(letters)-2)
        y = random.randint(x+1, len(letters)-1)
        clone[x], clone[y] = clone[y], clone[x]
    return clone


def crossover(par1 , par2):
    size = min(len(par1),len(par2))
    rand = random.randint(0,size-1)
    ans1 = [a for a in par1[0:rand]]
    ans2 = [a for a in par2[0:rand]]
    for x in par2:
        if x not in ans1:
            ans1.append(x)
    for x in par1:
        if x not in ans2:
            ans2.append(x)
    return ans1,ans2


def make_population(population):
    pop = []
    for i in range(population):
        individual = random_individual()
        pop.append([evaluate(individual),individual])
    return pop

make_text_freq()
pop = make_population(NUM)
pop.sort(reverse=True)

best = None
best_fitness = 0
stable = 0
counter = 0
count_for_tour = 0
tour = []
try:
    while counter < NGEN:
        new_pop = []
        #zaiif ha ro hazf mikonim va shanse ghavi ha ro vase entekhab shodan bishtar mikonim
        pop[NUM-RANK:NUM] = pop[0:RANK]
        pop.sort(reverse=True)

        for i in range(NUM/2):
            rand1 = random.randint(0,len(pop)-2)
            rand2 = random.randint(rand1+1,len(pop)-1)
            par1 = pop[rand1][1]
            par2 = pop[rand2][1]
            childs = crossover(par1,par2)
            new_pop.append([evaluate(childs[0]),childs[0]])
            new_pop.append([evaluate(childs[1]),childs[1]])
        for np in new_pop:
            temp = mutation(np[1],MUTPB)
            if temp != np[1] :
                np = [evaluate(temp),temp]
        new_pop.sort(reverse=True)


        all_pop = pop[2*RANK:NUM]
        for x in new_pop:
            if x not in all_pop:
                all_pop.append(x)
        all_pop.sort(reverse=True)
        pop= pop[0:2*RANK:2]

        t = 0
        while len(pop) < NUM:
            if t < len(all_pop):
                if all_pop[t] not in pop:
                    pop.append(all_pop[t])
                t = t+1
            else:
                rand = random.randint(0,len(all_pop)-1)
                new = mutation(all_pop[rand][1],1)
                if [evaluate(new),new] not in pop:
                    pop.append([evaluate(new),new])

        pop.sort(reverse=True)
        prev =[]
        for p in pop:
            if p[1] == prev:
                counter = counter + 1
            prev = p[1]
        if best_fitness < pop[0][0]:
            best = pop[0][1]
            best_fitness = pop[0][0]
            print best_fitness
            stable = 0
        else:
            stable = stable + 1
        if stable == STABLE_RESET:
            print "newwwwwwwwwww"
            add_to_tour = []
            t = 0
            while len(add_to_tour) < 10:
                if pop[t] not in tour:
                    add_to_tour.append(pop[t])
                t = t + 1
            tour = tour + add_to_tour
            count_for_tour = count_for_tour + 1
            stable = 0
            g = 0
            if count_for_tour == 5:
                pop = [t for t in tour]
                count_for_tour = 0
                tour = []
            else:
                pop = make_population(NUM)
        print_decode(best)
        for p in pop:
            print Fore.BLUE + ''.join(p[1]),
        print
        print "----------------"
        print "best_fitness :: ", best_fitness
        print "counter :",counter
        counter = counter + 1
except KeyboardInterrupt:
    pass
print_decode(best)
print "final generation"
print best_fitness
print ''.join(best)
line = ''
while_bool = True
while while_bool == True:
    line = raw_input();
    if line == "end":
        while_bool = False
    else:
        char = line.split()
        char[0] = char[0].upper()
        char[1] = char[1].upper()
        for i in range(len(best)):
            c = best[i]
            if c == char[0]:
                best[i] = char[1]
            elif c == char[1]:
                best[i] = char[0]
        print_decode(best)
        print ''.join(best)
        print Fore.YELLOW + "new_fitness :",
        print evaluate(best)
