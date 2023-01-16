import cv2
import os
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
                (abs((wrist_mean_point[0] - shoulder_mean_point[0]) / body_length) < 0.25)
                or is_front_orientation
            )
        )
        is_pushups.append(bool(is_pushup))
    return is_pushups

def plot_all_cluster(all_clusters, num_labels):
    for idx in range(len(all_clusters)):
        frame = plot_kps_as_image(all_clusters[idx], int(100 * num_labels[idx]/sum(num_labels)))
        cv2.imwrite(str(idx) + '.png', frame)

    #TODO: Plot images so that size of the image is proportional to the count of that cluster
    plot_cluster_as_image(len(all_clusters))

def plot_cluster_as_image(num_clusters):
    for idx in range(0, int(num_clusters/5)):
        for jdx in range(0, 5):
            if jdx == 0:
                frame = cv2.imread(str(idx*5 + jdx) + ".png")
            else:
                this_frame = cv2.imread(str(idx*5 + jdx) + ".png")
                frame = cv2.hconcat([frame, this_frame])
            os.remove(str(idx*5 + jdx) + ".png")
        if idx == 0:
            full_frame = frame
        else:
            full_frame = cv2.vconcat([full_frame, frame])
    file_name = "num_clusters_" + str(num_clusters)
    cv2.imwrite(file_name + '.png', full_frame)

def plot_kps_as_image(kps, prob):
    frame = np.zeros((256, 256, 3))
    max_val = max(kps)
    kps = kps * 200/max_val
    kps = np.array(kps).reshape((17,2))

    h,w = frame.shape[0], frame.shape[1]
    color = [256,256,256] 

    for iter_keypoints in range(17):
        x_raw_cord = int(np.ceil(kps[iter_keypoints][1]))
        y_raw_cord = int(np.ceil(kps[iter_keypoints][0]))
        radius = 3
        frame[min(max(0,x_raw_cord-radius),h):max(0,min(x_raw_cord+radius,h)),min(max(0,y_raw_cord-radius),w):max(0,min(y_raw_cord+radius,w))] = color

    frame = cv2.UMat(frame)

    skeleton_connections = [[[16,14],[14,12]], [[17,15],[15,13]], [[12,13],[6,12],[7,13],[6,7]], [[6,8],[8,10]], [[7,9],[9,11]], [[2,3],[1,2],[1,3],[2,4],[3,5]]]
    keypoints = kps   
    thickness = 1

    for skeleton_connection in skeleton_connections:
        for iter_line in range(len(skeleton_connection)):
            start_point = (int(np.ceil(keypoints[skeleton_connection[iter_line][0]-1][0])),int(np.ceil(keypoints[skeleton_connection[iter_line][0]-1][1])))
            end_point = (int(np.ceil(keypoints[skeleton_connection[iter_line][1]-1][0])),int(np.ceil(keypoints[skeleton_connection[iter_line][1]-1][1])))
            frame = cv2.line(frame, start_point, end_point, color, thickness)

    cv2.putText(frame,"Prob: " + str(prob), (5,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, 2)
    return frame