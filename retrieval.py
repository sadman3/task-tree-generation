import pickle
import json
from configparser import ConfigParser
from FOON_class import FunctionalUnit, Object


# -----------------------------------------------------------------------------------------------------------------------------#

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)


subgraph_dir = config['source']['data_source']
foon_pkl = config['source']['foon_pkl']
recipe_category_path = config["info"]["recipe_category"]

# -----------------------------------------------------------------------------------------------------------------------------#


# Extracts the dish type and ingredient list given input file path
def process_input(filepath):
    """
        parameters: path of input json file
        returns: recipe id, dish type and ingredient list
    """

    input = json.load(open(filepath))

    recipe_id = input["id"]
    dish_type = input["type"]
    ingredients = input["ingredients"]

    return recipe_id, dish_type, ingredients


# -----------------------------------------------------------------------------------------------------------------------------#


# For a dish and a set of ingredients, find the reference goal node
def find_goal_node(dish_type, ingredients):
    """
        parameters: dish type and a list of ingredients
        returns: a reference goal node
    """

    reference_goal_node = {}

    recipe_id = input["id"]
    dish_type = input["type"]
    ingredients = input["ingredients"]

    return

# -----------------------------------------------------------------------------------------------------------------------------#


# creates the graph using adjacency list
# each object has a list of functional list where it is an output
def create_adjacency_list(filepath=foon_pkl):
    """
        parameters: path of universal foon (pickle file)
        returns: a map. key = object, value = list of functional units
    """
    return None

# -----------------------------------------------------------------------------------------------------------------------------#


def retrieval():

    functional_units = pickle.load(open('FOON.pkl', 'rb'))

    functional_units[0].print()
    print(len(functional_units))
# -----------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    input_file = '/Users/sadman/repository/task-tree-generation/input/00d23f6efb.json'
    recipe_id, dish_type, ingredients = process_input(input_file)

    # step 1: find the reference goal node
    reference_goal_node = find_goal_node(dish_type, ingredients)

    # step 2: find the reference task tree

    # step 3: modify the reference task tree
