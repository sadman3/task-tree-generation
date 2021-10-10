import pickle
import json
from configparser import ConfigParser


# -----------------------------------------------------------------------------------------------------------------------------#

# load the config file
config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)

# -----------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    # kitchen = json.load(open('info/kitchen.json'))
    # for x in kitchen:
    #     if len(x["ingredients"]) > 1:
    #         print(x)

    a = [1, 2, 3]
    b = []

    print(sorted(a) == sorted(b))

    # while not q.empty():
    #     a = q.get()
    #     print(a)
