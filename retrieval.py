import pickle
import json
from configparser import ConfigParser
from FOON_class import FunctionalUnit, Object


# -----------------------------------------------------------------------------------------------------------------------------#

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

utensils_path = config['info']['utensils']
subgraph_dir = config['source']['data_source']
foon_pkl = config['source']['foon_pkl']
recipe_category_path = config["info"]["recipe_category"]

# -----------------------------------------------------------------------------------------------------------------------------#

# Create a list of utensils


def get_utensils(filepath=utensils_path):
    """
        parameters: path of a text file that contains all utensils
        returns: a list of utensils
    """

    utensils = []
    with open(filepath, 'r') as f:
        for line in f:
            utensils.append(line.rstrip())
    return utensils

# -----------------------------------------------------------------------------------------------------------------------------#


# Extracts the dish type and ingredient list given input file path
def process_input(filepath):
    """
        parameters: path of input json file
        returns: recipe id, dish type and ingredient list
    """

    _input = json.load(open(filepath))

    recipe_id = _input["id"]
    dish_type = _input["type"]
    ingredients = _input["ingredients"]

    utensils = get_utensils()
    processed_ingredients = []
    print(utensils)
    for ing in ingredients:
        if ing["object"] not in utensils:
            processed_ingredients.append(ing)

    return recipe_id, dish_type, processed_ingredients


# -----------------------------------------------------------------------------------------------------------------------------#


# For a dish and a set of ingredients, find the reference goal node
def find_goal_node(dish_type, ingredients):
    """
        parameters: dish type and a list of ingredients
        returns: a reference goal node
    """

    reference_goal_node = {}

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
    print(ingredients)

    # step 1: find the reference goal node
    reference_goal_node = find_goal_node(dish_type, ingredients)

    # step 2: find the reference task tree

    # step 3: modify the reference task tree
