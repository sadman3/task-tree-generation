import pickle
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


# creates the graph using adjacency list
# each object has a list of functional list where it is an output
def create_adjacency_list(filepath=foon_pkl):
    """
        parameters: path of universal foon (pickle file)
        returns: a map. key = object, value = list of functional units
    """


def retrieval():

    functional_units = pickle.load(open('FOON.pkl', 'rb'))

    functional_units[0].print()
    print(len(functional_units))


if __name__ == "__main__":
    retrieval()
