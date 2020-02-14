##okej, prolem byl w data_transform. Dalem te same a nie osobno dla small
##todo: coord na bazę danych a mpka 3d pobiera to właśnie z niej :)

print(f'start')
import os
import json
import numpy as np
import cv2

import torch
from torchvision import models, transforms
from PIL import Image
from os import mkdir, path,listdir
from shutil import rmtree
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials,firestore
cred = credentials.Certificate('config3.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

arr_coords=[]

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
folder_path='data/test_oficiall/format'

if path.isdir('test'):
    rmtree('test')
if path.isdir('results'):
    rmtree('results')
mkdir('test')
mkdir('results')

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])

data_transforms_big = transforms.Compose([
    # jakim kurwa cudem?
    transforms.ToTensor(),
    normalize
])
# w,_= small_image.size
# data_transforms_small = transforms.Compose([
#     transforms.CenterCrop(w),
#     transforms.ToTensor(),
#     normalize
# ])



def find_img_in_img(i, height_small, height_big):
    print('get:',i, height_small, height_big)
    small_image=Image.open(f'{folder_path}/{i+1}-{height_small}.JPG').convert('RGB')
    height_big=int(height_big)
    height_small=int(height_small)

    # small_image= Image.open('{}/{}-{}.JPG'.format(folder_path,i+1,height_small)).convert('RGB')
    
    small_image=small_image.resize((1920,1080))
    small_image=small_image.crop((420,0,1500,1080))
    small_image=small_image.resize((int(1080 *  height_small/ height_big),int(1080*  height_small/ height_big)))
    
    small_image.save(f'test/{i}-small.png')
    small_image.save('results/a.png')

    big_image=Image.open(f'{folder_path}/{i}-{height_big}.JPG').convert('RGB')
    # big_image=Image.open('{}/{}-{}.JPG'.format(folder_path,i,height_big)).convert('RGB')
    big_image=big_image.resize((1920,1080))
    big_image=big_image.crop((420,0,1500,1080))

    big_image.save(f'results/b.png')
    print('small size: ',small_image.size)
    print('big size: ',big_image.size)

    big_image_cv2_plis=cv2.imread(f'{folder_path}/{i}-{height_big}.JPG')
    # big_image_cv2_plis=cv2.imread('{}/{}-{}.JPG'.format(folder_path,i,height_big))
    big_image_cv2_plis=cv2.resize(big_image_cv2_plis,(1920,1080))
    big_image_cv2_plis = big_image_cv2_plis[0:1080,420:1500]
    
    
    #tranforms-compose
    w,_= small_image.size
    data_transforms_small = transforms.Compose([
    transforms.CenterCrop(w),
    transforms.ToTensor(),
    normalize
])

    #tranforms-assign
    big_image_transform=data_transforms_big(big_image)
    plt.imsave(f'test/{i}-big.png',big_image_transform.numpy()[2])

    big_image_transform=big_image_transform.numpy().transpose(1, 2, 0)
    big_image_transform=big_image_transform.astype(np.float32)
    plt.imsave('test/big2.png',big_image_transform[0])
    
    small_images_torch=[]    
    # print('small size: ',small_image.size)
    # print('big size: ',big_image.size)
    #rotating photos
    for rotate_angle in range(0,360,10):
        rotation_45_procent = (rotate_angle%45)/45
        scale=(rotation_45_procent * 0.51)+1
        w,h=small_image.size
        w_scale=int(w*scale)
        h_scale=int(h*scale)
        # print(rotate_angle,scale,w_scale,h_scale)


        small_image_transform=small_image.resize((w_scale,h_scale)).rotate(rotate_angle)
        # small_image_transform.save(f'test/{i}zzz{rotate_angle}.png')

        small_image_torch = data_transforms_small(small_image_transform)

        if rotate_angle%20==0:
            plt.imsave('test/test-{}.png'.format(rotate_angle), small_image_torch.numpy()[0])


        small_images_torch.append(small_image_torch.unsqueeze(0))
        
     #creating rectangle
    max_m=-100
    max_loc=None

    for torch_image in small_images_torch:
        template_image=torch_image[0].numpy().transpose(1, 2, 0)
        template_image=template_image.astype(np.float32)

        # w, h = template_image.shape[:-1]

        result = cv2.matchTemplate(big_image_transform, template_image, cv2.TM_CCOEFF_NORMED)

        if np.amax(result)>max_m:
            max_m=np.amax(result)
            print(max_m,max_loc)
        loc = np.where(result >= max_m)

        for pt in zip(*loc[::-1]): 
            max_loc=pt
            print(max_m,max_loc)


    print('coords: ',max_m,max_loc)
    arr_coords.append([max_loc[0],max_loc[1],1080, height_big])
    print([max_loc[0],max_loc[1],1080, height_big])

    w, h = small_image.size
    cv2.rectangle(big_image_cv2_plis, max_loc, (max_loc[0]+ h, max_loc[1]+ w),(0, 0, 255), 5)
    
    #save
    cv2.imwrite('results/{}.png'.format(i), big_image_cv2_plis)
    cv2.imwrite('www/{}.JPG'.format(i),big_image_cv2_plis)

    plt.imshow(big_image_cv2_plis[:,:,::-1])
    print('fc-end')
    return 'okej'


# i=0
arr=sorted(os.listdir(folder_path))
for i in range(len(arr)):
    big_height=arr[i].replace(F"{i+1}-",'').replace('.JPG','')
    try:
        small_height=arr[i+1]
        # print(i)
        small_height=small_height.replace(f'{i+2}-','').replace('.JPG','')
    
        # print(small_height,big_height)
        # print(findImgInImg(i+1,small_height,big_height))
        find_img_in_img(i+1,small_height,big_height)
    except:
        last_name = arr[len(arr)-1]
        last_image=Image.open(f'{folder_path}/{last_name}')
        last_image=last_image.resize((1920,1080))
        last_image=last_image.crop((420,0,1500,1080))
        last_image.save(f'results/{i+1}.png')

        last_height=last_name.replace(f'{len(arr)}-','').replace('.JPG','')

        arr_coords.append(['last','last','1080',last_height])
        print('arr:',arr_coords)
        
        ref = db.collection(u'Map_3D')#.document('coords')
        
        for index,element in enumerate(arr_coords):
            ref.document(f'{index}').set({
                u'x':str(arr_coords[index][0]),
                u'y':str(arr_coords[index][1]),
                u'size':str(arr_coords[index][2]),
                u'height':str(arr_coords[index][3])
            })
            print('db',arr_coords[index][3])




        
print('end')
