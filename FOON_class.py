class Object:
    # NOTE: -- an object node is any item that is used in the cooking/manipulation procedure.
    # 	an Object has a object label and state label to describe the state or condition it is observed in.
    # -- an Object may have multiple states! This is given by multiple lines of 'S' in the textfiles.

    """
    A object node object.

    Constructor Parameters:
            objectLabel (str): A string referring to the object's label

    """

    # NOTE: constructor for Object node:
    def __init__(self, label=None):
        # -- member variables
        self.label = label
        self.states = []
        self.ingredients = []
        self.container = None
        self.object_in_motion = 0
        self.recipe_category = -1  # -1, if not a goal node, else it will have a category id

    def get_ingredients_as_text(self):
        ingredients_list = self.ingredients
        ingredients = str()

        for x in range(len(ingredients_list)):
            ingredients += ingredients_list[x]
            if x < len(ingredients_list) - 1:
                ingredients += ','
            # endif
        # endfor

        return '{' + ingredients + '}'

    def get_object_as_text(self):
        str = "O" + "\t" + self.label
        for state in self.states:
            str += "\nS" + "\t" + state
        if len(self.ingredients) > 0:
            str += '\nS' + "\t" + 'contains' + "\t" + self.get_ingredients_as_text()
        if self.container:
            str += '\nS' + "\t" + 'in' + "\t" + "[" + self.container + "]"

        str += "\n"
        return str

    def print(self):
        print(self.get_object_as_text())

    # checks if two objects are same
    def check_object_equal(self, T):
        if self.label == T.label and sorted(self.states) == sorted(T.states) \
            and sorted(self.ingredients) == sorted(T.ingredients) \
                and self.container == T.container:
            return True
        return False

    # checks if an objet exist in a list of objects
    def check_object_exist(self, object_list):
        for index, object in enumerate(object_list):
            if self.check_object_equal(object):
                return index
        return -1


class FunctionalUnit:
    def __init__(self):
        # NOTE: list of input and output object nodes (which use the Object class defined above):
        self.input_nodes = []
        self.output_nodes = []
        self.motion_node = None
    # enddef

    def get_FU_as_text(self):
        str = ""
        for node in self.input_nodes:
            str += node.get_object_as_text()
        str += "M" + "\t" + self.motion_node + "\n"
        for node in self.output_nodes:
            str += node.get_object_as_text()
        str += "//"
        return str

    def print(self):
        print(self.get_FU_as_text())

    def check_if_FU_exist(self, functional_units):

        for FU in functional_units:
            if self.motion_node != FU.motion_node or \
                len(self.input_nodes) != len(FU.input_nodes) or \
                    len(self.output_nodes) != len(FU.output_nodes):
                continue

            input_found = 0
            for node in self.input_nodes:
                if node.check_object_exist(FU.input_nodes) != 1:
                    input_found += 1

            output_found = 0
            for node in self.output_nodes:
                if node.check_object_exist(FU.output_nodes) != -1:
                    output_found += 1

            if input_found == len(self.input_nodes) and output_found == len(self.output_nodes):
                return True

        return False
