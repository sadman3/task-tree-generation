import pickle
import json
from configparser import ConfigParser
import os
import utils

# -----------------------------------------------------------------------------------------------------------------------------#

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

# -----------------------------------------------------------------------------------------------------------------------------#


def prepare_input(path='recipe1m_merged.pkl'):

    # how many recipe to create for each category
    number_of_recipe = 120

    recipes = pickle.load(open(path, 'rb'))

    print('recipe1m loaded')

    selected_catagory = ['salad', 'drinks', 'omelette',
                         'cake', 'soup', 'bread', 'noodle', 'rice', 'smoothie']

    invalid_ingredient = ['juice']

    invalid_state = ['unknown']

    categorized_recipe = {}
    cnt = 0
    for recipe in recipes:
        id = recipe["id"]
        title = recipe["title"]
        if 'drinks' in title or 'smoothie' in title or 'juice' in title or 'tea' in title or 'coffee' in title:
            cnt += 1
    print(cnt)
    exit(0)
    for recipe in recipes:
        id = recipe["id"]
        title = recipe["title"]

        for category in selected_catagory:
            # if os.path.exists(input_category_dir):
            #     shutil.rmtree(input_category_dir)

            # os.makedirs(input_category_dir)

            if category in title:
                if category == 'smoothie':
                    category = 'drinks'

                input_category_dir = os.path.join('input', category)

                categorized_recipe[category] = categorized_recipe.get(
                    category, 0) + 1
                if categorized_recipe[category] <= number_of_recipe:
                    f = open(input_category_dir +
                             '/' + id + '.json', 'w')
                    _input = {}
                    _input['id'] = recipe['id']
                    _input['type'] = category
                    _input['ingredients'] = []

                    for i in range(len(recipe['ingredients'])):
                        ing = recipe['ingredients'][i]
                        state = recipe['states'][i]

                        if ing != '<pad>' and ing not in invalid_ingredient and state != '<pad>' and state not in invalid_state:
                            _input['ingredients'].append(
                                {
                                    "object": utils.get_singular_form(ing).replace('_', ' '),
                                    "state": state.replace('_', ' ')
                                }
                            )

                    json.dump(_input, f, indent=7)
                    f.close()
                    # print('input created: ', input_category_dir +
                    #       '/' + id + '.json')
                    break

# -----------------------------------------------------------------------------------------------------------------------------#

# this function will first merge the subgraphs,
# then do the retrieval
# then converts the task tree to json
# then creats the progress line


def run_full_pipeline():
    import preprocess
    import retrieval
    import evaluate

    preprocess.merge()
    preprocess.prepare_kitchen()
    preprocess.save_all_object_states()
    print('-- MERGING DONE')

    print('-- Reading universal foon from')
    functional_units, object_nodes, object_to_FU_map = retrieval.read_universal_foon()

    selected_category = ['drinks']

    for category in selected_category:
        input_dir = 'input/' + category
        for input_file in os.listdir(input_dir):
            input_file = os.path.join(input_dir, input_file)
            recipe_id, dish_type, ingredients = retrieval.process_input(
                input_file)

            # do the retrieval
            print("-- STARTING RETRIEVAL")
            retrieval.retrieval(functional_units, object_nodes, object_to_FU_map,
                                recipe_id, dish_type, ingredients)

    evaluate.convert_to_json('output', 'output_json')

    source_dir = 'output_json'
    target_dir = 'progress_line'
    print('-- SAVING PROGRESS LINE')
    for currentpath, folders, files in os.walk(source_dir):
        temp = currentpath.split('/')[-1]
        if temp not in selected_category:
            continue
        subdir = currentpath.replace(source_dir, target_dir)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        for file in files:
            source_path = os.path.join(currentpath, file)

            target_path = source_path.replace(source_dir, target_dir)
            evaluate.save_progress_line(source_path, target_path)


if __name__ == "__main__":
    # kitchen = json.load(open('info/kitchen.json'))
    # for x in kitchen:
    #     if len(x["ingredients"]) > 1:
    #         print(x)
    prepare_input()

    # run_full_pipeline()
