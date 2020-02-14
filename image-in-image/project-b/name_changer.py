import sys
import os
import os.path
import glob
import firebase_admin
from firebase_admin import credentials,firestore
# from firebase_admin import firestore
from pathlib import Path
from PIL import Image

cred = credentials.Certificate('config3.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

i = 1
u = i
# photos = 0 + i
photos = 4

for file in glob.glob("data/test_oficiall/*.JPG"):
    photos += 1

print(photos)

while u < photos:
    if i > 1000:
        num = str(i)
    elif i > 100:
        num = '0'+str(i)
    elif i > 10:
        num = '00'+str(i)
    elif i >= 0:
        num = '000'+str(i)
   
    # if os.path.isfile(r'DJI_'+num+'.JPG') != 1:
    #     i += 1
    #     continue

    ref = db.collection(u'SPM_Iwaniuk').document(u'T'+str(i))
    keyword = 'height'

    doc = str(ref.get().to_dict()['height'])
    print('doc:',doc)

    height = doc.find(keyword)
    x = doc.find("'",height+len(keyword)+1)
    y = doc.find("'",x+1)
    x = x + 1


    # print('DJI_'+num+'.JPG')
    # print(os.listdir('.'))
    print(Path('data/test_oficiall/DJI_'+num+'.JPG').is_file())
    img=Image.open('data/test_oficiall/DJI_'+num+'.JPG')
    img.save('data/test_oficiall/format/'+str(i)+'-'+doc+'.JPG')
    # os.rename('data/test_oficiall/DJI_'+num+'.JPG','data/test_oficiall/'+str(i)+'-'+str(doc[x:y])+'.JPG')
    u+=1
    i+=1


print('end')