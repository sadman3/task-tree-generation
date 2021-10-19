import pickle
import json
from configparser import ConfigParser
from FOON_class import Object
import os
import copy

from utils import compare_two_recipe, find_ingredient_mapping, get_utensils

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
similarity_threshold = float(config["constant"]["similarity_threshold"])
default_ingredient_path = config["info"]["default_ingredient"]
default_ingredient_mapping_path = config['info']['default_ingredient_mapping']

# -----------------------------------------------------------------------------------------------------------------------------#

###################
utensils = get_utensils()
kitchen_items = json.load(open(kitchen_path))
default_ingredients = [object.rstrip()
                       for object in open(default_ingredient_path, 'r')]
###################
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
                and sorted(item["ingredients"]) == sorted(ingredient.ingredients) \
                and item["container"] == ingredient.container:
            return True

    return False

# -----------------------------------------------------------------------------------------------------------------------------#


# select a candidate that has best overlap with input ingredients


def select_best_candidate(input_ingredients, candidates, functional_units):
    """
        parameters: input ingredient: a list of objects,
                    a list of candidate functional units
        returns: returns the id of the best candidate unit
    """

    input_objects = []
    for ingredient in input_ingredients:
        input_objects.append(ingredient["object"])

    candidate_FUs = []
    for i in candidates:
        FU = functional_units[i]
        candidate_FUs.append(FU)
    # sort the candidate FUs based on the number of input objects
    # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects
    candidate_FUs.sort(key=lambda x: len(x.input_nodes))

    best_score = -1
    best_candidate = None
    for fu in candidate_FUs:

        # create the candidate ingredient list with all input output  object and their ingredients
        candidate_ingredient_list = []
        for _input in fu.input_nodes:
            candidate_ingredient_list.append(_input.label)
            candidate_ingredient_list += _input.ingredients

        for _output in fu.output_nodes:
            candidate_ingredient_list.append(_output.label)
            candidate_ingredient_list += _output.ingredients

        # remove the utensils
        candidate_ingredient_list = list(filter(
            lambda s: s not in utensils, candidate_ingredient_list))

        candidate_ingredient_list = list(set(candidate_ingredient_list))

        score = compare_two_recipe(input_ingredients=input_objects,
                                   candidate_recipe_ingredients=candidate_ingredient_list)
        if score > best_score:
            best_candidate = fu
            best_score = score

    return best_candidate.id
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
                    goal_node.id = candidate["id"]
    return goal_node


# -----------------------------------------------------------------------------------------------------------------------------#
# Given a goal node, this method finds the reference task tree
# The search uses heuristic (ingredient overlap) to select a FU from candidate FUs.


def extract_reference_task_tree(functional_units=[], object_nodes=[], object_to_FU_map={},
                                kitchen_items=[], input_ingredients=[], goal_node=None):
    """
        parameters: a list of functioal units, a list of object nodes,
                    object to functional unit mapping, list of kitchen items,
                    a goal node

                    object_to_FU_map {
                        key = object index
                        value = list of index of functional units
                    }

                    function
        returns: a task tree that consists some functional units
    """

    # list of indices of functional units
    reference_task_tree = []

    # list of object indices that need to be searched
    items_to_search = []

    # find the index of the goal node in object node list
    items_to_search.append(goal_node.id)

    # list of item already explored
    items_already_searched = []

    while len(items_to_search) > 0:
        current_item_index = items_to_search.pop(0)  # pop the first element

        if current_item_index in items_already_searched:
            continue

        else:
            items_already_searched.append(current_item_index)

        current_item = object_nodes[current_item_index]

        if not check_if_exist_in_kitchen(kitchen_items, current_item):

            candidate_units = object_to_FU_map[current_item_index]

            best_candidate_idx = select_best_candidate(
                input_ingredients, candidate_units, functional_units)

            # if an fu is already taken, do not process it again
            if best_candidate_idx in reference_task_tree:
                continue

            reference_task_tree.append(best_candidate_idx)

            # all input of the selected FU need to be explored
            for node in functional_units[best_candidate_idx].input_nodes:
                node_idx = node.id
                if node_idx not in items_to_search:

                    # if in the input nodes, we have bowl contains {onion} and onion, chopped, in [bowl]
                    # explore only onion, chopped, in bowl
                    flag = True
                    if node.label in utensils and len(node.ingredients) == 1:
                        for node2 in functional_units[best_candidate_idx].input_nodes:
                            if node2.label == node.ingredients[0] and node2.container == node.label:

                                flag = False
                                break
                    if flag:
                        items_to_search.append(node_idx)

    # reverse the task tree
    reference_task_tree.reverse()

    # create a list of functional unit from the indices of reference_task_tree
    task_tree_units = []
    for i in reference_task_tree:
        # creating a copy to make sure that modifying a FU does not affect future search
        FU = copy.deepcopy(functional_units[i])
        task_tree_units.append(FU)

    return task_tree_units

# -----------------------------------------------------------------------------------------------------------------------------#

# remove FU if it is invalid


def check_fu_valid(FU):
    if len(FU.input_nodes) == 0 or len(FU.output_nodes) == 0:
        return False

    val = 0
    # if valid FU, val will be equal to 2, otherwise less than 2
    for node in FU.input_nodes:
        if node.label not in utensils:
            val += 1

        else:
            for ing in node.ingredients:
                if ing not in utensils:
                    val += 1
                    break
        if val == 1:
            break

    for node in FU.output_nodes:
        if node.label not in utensils:
            val += 1

        else:
            for ing in node.ingredients:
                if ing not in utensils:
                    val += 1
                    break
        if val == 2:
            break

    if val != 2:
        return False
    else:
        cnt = 0
        for _input in FU.input_nodes:
            for _output in FU.output_nodes:
                if _input.check_object_equal(_output):
                    cnt += 1
                    break

        if cnt == len(FU.input_nodes):
            return False

    return True

