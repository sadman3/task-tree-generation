from configparser import ConfigParser
import os
import json
from datetime import datetime
import pickle
from FOON_class import FunctionalUnit, Object


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
create_foon_pkl = config["flag"]["create_foon_pkl"]
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
                new_object.is_goal_node = True

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
    for subgraph in os.listdir(dir):
        filepath = os.path.join(dir, subgraph)
        FU_list = get_FU_list(filepath)
        for FU in FU_list:
            # checking duplicate functional unit
            if not FU.check_if_FU_exist(functional_units):
                functional_units.append(FU)

    # save universal foon in a text file
    if create_foon_txt:
        F = open(foon_txt, 'w')
        F.write('# Date created:\t' +
                str(datetime.today().strftime('%d.%m.%Y')) + '\n')
        F.write('//\n')
        for FU in functional_units:
            F.write(FU.get_FU_as_text() + "\n")
        F.close()

    # save universal foon in a pickle file
    if create_foon_pkl:
        F = open(foon_pkl, "wb")
        pickle.dump(functional_units, F)


if __name__ == "__main__":
    merge()
