import json
import os
import pickle
from configparser import ConfigParser

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

# selected_category = ['salad', 'omelette', 'rice', 'soup', 'drinks']

selected_category = ['drinks']

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


def find_object_state_motion_count():

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

    object_map = dict(
        sorted(object_map.items(), key=lambda item: item[1], reverse=True))
    utensil_map = dict(
        sorted(utensil_map.items(), key=lambda item: item[1], reverse=True))
    state_map = dict(
        sorted(state_map.items(), key=lambda item: item[1], reverse=True))
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

            for fu in output_json:
                for node in fu["input_nodes"]:
                    output_objects.append(node["label"])
                    for ing in node["ingredients"]:
                        output_objects.append(ing)

            overlap = len(set(input_objects) & set(output_objects))
            print(file, len(input_objects),  overlap)


if __name__ == "__main__":
    find_object_state_motion_count()
    # compare_performance('input', 'output_json/reference_task_tree')
    # compare_performance('input', 'output_json/final_task_tree')
