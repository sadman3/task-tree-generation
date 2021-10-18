import os
import json
from FOON_class import FunctionalUnit, Object

utensils = []
with open('info/utensils.txt', 'r') as f:
    for line in f:
        utensils.append(line.rstrip())

ignored_objects = ['water']

selected_category = ['salad', 'omelette', 'rice', 'soup', 'drinks']


def get_FU_list(filepath):
    """
        parameters: path of a subgraph text file
        returns: a list of FU
    """
    lines = open(filepath, 'r')

    FU_list = []

    FU = FunctionalUnit()
    new_object = None
    is_input = True

    for line in lines:

        if line.startswith("//"):
            # functional unit separators:

            # check if an object is constructed
            if new_object:
                FU.output_nodes.append(new_object)
                new_object = None
                # if FU is already constructed, add it to the FU list
            if FU.motion_node:
                FU_list.append(FU)
                FU = FunctionalUnit()

            is_input = True

            continue

        label = line.split("\t")
        if len(label) < 2:
            # -- this is to make sure that we skip incorrect lines
            print(
                ' -- WARNING: there is a line that is possibly incorrect : ' + str(label))
            continue

        label[1] = label[1].lower().rstrip()

        if line.startswith("O"):
            if new_object:
                # decide whether to add as input or output node
                if not is_input:
                    FU.output_nodes.append(new_object)
                else:
                    FU.input_nodes.append(new_object)

            # len = 3 for goal node
            new_object = Object(label[1])
            if len(label) > 2:
                new_object.object_in_motion = label[2]
            if len(label) > 3:
                new_object.recipe_category = label[3].rstrip()

        if line.startswith("S"):

            if len(label) > 2:
                # add the ingredients to current object
                if label[2].startswith('{'):
                    ingredients = label[2].rstrip().replace(
                        '{', '').replace('}', '')
                    new_object.ingredients = ingredients.split(',')

                # add the container to current object
                elif label[2].startswith('['):
                    container = label[2].rstrip().replace(
                        '[', '').replace(']', '')
                    new_object.container = container

            else:
                new_object.states.append(label[1])

        if line.startswith("M"):
            # append the current object
            FU.input_nodes.append(new_object)
            new_object = None
            is_input = False
            FU.motion_node = label[1]

    return FU_list


def convert_to_json(source_dir='output', target_dir='output_json'):
    for currentpath, folders, files in os.walk(source_dir):
        progress_line_dir = currentpath.replace(source_dir, target_dir)

        temp = currentpath.split('/')[-1]
        if temp not in selected_category:
            continue

        os.makedirs(progress_line_dir, exist_ok=True)
        for file in files:
            FU_list = get_FU_list(os.path.join(currentpath, file))
            task_tree_json = []
            for FU in FU_list:
                task_tree_json.append(FU.get_FU_as_json())

            progress_line_path = os.path.join(
                progress_line_dir, file.replace('.txt', '.json'))
            F = open(progress_line_path, 'w')
            json.dump(task_tree_json, F, indent=4)

            F.close()


