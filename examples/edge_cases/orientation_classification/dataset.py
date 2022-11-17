import json
import tensorflow as tf
import numpy as np
import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables import Keypoint
import numpy as np
from sklearn.preprocessing import Normalizer


class KpsDataset(tf.keras.utils.Sequence):
    def __init__(
        self,
        file_name,
        n_classes=2,
        batch_size=256,
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
        kps = [np.array(x["kps"]) for x in data]
        gts = [np.array(x["gt"]) for x in data]
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
                {"kps": np.array(batch_kps), "id": batch_ids},
                np.array(batch_gts),
            )
        else:
            sample = (np.array(batch_kps), np.array(batch_gts))

        return sample


def read_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data


def write_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f)


def input_to_dataset_transformation(inputs):
    dictn = json.loads(inputs["input"])
    return {"kps": list(dictn["kps"][0]), "id": int(dictn["id"][0])}
