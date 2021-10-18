from configparser import ConfigParser
import copy
from nltk.corpus import wordnet
import json

# -----------------------------------------------------------------------------------------------------------------------------#
# --- Global variables -- #

nlp_vector_map = {}

similarity_map = {}

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

similarity_threshold = float(config["constant"]["similarity_threshold"])
word2vec_model = config["constant"]["word2vec_model"]
utensils_path = config['info']['utensils']
object_state_map_path = config['info']['object_state_map']


# load word2vec model
if word2vec_model == "large":
    import spacy
    #nlp_model = spacy.load('en_vectors_web_lg', disable=["tagger", "parser"])
    nlp_model = spacy.load(
        'en_vectors_web_lg', disable=["tagger", "parser"])
else:
    import en_core_web_sm
    nlp_model = en_core_web_sm.load()


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


utensils = get_utensils()
object_state_map = json.load(open(object_state_map_path))
# -----------------------------------------------------------------------------------------------------------------------------#


def get_singular_form(label):
    """
        parameters: object label as string
        returns: singular form of the object label
    """
    import inflect

    inflect_engine = inflect.engine()

    if inflect_engine.singular_noun(label) is not False:
        label = inflect_engine.singular_noun(label)
    return label

# -----------------------------------------------------------------------------------------------------------------------------#


def get_object_similarity(object1, object2):
    # object1 = a word string, object2 = a word string
    # object1 = get_singular_form(object1)
    # object2 = get_singular_form(object2)

    return get_doc_similarity(get_nlp_vector(object1), get_nlp_vector(object2))

# -----------------------------------------------------------------------------------------------------------------------------#


def get_synonyms(word):
    for synset in wordnet.synsets(word):
        for lemma in synset.lemma_names():
            print(lemma)

# -----------------------------------------------------------------------------------------------------------------------------#


def get_nlp_vector(object):
    if object in nlp_vector_map:
        doc = nlp_vector_map[object]
    else:
        doc = nlp_model(object)
        nlp_vector_map[object] = doc

    return doc
# -----------------------------------------------------------------------------------------------------------------------------#


def get_doc_similarity(doc1, doc2):
    doc = str(doc1) + str(doc2)
    if doc in similarity_map:
        similarity = similarity_map[doc]
    else:
        similarity = doc1.similarity(doc2)
        similarity_map[doc] = similarity

    return similarity

# -----------------------------------------------------------------------------------------------------------------------------#


def compare_two_recipe(input_ingredients, candidate_recipe_ingredients):

    curr_recipe = copy.deepcopy(candidate_recipe_ingredients)

    score = 0
    for input_item in input_ingredients:
        doc1 = get_nlp_vector(input_item.replace('_', ' '))
        for recipe_item in reversed(curr_recipe):
            doc2 = get_nlp_vector(recipe_item)
            similarity = get_doc_similarity(doc1, doc2)
            if similarity > similarity_threshold:
                score += 1

                # if a item is already matched, remove it

                curr_recipe.remove(recipe_item)
                break
    return score


# -----------------------------------------------------------------------------------------------------------------------------#
# This method finds a mapping of the input ingredients in the reference task tree
# If a good mapping is not found in the reference tree, we will find mapping from FOON

def find_ingredient_mapping_in_reference_tree(task_tree, input_ingredients):
    # task tree: list of functional units
    # input ingredients: list of {object, state} pair

    # list of objects
    reference_tree_objects = []
    for fu in task_tree:
        for node in fu.input_nodes:

            # ignore the gaol nodes
            if node.recipe_category != -1:
                continue
            reference_tree_objects.append(node.label)
            reference_tree_objects += node.ingredients

        for node in fu.output_nodes:
            # ignore the gaol nodes
            if node.recipe_category != -1:
                continue
            reference_tree_objects.append(node.label)
            reference_tree_objects += node.ingredients

    reference_tree_objects = list(set(reference_tree_objects))
    reference_tree_objects = list(filter(
        lambda s: s not in utensils, reference_tree_objects))
    # generate similarity for all possible pairs between
    # task tree ingredient and given ingredients
    similarity_scores = {}
    for ingredient in input_ingredients:

        given_object = ingredient['object']

        similarity_scores[given_object] = []
        for tree_object in reference_tree_objects:
            score = get_object_similarity(given_object, tree_object)
            similarity_scores[given_object].append(
                {
                    "object": tree_object,
                    "score": score
                }
            )

    # sort the mappings based on similarity score
    for item in similarity_scores:
        similarity_scores[item].sort(key=lambda x: x["score"], reverse=True)

    ingredient_mapping = {}
    object_mapped = []

    for item in similarity_scores:
        input_object = item
        tree_object = similarity_scores[item][0]["object"]
        score = similarity_scores[item][0]["score"]
        if score == 1.0:
            ingredient_mapping[input_object] = {
                "object": tree_object,
                "score": score
            }
            object_mapped.append(tree_object)
            break

    for item in similarity_scores:
        # already mapping done
        if item in ingredient_mapping:
            continue
        for candidate in similarity_scores[item]:
            input_object = item
            tree_object = candidate["object"]
            score = candidate["score"]
            if tree_object not in object_mapped and score > similarity_threshold:
                ingredient_mapping[input_object] = {
                    "object": tree_object,
                    "score": score,
                    "is_found_in_tree": True
                }
                object_mapped.append(tree_object)
                break

    return ingredient_mapping


# -----------------------------------------------------------------------------------------------------------------------------#
def find_ingredient_mapping_in_foon(ingredient_mapping={}, input_ingredients=[], object_mapped=[]):
    # ingredient_mapping: a mapping return from find_ingredient_mapping_in_reference_tree function
    # input ingredients: list of {object, state} pair
    # object_mapped: list of objects that is already mapped in the reference tree

    for _input in input_ingredients:
    return ingredient_mapping


# -----------------------------------------------------------------------------------------------------------------------------#
def find_ingredient_mapping(task_tree, input_ingredients):
    ingredient_mapping = find_ingredient_mapping_in_reference_tree(
        task_tree, input_ingredients)

    return find_ingredient_mapping_in_foon(ingredient_mapping, input_ingredients)

# -----------------------------------------------------------------------------------------------------------------------------#

# # this method checks all objects in FOON and
# # find the one that has maximum state overlap with this object
# def find_equivalent_ingredient_on_state_overlap(object_list, given_object):
#     given_object = get_singular_form(given_object)
#     if given_object not in object_state_map:
#         return None, 0

#     given_object_state = object_state_map[given_object]

#     if len(given_object_state) == 0:
#         return None, 0

#     best_overlap_score = -2
#     best_match = None
#     for object in object_list:
#         if object not in object_state_map:
#             continue
#         candidate_object_state = object_state_map[object]

#         overlap = len(list(set(given_object_state) &
#                       set(candidate_object_state)))

#         if overlap > best_overlap_score and overlap > 2:
#             best_overlap_score = overlap
#             best_match = object

#     return best_match, best_overlap_score/len(given_object_state)
