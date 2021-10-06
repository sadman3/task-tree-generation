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
kitchen_path = config['info']['kitchen']

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

# Checks an ingredient exists in kitchen


def check_if_exist_in_kitchen(kitchen_items, ingredient):
    """
        parameters: a list of all kitchen items,
                    an ingredient to be searched in the kitchen
        returns: True if ingredient exists in the kitchen
    """

    for item in kitchen_items:
        if item["label"] == ingredient.label \
                and sorted(item["states"]) == sorted(ingredient.states) \
                and sorted(item["ingredients"] == sorted(ingredient.ingredients)) \
                and item["container"] == ingredient.container:
            return True

    return False

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
    # remove ingredient if it is actually a utensil
    for ing in ingredients:
        if ing["object"] not in utensils:
            processed_ingredients.append(ing)

    return recipe_id, dish_type, processed_ingredients


# -----------------------------------------------------------------------------------------------------------------------------#


# For a dish and a set of ingredients, find the reference goal node
def find_goal_node(dish_type, ingredients):
    from utils import compare_two_recipe
    """
        parameters: dish type and a list of ingredients
        returns: a reference goal node
    """
    input_objects = []
    for ing in ingredients:
        input_objects.append(ing["object"])

    # read the recipe classification
    with open(recipe_category_path) as f:
        categories = json.load(f)
        f.close()

    goal_node = Object()
    best_score = -1
    for category, candidate_recipes in categories.items():
        # find the category
        if dish_type in category.split(','):
            # check each candidate in that category
            for candidate in candidate_recipes:
                similarity_score = compare_two_recipe(
                    input_objects, candidate["ingredients"])
                if similarity_score > best_score:
                    best_score = similarity_score
                    goal_node.label = candidate["label"]
                    goal_node.states = candidate["states"]
                    goal_node.ingredients = candidate["ingredients"]
                    goal_node.container = candidate["container"]

    return goal_node
# -----------------------------------------------------------------------------------------------------------------------------#
# Given a goal node, this method finds the reference task tree
# The search uses heuristic (ingredient overlap) to select a FU from candidate FUs.


def extract_reference_task_tree(functional_units, object_nodes, object_to_FU_map, goal_node):
    """
        parameters: a list of functioal units, a list of object nodes,
                    object to functional unit mapping, a goal node
        returns: a task tree that consists some functional units
    """

    # load the kitchen file
    kitchen_items = json.load(open(kitchen_path))


# -----------------------------------------------------------------------------------------------------------------------------#

# creates the graph using adjacency list
# each object has a list of functional list where it is an output


def read_universal_foon(filepath=foon_pkl):
    """
        parameters: path of universal foon (pickle file)
        returns: a map. key = object, value = list of functional units
    """
    pickle_data = pickle.load(open(filepath, 'rb'))
    functional_units = pickle_data["functional_units"]
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    return functional_units, object_nodes, object_to_FU_map
# -----------------------------------------------------------------------------------------------------------------------------#
# this method creates the task using three major steps mentioned in the paper


def retrieval(functional_units, object_nodes, object_to_FU_map):

    input_file = '/Users/sadman/repository/task-tree-generation/input/00d23f6efb.json'
    recipe_id, dish_type, ingredients = process_input(input_file)

    # step 1: find the reference goal node
    reference_goal_node = find_goal_node(dish_type, ingredients)

    # step 2: find the reference task tree
    extract_reference_task_tree(
        functional_units, object_nodes, object_to_FU_map, reference_goal_node)

    # step 3: modify the reference task tree

    # save the task tree
# -----------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":

    # construct the graph
    print('-- Reading universal foon from', foon_pkl)
    functional_units, object_nodes, object_to_FU_map = read_universal_foon()

    # do the retrieval
    print("-- STARTING RETRIEVAL")
    retrieval(functional_units, object_nodes, object_to_FU_map)
