from configparser import ConfigParser
import os
import json
from datetime import datetime
import pickle
from FOON_class import FunctionalUnit, Object
from utils import get_utensils

# -----------------------------------------------------------------------------------------------------------------------------#

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)


subgraph_dir = config['source']['data_source']
foon_txt = config['source']['foon_txt']
foon_pkl = config['source']['foon_pkl']
dish_type_path = config["info"]["dish_type"]
recipe_category_path = config["info"]["recipe_category"]
create_foon_txt = config["flag"]["create_foon_txt"]
kitchen_path = config['info']['kitchen']
default_kitchen_path = config['info']['default_kitchen_item']
object_state_map_path = config['info']['object_state_map']

utensils = get_utensils()
default_kitchen_items = json.load(open(default_kitchen_path, 'r'))
# -----------------------------------------------------------------------------------------------------------------------------#


def read_categories(path=dish_type_path):
    """
        parameters: path of dish types
        returns: a map of dish types. key = dish id, value = dish type
    """
    categories = {}
    _file = open(path, 'r')
    for line in _file:
        category_id, category_name = line.split('\t')
        categories[category_id] = category_name.rstrip()

    return categories

# -----------------------------------------------------------------------------------------------------------------------------#


def check_item_in_default_kitchen(ingredient=None):

    for item in default_kitchen_items:
        if item["label"] == ingredient.label \
                and sorted(item["states"]) == sorted(ingredient.states) \
                and sorted(item["ingredients"]) == sorted(ingredient.ingredients) \
                and item["container"] == ingredient.container:
            return True

    return False

# -----------------------------------------------------------------------------------------------------------------------------#


def get_FU_list(filepath):
    """
        parameters: path of a subgraph text file
        returns: a list of FU
    """
    lines = open(filepath, 'r')

    FU_list = []

    FU = FunctionalUnit()
    new_object = None
    is_input = True

    for line in lines:

        if line.startswith("//"):
            # functional unit separators:

            # check if an object is constructed
            if new_object:
                FU.output_nodes.append(new_object)
                new_object = None
                # if FU is already constructed, add it to the FU list
            if FU.motion_node:
                FU_list.append(FU)
                FU = FunctionalUnit()

            is_input = True

            continue

        label = line.split("\t")
        if len(label) < 2:
            # -- this is to make sure that we skip incorrect lines
            print(
                ' -- WARNING: there is a line that is possibly incorrect : ' + str(label))
            continue

        label[1] = label[1].lower().rstrip()

        if line.startswith("O"):
            if new_object:
                # decide whether to add as input or output node
                if not is_input:
                    FU.output_nodes.append(new_object)
                else:
                    FU.input_nodes.append(new_object)

            # len = 3 for goal node
            new_object = Object(label[1])
            new_object.object_in_motion = label[2]
            if len(label) > 3:
                new_object.recipe_category = label[3].rstrip()

        if line.startswith("S"):

            if len(label) > 2:
                # add the ingredients to current object
                if label[2].startswith('{'):
                    ingredients = label[2].rstrip().replace(
                        '{', '').replace('}', '')
                    new_object.ingredients = ingredients.split(',')

                # add the container to current object
                elif label[2].startswith('['):
                    container = label[2].rstrip().replace(
                        '[', '').replace(']', '')
                    new_object.container = container

            else:
                new_object.states.append(label[1])

        if line.startswith("M"):
            # append the current object
            FU.input_nodes.append(new_object)
            new_object = None
            is_input = False
            FU.motion_node = label[1]

    return FU_list


# -----------------------------------------------------------------------------------------------------------------------------#


