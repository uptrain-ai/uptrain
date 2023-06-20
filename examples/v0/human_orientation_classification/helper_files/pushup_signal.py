import numpy as np


def body_length_from_kps(kps):
    head_mean_point = np.sum(kps[0:5, 0:2], axis=0) / 5
    legs_mean_point = np.sum(kps[11:17, 0:2], axis=0) / 6
    body_length_horizontal = max(0.01, abs(head_mean_point[0] - legs_mean_point[0]))
    body_length_vertical = max(0.01, abs(head_mean_point[1] - legs_mean_point[1]))
    return max(body_length_horizontal, body_length_vertical)


def body_length_signal(inputs, outputs, gts=None, extra_args={}):
    body_lengths = []
    for input in inputs["kps"]:
        kps = np.reshape(np.array(input), (17, 2))
        body_length = body_length_from_kps(kps)
        body_lengths.append(body_length)
    return body_lengths


def pushup_signal(inputs, outputs, gts=None, extra_args={}):
    # Define signal to identify cases when the user is in the pushup position
    is_pushups = []
    for input in inputs["kps"]:
        kps = np.reshape(np.array(input), (17, 2))
        head_mean_point = np.sum(kps[0:5, 0:2], axis=0) / 5
        legs_mean_point = np.sum(kps[11:17, 0:2], axis=0) / 6
        body_slope = abs(
            (legs_mean_point[1] - head_mean_point[1])
            / max(0.1, abs(legs_mean_point[0] - head_mean_point[0]))
        )
        hands_mean_point = np.sum(kps[7:11, 0:2], axis=0) / 4
        shoulder_mean_point = np.sum(kps[5:7, 0:2], axis=0) / 2
        wrist_mean_point = np.sum(kps[9:11, 0:2], axis=0) / 2
        body_length = body_length_from_kps(kps)
        is_front_orientation = (kps[9, 0] - kps[10, 0]) > body_length
        is_pushup = (
            (body_slope < 1)
            and (hands_mean_point[1] > shoulder_mean_point[1])
            and (
                (
                    abs((wrist_mean_point[0] - shoulder_mean_point[0]) / body_length)
                    < 0.25
                )
                or is_front_orientation
            )
        )
        is_pushups.append(bool(is_pushup))
    return is_pushups
