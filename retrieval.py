import FOON_class as FOON


def parse_file(file):
    _file = open(file, 'r')
    items = _file.read().splitlines()
    item = None
    item_list = []

    for line in items:
        if line.startswith("O"):
            # -- we have an Object already in consideration which we were appending states to:
            if item:
                item_list.append(item)

            # -- this is an Object node, get the Object identifier by splitting first instance of O
            objectParts = line.split("O")
            objectParts = objectParts[1].split("\t")

            # -- create a new object which is equal to the kitchenItem and add it to the list:
            item = FOON.Object(objectID=int(
                objectParts[0]), objectLabel=objectParts[1])

        elif line.startswith("S"):
            # -- get the Object's state identifier by splitting first instance of S
            stateParts = line.split("S")
            stateParts = stateParts[1].split("\t")
            stateParts = list(filter(None, stateParts))

            # -- check if this object is a container or has ingredients:
            container = None
            list_ingredients = []
            if len(stateParts) > 2:
                if '{' in stateParts[2]:
                    # NOTE: all ingredients are enclosed in curly brackets:
                    ingredients = [stateParts[2]]
                    ingredients = ingredients[0].split("{")
                    ingredients = ingredients[1].split("}")

                    # -- we then need to make sure that there are ingredients to be read.
                    if len(ingredients) > 0:
                        ingredients = ingredients[0].split(",")
                        for I in ingredients:
                            list_ingredients.append(I)
                elif '[' in stateParts[2]:
                    # NOTE: a container is enclosed in square brackets (e.g. in [bowl]):

                    container = stateParts[2].replace('[', '').replace(']', '')
                else:
                    print(' -- WARNING: possibly incorrect or unexpected extra entry in line ' +
                          str(items.index(line)) + '? > ' + str(stateParts[2]))
                    pass

            item.addNewState(
                [int(stateParts[0]), stateParts[1], container])

            if list_ingredients:
                item.setIngredients(list_ingredients)

        else:
            pass
    # endfor

    item_list.append(item)

    _file.close()  # -- Don't forget to close the file once we are done!
    return item_list
# enddef


if __name__ == '__main__':
    kitchen_items = parse_file('kitchen.txt')

    for item in kitchen_items:
        item.printObject()
        print()

    goal_nodes = parse_file('goal_nodes.txt')

    for node in goal_nodes:
        node.printObject()
        print()