def merge(dir=subgraph_dir):
    """
        parameters: directory of subgraphs
        creates: a merged version of all subgraphs (universal FOON)
    """
    functional_units = []
    fu_id = 0
    for subgraph in os.listdir(dir):
        filepath = os.path.join(dir, subgraph)
        FU_list = get_FU_list(filepath)
        for FU in FU_list:
            # checking duplicate functional unit
            if not FU.check_if_FU_exist(functional_units):
                FU.id = fu_id  # set the id according to its index
                functional_units.append(FU)
                fu_id += 1

    # save universal foon in a text file
    if create_foon_txt:
        F = open(foon_txt, 'w')
        F.write('# Date created:\t' +
                str(datetime.today().strftime('%d.%m.%Y')) + '\n')
        F.write('//\n')
        for FU in functional_units:
            F.write(FU.get_FU_as_text() + "\n")
        F.close()
        print('-- universal foon saved to', foon_txt)

    # save universal foon in a pickle file
    object_nodes = []
    object_id = 0
    for FU in functional_units:
        for _input in FU.input_nodes:
            # avoid adding duplicate objects
            existing_object_id = _input.check_object_exist(object_nodes)

            # if the object exists, assign the existing object id
            # if it does not, give it a new id
            if existing_object_id == -1:  # object is not found
                _input.id = object_id
                object_nodes.append(_input)
                object_id += 1
            else:
                _input.id = existing_object_id

        for _output in FU.output_nodes:
            existing_object_id = _output.check_object_exist(object_nodes)

            if existing_object_id == -1:  # object is not found
                _output.id = object_id
                object_nodes.append(_output)
                object_id += 1
            else:
                _output.id = existing_object_id

    object_to_FU_map = {}

    # create a mapping between output node to functional units
    # in this map, key = object index in object_nodes,
    # value = index of all FU where this object is an output
    for FU_index, FU in enumerate(functional_units):
        for _output in FU.output_nodes:

            # ignore object that has no state like "knife"
            if len(_output.states) == 0 and len(_output.ingredients) == 0 and _output.container == None:
                continue

            object_index = _output.id
            if object_index not in object_to_FU_map:
                object_to_FU_map[object_index] = []
            object_to_FU_map[object_index].append(FU_index)

    F = open(foon_pkl, "wb")
    pickle_data = {
        "functional_units": functional_units,
        "object_nodes": object_nodes,
        "object_to_FU_map": object_to_FU_map
    }
    pickle.dump(pickle_data, F)
    F.close()
    print('-- universal foon saved to', foon_pkl)

    print('-- total functional unit:', len(functional_units))
    # create recipe classification
    create_recipe_classification(functional_units)
    print('-- recipe classification created in', recipe_category_path)


# -----------------------------------------------------------------------------------------------------------------------------#


def create_recipe_classification(functional_units):
    """
        parameters: a list of all functional units
        creates: recipe classification in a json file
    """

    recipe_categories = {}
    categories = read_categories()
    for _, value in categories.items():
        recipe_categories[value] = []

    for FU in functional_units:
        for node in FU.output_nodes:
            category_id = node.recipe_category
            if category_id != -1:
                goal_node = {
                    "label": node.label,
                    "states": node.states,
                    "ingredients": node.ingredients,
                    "container": node.container,
                    "id": node.id
                }
                recipe_categories[categories[category_id]].append(goal_node)

    # save recipe classification in a json file
    json.dump(recipe_categories, open(recipe_category_path, 'w'), indent=4)

# -----------------------------------------------------------------------------------------------------------------------------#

# Creates a kitchen file based on the nodes that are only used as input


def prepare_kitchen(foon_path=foon_pkl, kitchen_path=kitchen_path):

    # load universal foon pickle file
    pickle_data = pickle.load(open(foon_path, 'rb'))
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    default_starting_states = ['off', 'clean', 'empty', 'whole']

    start_nodes = []
    object_added = []
    # check which object does not have any FU mapping
    for object in object_nodes:
        object_index = object.id
        object_json = object.get_object_as_json()

        if object_index in object_added:
            continue

        # if object state is in default_starting_states
        if len(object.states) == 1 and object.states[0] in default_starting_states:

            start_nodes.append(object_json)
            object_added.append(object_index)

        # if object is not a part of output in any fu
        elif object_index not in object_to_FU_map:
            start_nodes.append(object_json)
            object_added.append(object_index)

        # if object is a utensil without any ingredient
        elif object.label in utensils and len(object.ingredients) == 0:
            start_nodes.append(object_json)
            object_added.append(object_index)

        elif check_item_in_default_kitchen(object):
            start_nodes.append(object_json)
            object_added.append(object_index)

    F = open(kitchen_path, 'w')
    json.dump(start_nodes, F, indent=4)


# -----------------------------------------------------------------------------------------------------------------------------#

def save_all_object_states(foon_path=foon_pkl):
    pickle_data = pickle.load(open(foon_path, 'rb'))
    functional_units = pickle_data["functional_units"]

    object_state_map = {}

    for fu in functional_units:

        for node in fu.input_nodes:
            object = node.label
            if object in utensils or node.recipe_category != -1:
                continue
            if object not in object_state_map:
                object_state_map[object] = []
            for state in node.states:
                if state not in object_state_map[object]:
                    object_state_map[object].append(state)

        for node in fu.output_nodes:
            object = node.label
            if object in utensils or node.recipe_category != -1:
                continue
            if object not in object_state_map:
                object_state_map[object] = []
            for state in node.states:
                if state not in object_state_map[object]:
                    object_state_map[object].append(state)

    json.dump(object_state_map, open(object_state_map_path, 'w'), indent=4)
# -----------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    # merge()
    # prepare_kitchen()
    save_all_object_states()
