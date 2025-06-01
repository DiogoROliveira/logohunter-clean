import cv2
import numpy as np
import os
from PIL import Image
from timeit import default_timer as timer

import utils
from utils import contents_of_bbox, features_from_image
from similarity import load_brands_compute_cutoffs, similar_matches, similarity_cutoff, draw_matches


def detect_logo(yolo, img_path, save_img, save_img_path='./', postfix=''):
    """
    Call YOLO logo detector on input image, optionally save resulting image.

    Args:
      yolo: keras-yolo3 initialized YOLO instance
      img_path: path to image file
      save_img: bool to save annotated image
      save_img_path: path to directory where to save image
      postfix: string to add to filenames
    Returns:
      prediction: list of bounding boxes in format (xmin,ymin,xmax,ymax,class_id,confidence)
      image: unaltered input image as (H,W,C) array
    """
    try:
        image = Image.open(img_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image_array = np.array(image)
    except:
        print('File Open Error! Try again!')
        return None, None

    prediction, new_image = yolo.detect_image(image)

    img_out = postfix.join(os.path.splitext(os.path.basename(img_path)))
    if save_img:
        new_image.save(os.path.join(save_img_path, img_out))

    return prediction, image_array

def match_logo(img, prediction, model_preproc, text, sim_threshold, bins=100, cdf_thresh=0.99):
    """
    Given an image and a prediction, try to find logo by:
    1) extracting portion of image corresponding to prediction
    2) looking for the best match in inputs by:
       a) computing feature vectors for all logos in inputs
       b) computing feature vector for predicted logo
       c) finding closest input logo to predicted logo by cosine similarity
    3) if match is good enough, label prediction as input logo
    """
    model, my_preprocess = model_preproc
    feat_input, sim_cutoff, (cdf_list, bins_list) = sim_threshold
    
    # If no predictions or empty predictions, return empty results
    if prediction is None or len(prediction) == 0:
        return [], {}, []
    
    matches = {}
    match_index = 0
    confidence_scores = []
    
    for pred in prediction:
        try:
            # Verificar se a predição tem 4 ou 5 valores
            if len(pred) == 4:
                xmin, ymin, xmax, ymax = pred
                score = 1.0  # Default score se não fornecido
            else:
                xmin, ymin, xmax, ymax, score = pred
                
            confidence_scores.append(score)
            
            # extract region of image corresponding to prediction
            # and preprocess it so it can be fed to net
            logo_img = img[int(ymin):int(ymax), int(xmin):int(xmax)]
            if logo_img.size == 0:
                continue
                
            logo_feat = features_from_image(logo_img, model, my_preprocess)
            
            # find best match of crop among input logos
            matches[match_index] = find_match(logo_feat, feat_input, sim_cutoff)
            match_index += 1
            
        except Exception as e:
            print(f"Error processing prediction: {e}")
            continue
    
    return prediction, matches, confidence_scores


def detect_video(yolo, video_path, output_path=""):
    import cv2
    vid = cv2.VideoCapture(video_path)
    if not vid.isOpened():
        raise IOError("Couldn't open video")
    video_FourCC    = cv2.VideoWriter_fourcc(*'mp4v') #int(vid.get(cv2.CAP_PROP_FOURCC))
    video_fps       = vid.get(cv2.CAP_PROP_FPS)
    video_size      = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    isOutput = True if output_path != "" else False
    if isOutput:
        print(output_path, video_FourCC, video_fps, video_size)
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = timer()
    while vid.isOpened():
        return_value, frame = vid.read()
        if not return_value:
            break
        # opencv images are BGR, translate to RGB
        frame = frame[:,:,::-1]
        image = Image.fromarray(frame)
        out_pred, image = yolo.detect_image(image)
        result = np.asarray(image)
        if isOutput:
            out.write(result[:,:,::-1])
    vid.release()
    out.release()
    yolo.close_session()
