
from django.http import HttpResponse 
from django.shortcuts import render, redirect 
from .forms import *
from PIL import Image
from PIL.ExifTags import TAGS
from pymongo import MongoClient
import os
client = MongoClient()
client = MongoClient('localhost', 27017)
db = client['TDB']

# Create your views here. 
def image_view(request): 
  
    if request.method == 'POST': 

        form = ImageForm(request.POST, request.FILES) 
    
        if form.is_valid(): 
            form.save() 
            print(form.cleaned_data)
            image_table = db.image_image
            filename = str(form.cleaned_data['image'])
            image_id = image_table.find_one({'image':'images'+'/'+filename})['id']
            path= 'media/images/'+filename
            size = os.path.getsize(path)/(1024*1024)
            image = Image.open(path)
            exifdata = image.getexif()
            metadata = {"name":filename,'id':image_id,'size':int(size)}
            for tag_id in exifdata:
           # get the tag name, instead of human unreadable tag id
                tag = TAGS.get(tag_id, tag_id)
                data = exifdata.get(tag_id)
                # decode bytes 
                if isinstance(data, bytes):
                    data = data.decode()
                print(f"{tag}: {data}")
                
                try:
                    metadata.update({tag:float(str(data))})
                except:
                    metadata.update({tag:str(data)})
        
            metacollection = db.metacollection
            result  = metacollection.insert_one(metadata)
            print('One post: {0}'.format(result.inserted_id))
            data = {'success':True,'message': 'Upload and metadata extraction succesful','form':ImageForm()}
            return render(request,'upload.html',data)  
    else: 
        form = ImageForm() 
    data = {'form' : form,'success':False}
    return render(request, 'upload.html',data) 
  
def return_valid(dic):
    new_dic= {}
    for key in dic.keys():
        if(dic[key]!="" and key != 'csrfmiddlewaretoken'):
            new_dic.update({key:dic[key]})
    return new_dic

def search_view(request):
    if request.method == 'POST':
        try:
            test = request.POST['listall']
            print("OKAY")
            metacollection = db.metacollection
            result = list(metacollection.find({}))
            if(len(result)==0):
                success = False
            else:
                success = True
        except:    
            print("NOT OKAY")
            criteria = return_valid(request.POST)

            myquery = {"Make":criteria['Make'],"FocalLength":{ "$gt": float(criteria['minFocal']),"$lt": float(criteria['maxFocal'])},"ISOSpeedRatings":{ "$gt": float(criteria['minISO']),"$lt": float(criteria['maxISO'])}
                ,"ExposureTime":{ "$gt": float(criteria['minExp']),"$lt": float(criteria['maxExp'])}}
            metacollection = db.metacollection
            result = list(metacollection.find(myquery))
            if(len(result)==0):
                success= False
            else:
                success = True

        data = {'success':success,'listofimages':result}
        print(data['listofimages'])
    else:
        data = {'success':False}
    return render(request, 'search.html',data) 
#def success(request): 
#    return HttpResponse('successfully uploaded') 
