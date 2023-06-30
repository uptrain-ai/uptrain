import json
import numpy as np
import cv2
import os
import pandas as pd
import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables import Keypoint
from sklearn.preprocessing import Normalizer


class KpsDataset:
    def __init__(
        self,
        file_name,
        n_classes=2,
        batch_size=16,
        shuffle=False,
        augmentations=False,
        is_test=False,
        normalization=False,
    ):
        data = read_json(file_name)
        self.data = np.array(data)
        self.n_classes = n_classes
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.augmentations = augmentations
        self.is_test = is_test
        self.normalization = normalization
        np.random.seed(10)
        ia.seed(10)
        self.on_epoch_end()

    def load_x_y_from_data(self, data=None):
        if data is None:
            data = self.data
        kps = [x["kps"] for x in data]
        gts = [x["gt"] for x in data]
        ids = [x["id"] for x in data]
        if self.normalization:
            norm = Normalizer()
            kps = norm.fit_transform(kps)
        return (kps, gts, ids)

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.data))
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __len__(self):
        return int(np.floor(len(self.indexes) / self.batch_size))

    def __getitem__(self, index):
        indexes = self.indexes[index * self.batch_size : (index + 1) * self.batch_size]
        this_data = [self.data[i] for i in indexes]
        batch_kps, batch_gts, batch_ids = self.load_x_y_from_data(this_data)

        for idx in range(len(batch_kps)):
            raw_kps = np.reshape(np.array(batch_kps[idx]), (17, 2))
            kps = []
            for ijdx in range(17):
                kps.append(Keypoint(x=raw_kps[ijdx][0], y=raw_kps[ijdx][1]))
            image = np.zeros((2, 2, 3))

            if self.augmentations:
                seq = iaa.Sequential(
                    [
                        iaa.Affine(
                            rotate=(-10, 10),
                            scale=(0.75, 1.25),
                            translate_percent=(-0.25, 0.25),
                            shear=(-20, 20),
                        )
                    ]
                )
                image_aug, kps_aug = seq(image=image, keypoints=kps)
                new_kps = []
                for ijdx in range(len(kps_aug)):
                    new_kps.extend([kps_aug[ijdx].x, kps_aug[ijdx].y])
            else:
                new_kps = np.reshape(raw_kps, 34)
            batch_kps[idx] = np.array(new_kps)

        if self.is_test:
            sample = (
                {"kps": np.array(batch_kps), "id": np.array(batch_ids)},
                np.array(batch_gts),
            )
        else:
            sample = (np.array(batch_kps), np.array(batch_gts))

        return sample

    def __iter__(self):
        """Create a generator that iterate over the Sequence."""
        for item in (self[i] for i in range(len(self))):
            yield item


def read_json(file_name, dataframe=False):
    with open(file_name) as f:
        data = json.load(f)
    if dataframe:
        data = pd.DataFrame(data)
        data = data.drop(["frame_idx"], axis=1)
        keys = [
            "Nose_X",
            "Nose_Y",
            "Left_Eye_X",
            "Left_Eye_Y",
            "Right_Eye_X",
            "Right_Eye_Y",
            "Left_Ear_X",
            "Left_Ear_Y",
            "Right_Ear_X",
            "Right_Ear_Y",
            "Left_Shoulder_X",
            "Left_Shoulder_Y",
            "Right_Shoulder_X",
            "Right_Shoulder_Y",
            "Left_Elbow_X",
            "Left_Elbow_Y",
            "Right_Elbow_X",
            "Right_Elbow_Y",
            "Left_Wrist_X",
            "Left_Wrist_Y",
            "Right_Wrist_X",
            "Right_Wrist_Y",
            "Left_Hip_X",
            "Left_Hip_Y",
            "Right_Hip_X",
            "Right_Hip_Y",
            "Left_Knee_X",
            "Left_Knee_Y",
            "Right_Knee_X",
            "Right_Knee_Y",
            "Left_Ankle_X",
            "Left_Ankle_Y",
            "Right_Ankle_X",
            "Right_Ankle_Y",
        ]
        for idx in range(len(keys)):
            values = [x[idx] for x in list(data["kps"])]
            data[keys[idx]] = values
        data = data.drop(["kps"], axis=1)
    return data


def write_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)


def plot_all_cluster(all_clusters, num_labels):
    for idx in range(len(all_clusters)):
        frame = plot_kps_as_image(
            all_clusters[idx], int(100 * num_labels[idx] / sum(num_labels))
        )
        cv2.imwrite(str(idx) + ".png", frame)

    # TODO: Plot images so that size of the image is proportional to the count of that cluster
    plot_cluster_as_image(len(all_clusters))


def plot_cluster_as_image(num_clusters):
    for idx in range(0, int(num_clusters / 5)):
        for jdx in range(0, 5):
            if jdx == 0:
                frame = cv2.imread(str(idx * 5 + jdx) + ".png")
            else:
                this_frame = cv2.imread(str(idx * 5 + jdx) + ".png")
                frame = cv2.hconcat([frame, this_frame])
            os.remove(str(idx * 5 + jdx) + ".png")
        if idx == 0:
            full_frame = frame
        else:
            full_frame = cv2.vconcat([full_frame, frame])
    file_name = "num_clusters_" + str(num_clusters)
    cv2.imwrite(file_name + ".png", full_frame)


