from configparser import ConfigParser
import os
import json

# -----------------------------------------------------------------------------------------------------------------------------#

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)


subgraph_dir = config['source']['data_source']
dish_type_path = config["info"]["dish_type"]
recipe_category_path = config["info"]["recipe_category"]
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


def parse_subgraphs(source_dir=subgraph_dir):
    # preparing map to categorize existing foon recipes
    recipe_categories = {}
    categories = read_categories()
    for _, value in categories.items():
        recipe_categories[value] = []

    recipe_counter = 0

    for F in os.listdir(source_dir):
        if not F.endswith('.txt'):
            continue

        goal_node_object = {}
        goal_node_category = None
        is_goal_node = False
        unparsed_filepath = os.path.join(source_dir, F)
        parsed_filepath = os.path.join(source_dir, 'parsed.txt')
        unparsed_file = open(unparsed_filepath, "r")
        parsed_file = open(parsed_filepath, "w")

        recipe_counter += 1
        print('  -- Saving ' + unparsed_filepath +
              '..., counter = ', recipe_counter)

        for line in unparsed_file:
            if line.startswith("# Source:"):
                # -- new addition: note the source of the annotated video:
                parsed_file.write(line)
                continue

            if line.startswith("/"):
                # -- functional unit separators:
                parsed_file.write('//\n')
                continue

            label = line.split("\t")
            if len(label) < 2:
                # -- this is to make sure that we skip incorrect lines
                print(
                    ' -- WARNING: there is a line that is possibly incorrect : ' + str(label))
                continue

            parsed_line = ''

            label[1] = label[1].lower().rstrip()

            if line.startswith("O"):
                # len = 3 for goal node
                if len(label) > 3:
                    is_goal_node = True
                    parsed_line = 'O' + '\t' + \
                        label[1] + '\t' + label[2] + '\t' + \
                        str(label[3].rstrip()) + '\n'
                    goal_node_object['object_label'] = label[1]
                    goal_node_object['object_states'] = []
                    goal_node_object['ingredients'] = []
                    # add the goal node information to recipe category
                    category_id = label[3].rstrip()
                    goal_node_category = categories[category_id].rstrip()

                else:
                    is_goal_node = False
                    parsed_line = 'O' + '\t' + \
                        label[1] + '\t' + str(label[2].rstrip()) + '\n'

            if line.startswith("S"):
                if len(label) > 2:
                    parsed_line = 'S' + '\t' + \
                        label[1] + '\t' + label[2].rstrip() + '\n'
                    if is_goal_node and label[2].startswith('{'):
                        ingredients = label[2].rstrip().replace(
                            '{', '').replace('}', '')
                        goal_node_object['ingredients'] = ingredients.split(
                            ',')
                    if is_goal_node and label[2].startswith('['):
                        relater = label[2].rstrip().replace(
                            '[', '').replace(']', '')
                        goal_node_object['relater'] = relater

                else:
                    parsed_line = 'S' + '\t' + label[1] + '\n'

                if is_goal_node:
                    goal_node_object['object_states'].append(label[1])

            if line.startswith("M"):
                # new format of writing the timestamps
                if '<' in line:
                    parsed_line = 'M' + '\t' + \
                        label[1] + '\t' + label[2].rstrip() + '\n'
                else:
                    parsed_line = 'M' + '\t' + \
                        label[1] + '\t' + label[2] + \
                        '\t' + label[3].rstrip() + '\n'

            # write the updated line
            parsed_file.write(parsed_line)
        # endfor

        # close the open files
        parsed_file.close()
        unparsed_file.close()

        # replace the unparsed file with the parsed file
        os.rename(parsed_filepath, unparsed_filepath)

        recipe_categories[goal_node_category].append(goal_node_object)

    # endfor

    json.dump(recipe_categories, open(recipe_category_path, 'w'), indent=4)
    print('\n-- recipe categories created')
# -----------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    parse_subgraphs(subgraph_dir)
