import pickle
import json
from configparser import ConfigParser

# -----------------------------------------------------------------------------------------------------------------------------#

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

kitchen_path = config['info']['kitchen']
foon_pkl = config['source']['foon_pkl']
# -----------------------------------------------------------------------------------------------------------------------------#

# Creates a kitchen file based on the nodes that are only used as input


def prepare_kitchen(foon_path=foon_pkl, kitchen_path=kitchen_path):

    # load universal foon pickle file
    pickle_data = pickle.load(open(foon_path, 'rb'))
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    start_nodes = []
    # check which object does not have any FU mapping
    for object_index, object in enumerate(object_nodes):
        if object_index not in object_to_FU_map:
            object_json = object.get_object_as_json()
            start_nodes.append(object_json)

    F = open(kitchen_path, 'w')
    json.dump(start_nodes, F, indent=4)


# -----------------------------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    prepare_kitchen()
