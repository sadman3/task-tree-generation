class Object:
    # NOTE: -- an object node is any item that is used in the cooking/manipulation procedure.
    # 	an Object has a state type and state label to describe the state or condition it is observed in.
    # -- an Object may have multiple states! This is given by multiple lines of 'S' in the textfiles.

    """
    A object node object.

    Constructor Parameters:
            objectID (int): An integer referring to the object's ID
            objectLabel (str): A string referring to the object's label

    """

    # NOTE: constructor for Object node:
    def __init__(self, objectID=None, objectLabel=None):
        # -- member variables
        self.type = objectID
        self.label = objectLabel
        self.objectStates = []
        self.objectIngredients = []

    # -- accessor methods for Objects:
    def getObjectType(self):
        return self.type

    def getStateType(self, X):
        return self.objectStates[X][0]

    def getStateLabel(self, X):
        return self.objectStates[X][1]

    def getObjectLabel(self):
        return self.label

    def setObjectLabel(self, L):
        self.label = L

    def setIngredients(self, L):
        self.objectIngredients = list(L)

    def getContainer(self, X):
        return self.objectStates[X][2]

    # NOTE: objects can have multiple states, so we are working with a list of states:
    def getStatesList(self):
        return list(self.objectStates)

    def getIngredients(self):
        return list(self.objectIngredients)

    def getIngredientsText(self):
        ingredients_list = self.getIngredients()
        ingredients = str()

        for x in range(len(ingredients_list)):
            ingredients += ingredients_list[x]
            if x < len(ingredients_list) - 1:
                ingredients += ','
            # endif
        # endfor

        return '{' + ingredients + '}'

    def addNewState(self, T):
        for S in self.objectStates:
            # -- this is to check whether we are potentially adding a duplicate state type or label:
            if S[0] == T[0] and S[1] == T[1] and S[1] and S[2] == T[2]:
                print(
                    " -- WARNING: Duplicate state detected when adding :"
                    + str(T)
                    + " to object "
                    + str(self.getObjectLabel())
                    + "!"
                )
                return
            # endif
        # endfor
        self.objectStates.append(list(T))
        self.objectStates.sort()

    def printObject(self):
        print("O" + str(self.getObjectType()) + "\t" + self.getObjectLabel())
        for x in range(len(self.getStatesList())):
            if "contains" in self.getStateLabel(
                x
            ) or "ingredients" in self.getStateLabel(x):
                print(
                    "S"
                    + str(self.getStateType(x))
                    + "\t"
                    + self.getStateLabel(x)
                    + "\t"
                    + self.getIngredientsText()
                )
            else:
                print(
                    "S"
                    + str(self.getStateType(x))
                    + "\t"
                    + self.getStateLabel(x)
                    + (
                        str("\t " + "[" + str(self.getContainer(x)) + "]")
                        if self.getContainer(x)
                        else ""
                    )
                )
        # endfor


class Motion:
    # NOTE: -- a Motion node is the other node that is found in the bipartite FOON graph.
    # -- a Motion node reflects a manipulation or non-manipulation action that is needed to change (some) objects from one state to another
    # -- a Motion node simply has a type that describes what it is along with a label.

    '''
    A motion node object.

    Constructor Parameters:
            motionID (int): An integer referring to the motion's ID
            motionLabel (str): A string referring to the motion's label
    '''

    # NOTE: constructor for Motion node:
    def __init__(self, motionID=None, motionLabel=None):
        # -- member variables
        self.type = motionID
        self.label = motionLabel


class FunctionalUnit:
    def __init__(self):
        # NOTE: list of input and output object nodes (which use the Object class defined above):
        self.inputNodes = []
        self.outputNodes = []
        self.motionNode = None
    # enddef
