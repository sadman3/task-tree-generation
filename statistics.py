import json
import os
import pickle
from configparser import ConfigParser
import utils

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

selected_category = ['salad', 'omelette', 'rice', 'soup', 'drinks']

#selected_category = ['omelette']

subgraph_dir = config['source']['data_source']
foon_txt = config['source']['foon_txt']
foon_pkl = config['source']['foon_pkl']
dish_type_path = config["info"]["dish_type"]
recipe_category_path = config["info"]["recipe_category"]
create_foon_txt = config["flag"]["create_foon_txt"]
kitchen_path = config['info']['kitchen']
default_kitchen_path = config['info']['default_kitchen_item']
object_state_map_path = config['info']['object_state_map']

utensils = []
with open('info/utensils.txt', 'r') as f:
    for line in f:
        utensils.append(line.rstrip())

foon = pickle.load(open(foon_pkl, 'rb'))

object_state_map = json.load(open(object_state_map_path))


def find_state_motion_count():
    print('Total functional unit: ', len(foon["functional_units"]))

    object_map = {}
    motion_map = {}
    state_map = {}
    utensil_map = {}
    for fu in foon["functional_units"]:
        for node in fu.input_nodes:
            object = node.label

            if object in utensils:
                utensil_map[object] = utensil_map.get(object, 0) + 1
            else:
                if len(node.ingredients) == 0:
                    object_map[object] = object_map.get(object, 0) + 1

            for state in node.states:
                state_map[state] = state_map.get(state, 0) + 1

        for node in fu.output_nodes:
            object = node.label

            if object in utensils:
                utensil_map[object] = utensil_map.get(object, 0) + 1
            else:
                if len(node.ingredients) == 0:
                    object_map[object] = object_map.get(object, 0) + 1

            for state in node.states:
                state_map[state] = state_map.get(state, 0) + 1

        motion = fu.motion_node.replace('*', '')

        motion_map[motion] = motion_map.get(motion, 0) + 1

    print('Total objects:', len(object_map))
    print('Total utensils:', len(utensil_map))
    print('Total states:', len(state_map))
    print('Total motions:', len(motion_map))

    print(state_map)
    exit(0)

    object_map = dict(
        sorted(object_map.items(), key=lambda item: item[1], reverse=True))
    utensil_map = dict(
        sorted(utensil_map.items(), key=lambda item: item[1], reverse=True))
    # state_map = dict(
    #     sorted(state_map.items(), key=lambda item: item[1], reverse=True))
    motion_map = dict(
        sorted(motion_map.items(), key=lambda item: item[1], reverse=True))

    top_n = 10

    print('\n\nTop {} motions'.format(top_n))
    cnt = 0
    for motion in motion_map:
        print(motion, motion_map[motion])

        cnt += 1
        if cnt == top_n:
            break

    print('\n\nTop {} states'.format(top_n))
    object_state_map = json.load(open(object_state_map_path))

    state_freq = {}
    for object in object_state_map:
        for state in object_state_map[object]:
            if state not in state_freq:
                state_freq[state] = set()
            state_freq[state].add(object)

    state_freq = dict(
        sorted(state_freq.items(), key=lambda item: len(item[1]), reverse=True))

    cnt = 0
    for state in state_freq:
        print(state, len(state_freq[state]))

        cnt += 1
        if cnt == top_n:
            break


def find_object_utensil_count():
    object_map = {}
    utensil_map = {}
    for _file in os.listdir('subgraphs/JSON'):
        subgraph = json.load(open('subgraphs/JSON/' + _file))
        mapped_item = []

        for fu in subgraph:
            for node in fu["input_nodes"]:
                object = node["label"]
                if object not in mapped_item:
                    mapped_item.append(object)
                    if object in utensils:
                        utensil_map[object] = utensil_map.get(object, 0) + 1
                    else:
                        if len(node["ingredients"]) == 0:
                            object_map[object] = object_map.get(object, 0) + 1
                else:
                    continue

            for node in fu["output_nodes"]:
                object = node["label"]
                if object not in mapped_item:
                    mapped_item.append(object)
                    if object in utensils:
                        utensil_map[object] = utensil_map.get(object, 0) + 1
                    else:
                        if len(node["ingredients"]) == 0:
                            object_map[object] = object_map.get(object, 0) + 1
                else:
                    continue
    object_map = dict(
        sorted(object_map.items(), key=lambda item: item[1], reverse=True))
    utensil_map = dict(
        sorted(utensil_map.items(), key=lambda item: item[1], reverse=True))

    top_n = 10

    print('\n\nTop {} objects'.format(top_n))
    cnt = 0
    for object in object_map:
        print(object, object_map[object])

        cnt += 1
        if cnt == top_n:
            break

    print('\n\nTop {} utensils'.format(top_n))
    cnt = 0
    for utensil in utensil_map:
        print(utensil, utensil_map[utensil])

        cnt += 1
        if cnt == top_n:
            break

    print()
    print()