def save_progress_line(source_path, target_path):
    print('creating progress line for ', source_path)
    state_trace = {}

    task_tree = json.load(open(source_path, 'r'))

    for fu in task_tree:
        motion = fu["motion_node"].replace('*', '')

        # first check objects only, not containers
        object_traced = []
        for node in fu['input_nodes']:
            object = node['label']
            if object in ignored_objects or object in utensils:
                continue
            if object not in state_trace and len(node['states']) > 0:
                # keep track of state and location separately

                state_trace[object] = {
                    "state": [],
                    "motion": [],
                    "end_product": None
                }

            new_state = {}
            new_state["physical_state"] = []
            new_state["location"] = []
            if len(node["states"]) > 0:
                object_traced.append(object)
            state_list = []
            for state in node["states"]:
                state_list.append(state)

                if node['container'] is not None:
                    # location_list.append
                    new_state["location"] = node['container']

                new_state["physical_state"] = ','.join(state_list)
                state_trace[object]["state"].append(new_state)
                state_trace[object]["motion"].append(motion)

        for node in fu['input_nodes']:
            object = node['label']
            # object already traced for this FU
            if object in object_traced:
                continue

            if (object in utensils and len(node["ingredients"]) == 0) or object in ignored_objects:
                continue

            if object not in state_trace and object not in utensils:
                # keep track of state and location separately
                state_trace[object] = {
                    "state": [],
                    "motion": [],
                    "end_product": None
                }
            new_state = {}
            new_state["physical_state"] = []
            new_state["location"] = []

            if object not in utensils:
                state_list = []
                for state in node["states"]:
                    state_list.append(state)

                if node['container'] is not None:
                    new_state["location"] = node['container']

                new_state["physical_state"] = ','.join(state_list)
                state_trace[object]["state"].append(new_state)
                state_trace[object]["motion"].append(motion)

            else:
                state_list = []
                for state in node['states']:
                    state_list.append(state)

                new_state["physical_state"] = ','.join(state_list)
                new_state["location"] = object
                for ing in node["ingredients"]:

                    if ing in object_traced or ing in ignored_objects:
                        continue
                    if ing not in state_trace:
                        state_trace[ing] = {
                            "state": [],
                            "motion": [],
                            "end_product": None
                        }

                    state_trace[ing]["state"].append(new_state)
                    state_trace[ing]["motion"].append(motion)

    # remove consecutive duplicate state
    for ing in state_trace:

        temp_motion = []
        temp_state = []
        states = state_trace[ing]["state"]
        motion = state_trace[ing]["motion"]
        for i in range(len(states)):
            if i < len(states) - 1 and states[i]["physical_state"] == states[i+1]["physical_state"] and states[i]["location"] == states[i+1]["location"]:
                continue

            if i < len(states) - 1 and (states[i]["physical_state"] == "" or states[i+1]["physical_state"] == "") and states[i]["location"] == states[i+1]["location"]:
                continue

            else:
                temp_motion.append(motion[i])
                temp_state.append(states[i])

        state_trace[ing]["state"] = temp_state
        state_trace[ing]["motion"] = temp_motion

    # find the node that has been most frequent used as a end node
    most_freq_end_node = {}
    last_fu_idx = len(task_tree) - 1
    last_fu = task_tree[last_fu_idx]
    candidates = []
    for node in last_fu["output_nodes"]:
        obj = node["label"]
        if obj not in utensils:
            candidates.append(obj)

    for fu in task_tree:
        for node in fu['output_nodes']:
            object = node['label']

            for ing in node['ingredients']:

                # if len(ingredients) > 0 and ing not in ingredients:
                #     continue

                if object not in utensils and ing in state_trace:
                    state_trace[ing]['end_product'] = object
                    # motion = fu["motion_node"].replace('*', '')
                    # state_trace[ing]["motion"].append(motion)
                    if object in candidates:
                        most_freq_end_node[object] = most_freq_end_node.get(
                            object, 0) + 1

    # # if len(most_freq_end_node) > 0:
    # #     most_freq_end_node = max(most_freq_end_node.items(), key=operator.itemgetter(1))[0]

    # #     for ing in state_trace:
    # #         if not state_trace[ing]["end_product"] and ing != most_freq_end_node:
    # #             state_trace[ing]["end_product"] = most_freq_end_node

    # for object in state_trace:
    #     print(object + ': ')
    #     print('state:', state_trace[object]['state'])
    #     print('motion:', ' --> '.join(state_trace[object]['motion']))
    #     print('end product:', state_trace[object]['end_product'])
    #     print('\n')

    progress_line = []
    for ing in state_trace:
        progress_line.append(
            {
                "ingredient": ing,
                "state": state_trace[ing]["state"],
                "motion": state_trace[ing]["motion"],
                "end_product": state_trace[ing]["end_product"]
            }
        )

    with open(target_path, 'w') as f:
        json.dump(progress_line, f, indent=7)
    print('progress line stored for ', source_path)


if __name__ == '__main__':

    # convert_to_json('output', 'output_json')

    source_dir = 'output_json'
    target_dir = 'progress_line'

    for currentpath, folders, files in os.walk(source_dir):
        temp = currentpath.split('/')[-1]
        if temp not in selected_category:
            continue
        subdir = currentpath.replace(source_dir, target_dir)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        for file in files:
            source_path = os.path.join(currentpath, file)

            target_path = source_path.replace(source_dir, target_dir)
            save_progress_line(source_path, target_path)
