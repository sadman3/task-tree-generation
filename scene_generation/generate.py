import json
import random
import copy


def generate_different_scenes(motion, num_scene=10):

    f = open("parameter_space/{}.json".format(motion), 'r')
    setting = json.load(f)
    f.close()

    f = open("generated_scene/{}.json".format(motion), 'w')

    parameter_space = setting['parameter-space']
    action = setting['action']

    all_scenes = []
    track_scene = {}
    for scene in parameter_space:
        cnt = 0
        object = scene['object']
        portions = scene['portions']
        source = scene['source']
        target = scene['target']
        utensils = scene['utensils']
        while cnt < num_scene:
            selected_utensil = ""
            selected_source = ""
            selected_target = ""
            selected_portion = ""
            if len(source) > 0:
                selected_source = source[random.randint(0, len(source) - 1)]
            if len(target) > 0:
                selected_target = target[random.randint(0, len(target) - 1)]
            selected_utensil = ""
            if len(utensils) > 0:
                selected_utensil = utensils[random.randint(
                    0, len(utensils) - 1)]
            if len(portions) > 0:
                selected_portion = portions[random.randint(
                    0, len(portions) - 1)]
            cnt += 1
            generated_scene = copy.deepcopy(action)

            generated_scene['input'] = "{} {}".format(selected_portion, object)

            pre_condtions = []
            for condition in generated_scene["pre-conditions"]:
                condition = condition.replace("{object}", object)
                condition = condition.replace("{portions}", selected_portion)
                condition = condition.replace("{source}", selected_source)
                condition = condition.replace("{target}", selected_target)
                condition = condition.replace("{utensils}", selected_utensil)

                pre_condtions.append(condition)
            generated_scene["pre-conditions"] = pre_condtions

            steps = []
            for step in generated_scene["steps"]:
                step = step.replace("{object}", object)
                step = step.replace("{source}", selected_source)
                step = step.replace("{target}", selected_target)
                step = step.replace("{utensils}", selected_utensil)
                steps.append(step)
            generated_scene["steps"] = steps

            operating_condtions = []
            for condition in generated_scene["operating-conditions"]:
                condition = condition.replace("{object}", object)
                condition = condition.replace("{source}", selected_source)
                condition = condition.replace("{utensils}", selected_utensil)

                operating_condtions.append(condition)
            generated_scene["operating-conditions"] = operating_condtions

            post_condtions = []
            for condition in generated_scene["post-conditions"]:
                condition = condition.replace("{object}", object)
                condition = condition.replace("{target}", selected_target)
                condition = condition.replace("{utensils}", selected_utensil)

                post_condtions.append(condition)
            generated_scene["post-conditions"] = post_condtions

            str_scene = str(generated_scene)

            # if str_scene not in track_scene:
            #     cnt += 1
            #     track_scene[str_scene] = True

            all_scenes.append(generated_scene)

    json.dump(all_scenes, f, indent=4)


if __name__ == "__main__":
    motions = ["pick-and-place", "pour", "scoop-and-pour", "sprinkle", "mix"]

    for motion in motions:
        generate_different_scenes(motion)
