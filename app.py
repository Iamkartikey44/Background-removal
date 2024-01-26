import streamlit as st
import cv2
import numpy as np
import base64
import requests
import os
from PIL  import Image
from streamlit_image_coordinates import streamlit_image_coordinates as im_coordinates
from streamlit_dimensions import st_dimensions

st.set_page_config(page_title="BackgroundRemoval",page_icon='🖼',layout='wide')


def set_background(image_file):

    with open(image_file,'rb') as f:
        img_data = f.read()
    img_encoded = base64.b64encode(img_data).decode()

    style = f"""
         <style>
         .stApp{{
               background-image:url(data:image/png;base64,{img_encoded});
               background-size:cover;
         }} 
         <style>
         """
    st.markdown(style,unsafe_allow_html=True)

set_background('./bg.jpg')


api_endpoint = "https://miet-ac.app.modelbit.com/v1/remove_background/latest"



col1,col2 = st.columns(2)

file = col2.file_uploader("",type=['jpeg','jpg','png'])

if file is not None:
    image = Image.open(file).convert('RGB')

    #screen_dim = st_dimensions(key='main')
    #screen_dim = screen_dim['width']
    image = image.resize((664,int(image.height*664/image.width)))


    col3,col4 = col2.columns(2)
    placeholder0 = col2.empty()
    with placeholder0:
        value = im_coordinates(image)
        if value is not None:
            print(value)

    if col3.button("Original",use_container_width=True):
        placeholder0.empty()
        placeholder1 = col2.empty()
        with placeholder1:
            col2.image(image,use_column_width=True)

    if col4.button("Remove background",type='primary',use_container_width=True):
        placeholder0.empty()
        placeholder2 = col2.empty()

        filename = f"{file.name}_{value['x']}_{value['y']}.png"

        if os.path.exists(filename):
            result_image = cv2.imread(filename,cv2.IMREAD_UNCHANGED)

        else:
            _,image_bytes = cv2.imencode('.png',np.asarray(image))
            image_bytes = image_bytes.tobytes()
            image_bytes_encoded = base64.b64encode(image_bytes).decode('utf-8')
            api_data = {'data':[image_bytes_encoded,value['x'],value['y']]}
            response = requests.post(api_endpoint,json=api_data)
            result_image =response.json()['data']
            result_image = base64.b64decode(result_image)
            result_image = cv2.imdecode(np.frombuffer(result_image,dtype=np.uint8),cv2.IMREAD_UNCHANGED)

            cv2.imwrite(filename,result_image)
        

        with placeholder2:
            col2.image(result_image,use_column_width=True)
