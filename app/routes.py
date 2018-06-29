from app import app
from flask import render_template, request, redirect, url_for
import os.path
from werkzeug.utils import secure_filename
import json
from pprint import pprint
import requests
import io
import time



# destination for uploaded files
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
UPLOAD_FOLDER= os.path.join(APP_STATIC, 'uploads')
HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

URL_POST = "https://gretb1518083645.zendesk.com/api/v2/requests.json"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# allowed filetypes
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def writeFile(f):
    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

#  method to check file extensions, lower case
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# defauly route
@app.route('/')
def flask():
    return "Flask"
# test route
@app.route('/index')
def index():
    return "Welcome to Support@"

# display support form
@app.route('/support_request')
def support_request():
    return render_template('support_request.html')
# parse form data to data structures
@app.route('/get_support_request', methods=['POST','GET'] )
def get_support_request():
    att = []
    if request.method == 'POST':
        name=request.form['name']
        subject=request.form['subject']
        email=request.form['email']
        school_center=request.form['school_center']
        contact_number=request.form['contact_number']
        emp_id=request.form['emp_id']
        support_type=request.form['select_type']
        detail_message=request.form['detail_message']
        phos = request.files.getlist('photos')
        #print(phos)
        for i in phos:
            writeFile(i)

            a = {
                "id": time.time(),
                "name": i.filename,
                "content_url": UPLOAD_FOLDER,
                "content_type": i.content_type}
            att.append(a)
            #print(a)
            #print(i.filename)

      
        try:
            #file_upload=request.files['file']
            if len(phos) > 0:
                    # 
                #writeFile(phos.filename)
                print(phos)
                # create dict to pass too jinja in html
                attach=dict({'name': name,'subject': subject, 'email': email,'school_center': school_center,'contact_number': contact_number, 'emp_id': emp_id, 'support_type':support_type, 'detail_message': detail_message, 'attachments':phos} )
                print(attach)
                json_request ={
                                "request": {
                                    "requester": {
                                        "name": email
                                    },
                                    "subject": subject,
                                    "custom_fields": [{
                                            # get id of field from zendesk
                                            "id": "360000030009",
                                            "value": contact_number
                                        },
                                        {
                                            "id": "360000028405",
                                            "value": emp_id
                                        },
                                        {
                                            "id": "360000032529",
                                            "value": support_type
                                        },
                                        {
                                            "id": "360000027785",
                                            "value": school_center
                                        }
                                    ],
                                    "comment": {
                                        "body": detail_message,
                                       
                                       "thumbnails":att
                                       
                                    }
                                     
                                }
                            }
                print(json_request)
                #create json string from json object, formatting for easy reading
                parsed_json = json.dumps(json_request , indent=2)
                # print json string to console
                print(parsed_json)
                #data_attach = parsed_json
                r = requests.post(url = URL_POST, data=parsed_json, headers=HEADERS)
                ## TODO add if and redirect on status code here
                
                print(r.status_code)
                print(r)
            return render_template("results.html", data_to_results = attach)    
        except:
            # create dict to pass too jinja in html
            non_attach=dict({'name': name,'subject': subject, 'email': email,'school_center': school_center,'contact_number': contact_number, 'emp_id': emp_id, 'support_type':support_type, 'detail_message': detail_message} )
            json_request_no_attach = {
                                    "request": {
                                        "requester": {
                                            "name": email
                                        },
                                        "subject": subject,
                                        "custom_fields": [{
                                                "id": "360000030009",
                                                "value": contact_number
                                            },
                                            {
                                                "id": "360000028405",
                                                "value": emp_id
                                            },
                                            {
                                                "id": "360000032529",
                                                "value": support_type
                                            },
                                            {
                                                "id": "360000027785",
                                                "value": school_center
                                            }
                                        ],
                                        "comment": {
                                            "body": detail_message,
                                            "no attach": "no attach"
                                        }
                                    }
                                }
        
            #print(json_request_no_attach)
             #create json string from json object, formatting for easy reading
            parsed_json = json.dumps(json_request_no_attach , indent=2)
            # print json string to console
            #print(parsed_json)
            data = parsed_json
            r = requests.post(url = URL_POST, data=data, headers=HEADERS)
            ## TODO add if and redirect on status code here
            print(r.status_code)
            #print(non_attach)
            return render_template("results.html", data_to_results = non_attach)
        
            
       