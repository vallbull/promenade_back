from collections import Counter
import json
from IPython.core.display import deepcopy
import pandas as pd
import numpy as np
from random import randint, choice, choices

DAYS = 5
HOURS_PER_DAY = 8
SLOTS_PER_DAY = HOURS_PER_DAY * 2
STAFF_NUM = 8


def fix_index(index):
    return str(index).encode('cp1251').decode('utf-8')


def fix_column_name(column):
    return str(column).encode('cp1251').decode('utf-8')


def get_data(filename):
    data = pd.read_excel(filename, sheet_name='Входные данные для анализа')
    data.dropna(inplace=True, axis=0)
    data.loc[22, 'Адрес точки, г. Краснодар'] = 'ул. им. Героя Аверкиева А.А., д. 8'
    staff = pd.read_excel(filename, sheet_name='Справочник сотрудников')
    return data, staff


def generate_priority(data):
    res = []
    for row in data.values.tolist():
        if (row[-3] > 7 and row[-2] > 0) or (row[-3] > 14):
            res.append('Выезд на точку для стимулирования выдач')
        elif row[-1] > 0 and (row[-1] / row[-2] < 0.5):
            res.append('Обучение агента')
        elif row[2] == 'вчера' or row[3] == 'нет':
            res.append('Доставка карт и материалов')
        else:
            res.append('-')

    return res


def get_tasks(data_task):
    tasks = [[id, t, p] for id, t, p in
             zip(data_task['№ точки'], data_task['Задача'].values.tolist(), data_task['Приоретет'].values.tolist())]

    task_type = {'Доставка карт и материалов': (3, 1.5), 'Обучение агента': (2, 2),
                 'Выезд на точку для стимулирования выдач': (1, 4)}
    priority = {'Низкий': 1, 'Средний': 2, 'Высокий': 3}

    for i in range(len(tasks)):
        tasks[i].append(int(task_type[tasks[i][1]][1] / 0.5))
        tasks[i][1] = task_type[tasks[i][1]][0]
        tasks[i][2] = priority[tasks[i][2]]
    return tasks


def random_position(cur_task):
    duration = cur_task[-1]
    day = randint(0, DAYS - 1)
    worker = randint(0, STAFF_NUM - 1)
    time = randint(0, SLOTS_PER_DAY - duration)
    position = day * STAFF_NUM * SLOTS_PER_DAY + worker * SLOTS_PER_DAY + time
    return position


def generate_genome(data_task):
    genome = [[] for _ in range(DAYS * SLOTS_PER_DAY * STAFF_NUM)]
    hashmap = {}
    position_list = []
    s = 0
    for cur_task in get_tasks(data_task):
        duration = cur_task[-1]
        position = random_position(cur_task)

        position_list.append(position)
        hashmap[cur_task[0]] = cur_task[1:], position

        for i in range(position, position + duration):
            genome[i].append(cur_task[0])

    return genome, hashmap


def generate_population(data_task):
    population = []
    for _ in range(100):
        genome = generate_genome(data_task)
        population.append(genome)
    return population


def genome_from_hash(hashmap):
    keys = list(hashmap.keys())
    genome = [[] for _ in range(DAYS * SLOTS_PER_DAY * STAFF_NUM)]
    for key in keys:
        duration = hashmap[key][0][-1]
        position = hashmap[key][1]

        for i in range(position, position + duration):
            genome[i].append(key)

    return genome


def crossover(parent1, parent2):
    keys = list(parent1[1].keys())
    crossover_point = randint(1, len(keys))
    offspring1_hash = {}
    offspring2_hash = {}

    for key in keys[: crossover_point]:
        offspring1_hash[key] = parent1[1][key]
    for key in keys[crossover_point:]:
        offspring1_hash[key] = parent2[1][key]

    offspring1_genome = genome_from_hash(offspring1_hash)

    for key in keys[: crossover_point]:
        offspring2_hash[key] = parent2[1][key]
    for key in keys[crossover_point:]:
        offspring2_hash[key] = parent1[1][key]

    offspring2_genome = genome_from_hash(offspring2_hash)

    return (offspring1_genome, offspring1_hash), (offspring2_genome, offspring2_hash)


def mutation(genome):
    random_task = choice(list(genome[1].keys()))
    pos = random_position(genome[1][random_task][0])
    mutated_hash = {key: value for key, value in zip(list(genome[1].keys()), list(genome[1].values()))}
    mutated_hash[random_task] = (mutated_hash[random_task][0], pos)
    mutated_genome = genome_from_hash(mutated_hash)

    return mutated_genome, mutated_hash


def get_distance(loc1, loc2, distance):
    meters = distance.loc[loc1, loc2]
    if meters == 0:
        return 0
    if meters > 15000:
        return int(np.ceil(meters / 1000 / 40 * 60 / 30))
    else:
        return int(np.ceil(meters / 1000 / 20 * 60 / 30))


