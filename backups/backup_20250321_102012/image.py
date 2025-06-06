import torch
from torch.utils.model_zoo import load_url
from PIL import Image
from scipy.special import expit
import sys
import streamlit as st
sys.path.append('..')

from blazeface import FaceExtractor, BlazeFace
from architectures import fornet,weights
from isplutils import utils

def image_pred(threshold=0.5, model='EfficientNetAutoAttB4', dataset='DFDC', image_path=None):
    """
    Choose an architecture between
    - EfficientNetB4
    - EfficientNetB4ST
    - EfficientNetAutoAttB4
    - EfficientNetAutoAttB4ST
    - Xception
    """
    if image_path is None:
        raise ValueError("image_path must be provided")

    net_model = model

    """
    Choose a training dataset between
    - DFDC
    - FFPP
    """
    train_db = dataset

    device = torch.device('cuda:0') if torch.cuda.is_available() else torch.device('cpu')
    face_policy = 'scale'
    face_size = 224

    model_url = weights.weight_url['{:s}_{:s}'.format(net_model,train_db)]
    net = getattr(fornet,net_model)().eval().to(device)
    net.load_state_dict(load_url(model_url,map_location=device,check_hash=True))

    transf = utils.get_transformer(face_policy, face_size, net.get_normalizer(), train=False)
    
    facedet = BlazeFace().to(device)
    facedet.load_weights("blazeface/blazeface.pth")
    
    facedet.load_anchors("blazeface/anchors.npy")
    face_extractor = FaceExtractor(facedet=facedet)
    print(image_path,"image_path")
    im_real = Image.open(image_path)
    im_real_faces = face_extractor.process_image(img=im_real)
    im_real_face = im_real_faces['faces'][0] # take the face with the highest confidence score found by BlazeFace
    
    faces_t = torch.stack( [ transf(image=im)['image'] for im in [im_real_face] ] )

    with torch.no_grad():
        # Get raw logits from the model
        faces_pred = net(faces_t.to(device)).cpu().numpy().flatten()
        # Apply sigmoid to get probability
        prob = expit(faces_pred.mean())
             
    if prob > threshold:
        return "fake", prob
    else:
        return "real", prob