# -----------------------------------------------------------------------------------------------------------------------------#

# Given a task tree, this method removes the ingredient that
# are not part of the input ingredients


def remove_extra_ingredients(final_task_tree=[], input_ingredients=[]):
    """
        parameters: a task tree as a list of functioal units,
                    input ingredients {object,state}

        returns: modified task tree that consists some functional units
    """

    task_tree = copy.deepcopy(final_task_tree)

    objects_to_keep = []

    for ingredient in input_ingredients:
        objects_to_keep.append(ingredient['object'])

    objects_to_keep += default_ingredients
    # remove extra ingredient from each FU
    for fu in task_tree:
        temp_input_nodes = []
        for node in fu.input_nodes:
            if node.label in objects_to_keep or \
                    (node.label in utensils and len(node.ingredients) == 0):
                temp_input_nodes.append(node)
                continue

            node.ingredients = list(
                set(node.ingredients) & set(objects_to_keep))

            if len(node.ingredients) > 0:

                temp_input_nodes.append(node)

        fu.input_nodes = temp_input_nodes
        temp_output_nodes = []
        for node in fu.output_nodes:
            if node.label in objects_to_keep or \
                    (node.label in utensils and len(node.ingredients) == 0):
                temp_output_nodes.append(node)
                continue

            node.ingredients = list(
                set(node.ingredients) & set(objects_to_keep))
            if len(node.ingredients) > 0:
                temp_output_nodes.append(node)

        fu.output_nodes = temp_output_nodes

    return task_tree


# -----------------------------------------------------------------------------------------------------------------------------#

# Given a reference task tree, this method modifies it to
# so that it is aligned with input ingredients.
# Major step: food prep, substituion, deletion of extra ingredients

def modify_reference_task_tree(reference_task_tree=[], input_ingredients=[]):
    """
        parameters: a task tree as a list of functioal units,
                    input ingredients {object,state}

        returns: modified task tree that consists some functional units
    """

    task_tree = copy.deepcopy(reference_task_tree)

    ingredient_mapping = find_ingredient_mapping(task_tree, input_ingredients)
    for ingredient in ingredient_mapping:

        # if the mapping exists in reference task tree, we do not need to search in FOON
        if ingredient["mapping_source"] == "reference_task_tree":
            mapped_object = ingredient_mapping[ingredient]['object']

            # substitue object in the task tree
            for fu in task_tree:
                for node in fu.input_nodes:
                    if node.label == mapped_object:
                        node.label = ingredient
                    if mapped_object in node.ingredients:
                        idx = node.ingredients.index(mapped_object)
                        node.ingredients[idx] = ingredient

                for node in fu.output_nodes:
                    if node.label == mapped_object:
                        node.label = ingredient
                    if mapped_object in node.ingredients:
                        idx = node.ingredients.index(mapped_object)
                        node.ingredients[idx] = ingredient

        else:  # mapping exists in foon but not in reference tree

            # we need to search in foon for the food prep steps
            continue

    return task_tree
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
# this method saves the task tree

def save_paths_to_file(task_tree, path):

    print('writing generated task tree to ', path)
    _file = open(path, 'w')

    _file.write('//\n')
    for FU in task_tree:
        if check_fu_valid(FU):
            _file.write(FU.get_FU_as_text() + "\n")
    _file.close()

# -----------------------------------------------------------------------------------------------------------------------------#
# this method creates the task using three major steps mentioned in the paper


def retrieval(functional_units, object_nodes, object_to_FU_map, recipe_id, dish_type, input_ingredients):

    # step 1: find the reference goal node
    reference_goal_node = find_goal_node(dish_type, input_ingredients)
    print("-------- REFERENCE GOAL NODE --------")
    reference_goal_node.print()

    # step 2: find the reference task tree
    print("extracting reference task tree")
    reference_task_tree = extract_reference_task_tree(
        functional_units, object_nodes, object_to_FU_map, kitchen_items, input_ingredients, reference_goal_node)

    # save the reference task tree
    output_dir = os.path.join('output', 'reference_task_tree', dish_type)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, recipe_id + '.txt')
    save_paths_to_file(reference_task_tree, output_path)

    # step 3: modify the reference task tree
    final_task_tree = modify_reference_task_tree(
        reference_task_tree=reference_task_tree, input_ingredients=input_ingredients)

    final_task_tree = remove_extra_ingredients(
        final_task_tree, input_ingredients)

    # save the final task tree
    output_dir = os.path.join('output', 'final_task_tree', dish_type)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, recipe_id + '.txt')
    save_paths_to_file(final_task_tree, output_path)


# -----------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":

    # construct the graph
    print('-- Reading universal foon from', foon_pkl)
    functional_units, object_nodes, object_to_FU_map = read_universal_foon()

    # selected_catagory = ['salad', 'drinks', 'omelette',
    #                      'cake', 'soup', 'bread', 'noodle', 'rice']

    #selected_category = ['salad', 'omelette', 'rice', 'soup', 'drinks']
    selected_category = ['drinks']

    for category in selected_category:
        input_dir = 'input/' + category
        for input_file in os.listdir(input_dir):
            input_file = os.path.join(input_dir, input_file)
            recipe_id, dish_type, ingredients = process_input(input_file)

            # do the retrieval
            print("-- STARTING RETRIEVAL")
            retrieval(functional_units, object_nodes, object_to_FU_map,
                      recipe_id, dish_type, ingredients)