def append_time(genome, hashmap_address, employee_address, distance):
    score = 0
    new_genome = deepcopy(genome)
    for key in list(new_genome[1].keys()):

        duration_ab = 0
        task = new_genome[1][key]
        position = task[1]
        worker_start = position // 128 * STAFF_NUM * SLOTS_PER_DAY + (position % 128) // 16 * SLOTS_PER_DAY
        flag = 0

        for i in range(position - 1, worker_start - 1, -1):
            if new_genome[0][i] != []:
                flag = 1
                for z in range(len(new_genome[0][i])):
                    duration_ab = get_distance(hashmap_address[new_genome[0][i][z]],
                                               hashmap_address[new_genome[0][position][0]], distance)
        if flag == 0:
            duration_ab = get_distance(employee_address[(position % 128) // 16],
                                       hashmap_address[new_genome[0][position][0]], distance)

        for p in range(position - 1, position - 1 - duration_ab, -1):
            new_genome[0][p].append(key)
            if p < worker_start:
                score += 640
    return new_genome, score


def fitness_genome(genome, grade_tasks, employee_grade, hashmap_address, employee_address, distance):
    fit_genome = deepcopy(genome)
    hashmap = fit_genome[1]
    fit_genome, score = append_time(fit_genome, hashmap_address, employee_address, distance)

    for position, gene in enumerate(fit_genome[0]):
        if len(gene) > 1:
            score += 800
        if gene == []:
            score += 640 - position
        if gene != []:
            for i in range(len(gene)):
                if hashmap[gene[i]][0][0] not in grade_tasks[employee_grade[(position % 128) // 16]]:
                    score += 640
                if hashmap[gene[i]][0][1] == 3:
                    score += position
                elif hashmap[gene[i]][0][1] == 2:
                    score += position // 1.5
    return score


def create_top_population(population, grade_tasks, employee_grade, hashmap_address, employee_address, distance):
    hashmap_score = {}
    for idx, genom in enumerate(population):
        hashmap_score[idx] = fitness_genome(genom, grade_tasks, employee_grade, hashmap_address, employee_address, distance)
    hashmap_score = {k: v for k, v in sorted(hashmap_score.items(), key=lambda item: item[1])}
    top_population = []
    hashmap_score_keys = list(hashmap_score.keys())
    for i in range(len(hashmap_score) // 2):
        top_population.append(append_time(population[hashmap_score_keys[i]], hashmap_address, employee_address, distance)[0])  #######
    return top_population, hashmap_score


def evolution(n: int, data_task, grade_tasks, employee_grade, hashmap_address, employee_address, distance, best_score=10000000):
    population = generate_population(data_task)
    top_population, _ = create_top_population(population, grade_tasks, employee_grade, hashmap_address, employee_address, distance)
    for i in range(n):
        for genom1, genom2 in zip(top_population[::2], top_population[1::2]):
            new_genom1, new_genom2 = crossover(genom1, genom2)
            new_genom2_mutation = mutation(new_genom2)
            top_population.extend([new_genom1, new_genom2_mutation])

        top_population, hashmap_score = create_top_population(top_population, grade_tasks, employee_grade, hashmap_address, employee_address, distance)
        max_score = list(hashmap_score.values())[0]
        if max_score < best_score:
            best_score = max_score
            # print(best_score)
    return top_population[0]


def get_tasks_day(top_genome, hashmap_address):
    task_type_hash = {3: 'Доставка карт и материалов', 2: 'Обучение агента',
                      1: 'Выезд на точку для стимулирования выдач'}
    one_day_g = top_genome[0][0:128]
    work_time = Counter([x for xs in one_day_g for x in xs if x != []])
    json_dict = {}
    idx_for_drop = []
    for i in range(0, 128, 16):
        staff_address = []
        for j in range(i, i + 16):
            if one_day_g[j] != []:
                for task in range(len(one_day_g[j])):
                    address = hashmap_address[one_day_g[j][task]]
                    if address not in staff_address:
                        staff_address.append(address)
                        task_type = task_type_hash[top_genome[1][one_day_g[j][task]][0][0]]
                        staff_name = i // 16
                        if staff_name not in json_dict.keys():
                            json_dict[staff_name] = [[address, task_type, work_time[one_day_g[j][task]] * 30]]
                        else:
                            json_dict[staff_name].append([address, task_type, work_time[one_day_g[j][task]] * 30])
                        idx_for_drop.append(one_day_g[j][task])
    return json_dict


def creat_distance(distance_filename):
    distance = pd.read_excel(distance_filename)
    distance = distance.set_index(0)
    distance = distance.rename(columns=fix_column_name)
    distance.index = distance.index.map(fix_index)
    distance.drop_duplicates(inplace=True)
    return distance


def create_data_task(data, res):
    data_task = data.copy()
    data_task['Задача'] = res
    data_task = data_task.loc[data_task['Задача'] != '-']
    data_task.loc[data_task['Задача'] == 'Выезд на точку для стимулирования выдач', 'Приоретет'] = 'Высокий'
    data_task.loc[data_task['Задача'] == 'Обучение агента', 'Приоретет'] = 'Средний'
    data_task.loc[data_task['Задача'] == 'Доставка карт и материалов', 'Приоретет'] = 'Низкий'
    return data_task


def main(n):
    data, staff = get_data('Копия ДатаСет_Финал.xlsx')
    distance = creat_distance('Копия output_v3.xlsx')
    res = generate_priority(data)
    data_task = create_data_task(data, res)

    hashmap_address = {}
    for point, address in zip(data['№ точки'], data['Адрес точки, г. Краснодар']):
        hashmap_address[point] = 'Краснодар, ' + address
    task_type = {'Доставка карт и материалов': (3, 1.5), 'Обучение агента': (2, 2),
                 'Выезд на точку для стимулирования выдач': (1, 4)}
    employee_grade = dict(zip(list(staff.index), staff['Грейд']))
    grade_tasks = {'Синьор': [task_type['Доставка карт и материалов'][0],
                              task_type['Обучение агента'][0],
                              task_type['Выезд на точку для стимулирования выдач'][0]],
                   'Мидл': [task_type['Доставка карт и материалов'][0], task_type['Обучение агента'][0]],
                   'Джун': [task_type['Доставка карт и материалов'][0]]}
    employee_address = dict(zip(list(staff.index), staff['Адрес локации']))

    top_population = evolution(n, data_task, grade_tasks, employee_grade, hashmap_address, employee_address, distance)
    json_dict = get_tasks_day(top_population, hashmap_address)
    return json_dict

