import spacy


def process_object_label(label):
    """
        parameters: object label as string
        returns: singular form of the object label
    """
    import inflect

    inflect_engine = inflect.engine()

    if inflect_engine.singular_noun(label) is not False:
        label = inflect_engine.singular_noun(label)
    print(label)


# def convert_obj_to_JSON(subgraph_txt) {
#     """
#         parameters: a subgraph file
#         returns: subgraph as a json
#     """

# }
