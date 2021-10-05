import pickle
from FOON_class import FunctionalUnit, Object


def retrieval():
    functional_units = pickle.load(open('FOON.pkl', 'rb'))

    functional_units[0].print()
    print(len(functional_units))


if __name__ == "__main__":
    retrieval()
