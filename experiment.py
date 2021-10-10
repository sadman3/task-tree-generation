import pickle
import json
from configparser import ConfigParser
import shutil
import os

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

    categorized_recipe = {}

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

                        if ing != '<pad>' and state != '<pad>':
                            _input['ingredients'].append(
                                {
                                    "object": ing,
                                    "state": state
                                }
                            )

                    json.dump(_input, f, indent=7)
                    f.close()
                    # print('input created: ', input_category_dir +
                    #       '/' + id + '.json')
                    break

# -----------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    # kitchen = json.load(open('info/kitchen.json'))
    # for x in kitchen:
    #     if len(x["ingredients"]) > 1:
    #         print(x)
    prepare_input()