def plot_kps_as_image(kps, prob):
    frame = np.zeros((256, 256, 3))
    max_val = max(kps)
    kps = kps * 200 / max_val
    kps = np.array(kps).reshape((17, 2))

    h, w = frame.shape[0], frame.shape[1]
    color = [256, 256, 256]

    for iter_keypoints in range(17):
        x_raw_cord = int(np.ceil(kps[iter_keypoints][1]))
        y_raw_cord = int(np.ceil(kps[iter_keypoints][0]))
        radius = 3
        frame[
            min(max(0, x_raw_cord - radius), h) : max(0, min(x_raw_cord + radius, h)),
            min(max(0, y_raw_cord - radius), w) : max(0, min(y_raw_cord + radius, w)),
        ] = color

    frame = cv2.UMat(frame)

    skeleton_connections = [
        [[16, 14], [14, 12]],
        [[17, 15], [15, 13]],
        [[12, 13], [6, 12], [7, 13], [6, 7]],
        [[6, 8], [8, 10]],
        [[7, 9], [9, 11]],
        [[2, 3], [1, 2], [1, 3], [2, 4], [3, 5]],
    ]
    keypoints = kps
    thickness = 1

    for skeleton_connection in skeleton_connections:
        for iter_line in range(len(skeleton_connection)):
            start_point = (
                int(np.ceil(keypoints[skeleton_connection[iter_line][0] - 1][0])),
                int(np.ceil(keypoints[skeleton_connection[iter_line][0] - 1][1])),
            )
            end_point = (
                int(np.ceil(keypoints[skeleton_connection[iter_line][1] - 1][0])),
                int(np.ceil(keypoints[skeleton_connection[iter_line][1] - 1][1])),
            )
            frame = cv2.line(frame, start_point, end_point, color, thickness)

    cv2.putText(
        frame,
        "Prob: " + str(prob),
        (5, 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        2,
    )
    return frame


def plot_all_cluster(all_clusters, num_labels, plot_save_name=""):
    for idx in range(len(all_clusters)):
        frame = plot_kps_as_image(all_clusters[idx], int(num_labels[idx]))
        cv2.imwrite(str(idx) + ".png", frame)

    # TODO: Plot images so that size of the image is proportional to the count of that cluster
    plot_cluster_as_image(len(all_clusters), plot_save_name=plot_save_name)


def plot_cluster_as_image(num_clusters, plot_save_name=""):
    for idx in range(0, int(np.ceil(num_clusters / 5))):
        for jdx in range(0, 5):
            if idx * 5 + jdx >= num_clusters:
                frame = cv2.hconcat([frame, this_frame * 0])
                continue
            if jdx == 0:
                frame = cv2.imread(str(idx * 5 + jdx) + ".png")
            else:
                this_frame = cv2.imread(str(idx * 5 + jdx) + ".png")
                frame = cv2.hconcat([frame, this_frame])
            os.remove(str(idx * 5 + jdx) + ".png")
        if idx == 0:
            full_frame = frame
        else:
            full_frame = cv2.vconcat([full_frame, frame])
    if plot_save_name == "":
        plot_save_name = "num_clusters_" + str(num_clusters) + ".png"
    cv2.imwrite(plot_save_name, full_frame)


def plot_kps_as_image(kps, prob):
    frame = np.zeros((256, 256, 3))
    max_val = max(kps)
    kps = kps * 200 / max_val
    kps = np.array(kps).reshape((17, 2))

    h, w = frame.shape[0], frame.shape[1]
    color = [256, 256, 256]

    for iter_keypoints in range(17):
        x_raw_cord = int(np.ceil(kps[iter_keypoints][1]))
        y_raw_cord = int(np.ceil(kps[iter_keypoints][0]))
        radius = 3
        frame[
            min(max(0, x_raw_cord - radius), h) : max(0, min(x_raw_cord + radius, h)),
            min(max(0, y_raw_cord - radius), w) : max(0, min(y_raw_cord + radius, w)),
        ] = color

    frame = cv2.UMat(frame)

    skeleton_connections = [
        [[16, 14], [14, 12]],
        [[17, 15], [15, 13]],
        [[12, 13], [6, 12], [7, 13], [6, 7]],
        [[6, 8], [8, 10]],
        [[7, 9], [9, 11]],
        [[2, 3], [1, 2], [1, 3], [2, 4], [3, 5]],
    ]
    keypoints = kps
    thickness = 1

    for skeleton_connection in skeleton_connections:
        for iter_line in range(len(skeleton_connection)):
            start_point = (
                int(np.ceil(keypoints[skeleton_connection[iter_line][0] - 1][0])),
                int(np.ceil(keypoints[skeleton_connection[iter_line][0] - 1][1])),
            )
            end_point = (
                int(np.ceil(keypoints[skeleton_connection[iter_line][1] - 1][0])),
                int(np.ceil(keypoints[skeleton_connection[iter_line][1] - 1][1])),
            )
            frame = cv2.line(frame, start_point, end_point, color, thickness)

    cv2.putText(
        frame,
        "Support: " + str(prob),
        (5, 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
        2,
    )
    return frame