def evaluate_without_substitution(input_dir=''):
    for currentpath, folders, files in os.walk(input_dir):
        # progress_line_dir = currentpath.replace(source_dir, target_dir)

        temp = currentpath.split('/')[-1]
        if temp not in selected_category:
            continue

        for file in files:
            input_path = os.path.join(currentpath, file)

            input_json = json.load(open(input_path))
            overlap = 0
            for ing in input_json["ingredients"]:
                input_object = ing["object"]
                input_state = ing["state"]

                if input_object in object_state_map:
                    overlap += 1

            # print(file.replace('.json', ''))
            # print(len(input_json["ingredients"]))
            print(overlap)


def compare_performance(input_dir='', output_dir=''):
    for currentpath, folders, files in os.walk(input_dir):
        # progress_line_dir = currentpath.replace(source_dir, target_dir)

        temp = currentpath.split('/')[-1]
        if temp not in selected_category:
            continue

        for file in files:
            input_path = os.path.join(currentpath, file)
            output_path = input_path.replace(input_dir, output_dir)

            input_json = json.load(open(input_path))
            output_json = json.load(open(output_path))

            input_objects = []
            for ing in input_json["ingredients"]:
                input_objects.append(ing["object"])

            output_objects = []
            for fu in output_json:
                for node in fu["input_nodes"]:
                    output_objects.append(node["label"])
                    for ing in node["ingredients"]:
                        output_objects.append(ing)
                for node in fu["output_nodes"]:
                    output_objects.append(node["label"])
                    for ing in node["ingredients"]:
                        output_objects.append(ing)

            overlap = len(set(input_objects) & set(output_objects))
            # print(file.replace('.json', '') + ',' +
            #      str(len(input_objects)) + ',' + str(overlap))
            print(overlap)


def find_recipe1m_object_state_count(path='recipe1m_merged.pkl'):

    recipes = pickle.load(open(path, 'rb'))
    obj = []
    state_list = []
    for recipe in recipes:
        ing = recipe['ingredients']
        states = recipe['states']
        for i in ing:
            obj.append(i)
        for state in states:
            state_list.append(state)

    obj = set(obj)
    state_list = set(state_list)
    print(len(obj))
    print(len(state_list))
    print(state_list)


def find_confidence(input_dir):
    ingredient_set = set()

    for currentpath, folders, files in os.walk(input_dir):
        # progress_line_dir = currentpath.replace(source_dir, target_dir)

        temp = currentpath.split('/')[-1]

        if temp in selected_category:
            for file in files:
                input_path = os.path.join(currentpath, file)

                input_json = json.load(open(input_path))

                for ing in input_json['ingredients']:
                    ingredient_set.add(ing['object'])

    print(len(ingredient_set))

    confidence_map = {}
    for ing in ingredient_set:
        confidence_map[ing] = []
        best_score = -1
        best_match = ''
        for object in object_state_map:
            if object in utensils:
                continue
            score = utils.get_object_similarity(ing, object)
            confidence_map[ing].append({'object': object, 'score': score})
            if best_score < score:
                best_score = score
                best_match = object
        if best_score > 0 and best_score < 1:
            print(ing, "{:.2f}".format(best_score*100))
    # print(confidence_map)
    # json.dump(confidence_map, open('confidence_map.json', 'w'), indent=4)


def find_top5_equivalent():
    f = open('confidence_map.json')
    confidence_map = json.load(f)
    for i in confidence_map:
        print(i)
    f.close()
    # for item in confidence_map:
    #     confidence_map[item].sort(key=lambda x: x["score"], reverse=True)
    # json.dump(confidence_map, open('confidence_map.json', 'w'), indent=4)


def most_freq_motion_in_final_tree(dir='output_json/final_task_tree/salad/'):
    freq = {}
    for recipe in os.listdir(dir):
        f = open(dir + recipe)
        FUs = json.load(f)
        for fu in FUs:
            motion = fu["motion_node"].replace('*', '')
            freq[motion] = freq.get(motion, 0) + 1
    for i in freq:
        print(freq[i])


def most_freq_ingredients(path):
    freq_map = {}
    cnt = 0
    for x in os.listdir(path):
        cnt += 1
        if cnt > 100:
            break
        recipe = json.load(open(os.path.join(path, x), 'r'))
        ings = recipe["ingredients"]
        for ing in ings:
            obj = ing["object"]
            freq_map[obj] = freq_map.get(obj, 0) + 1

    freq_map = dict(
        sorted(freq_map.items(), key=lambda item: item[1], reverse=True))

    for ing, freq in freq_map.items():
        print(ing)
    for ing, freq in freq_map.items():
        print(freq)


if __name__ == "__main__":
    # find_object_utensil_count()
    # find_state_motion_count()

    #compare_performance('input', 'output_json/reference_task_tree')
    # compare_performance('input', 'output_json/final_task_tree')
    # evaluate_without_substitution('input')
    # find_confidence('input')
    # find_top5_equivalent()
    # find_state_motion_count()
    # find_recipe1m_object_state_count()
    # most_freq_motion_in_final_tree()
    most_freq_ingredients("input/salad")
