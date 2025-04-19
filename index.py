from flask import Flask, render_template, request,flash
from werkzeug.utils import secure_filename
import os
from flask import Response
from flask import session
from DBConfig import DBConnection
import  sys,io
from PIL import Image
import base64
import cv2
from AgeGender import detection

app = Flask(__name__)
app.secret_key = "abc"

camera = cv2.VideoCapture(0)
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/newuser")
def newuser():
    return render_template("register.html")

@app.route("/face_bmi")
def face_bmi():
    return render_template("face_bmi.html")

@app.route("/user_register",methods =["GET", "POST"])
def user_register():
    try:
        
        sts=""
        name = request.form.get('name')
        uid = request.form.get('unm')
        pwd = request.form.get('pwd')
        mno = request.form.get('mno')
        email = request.form.get('email')
        database = DBConnection.getConnection()
        cursor = database.cursor()
        sql = "select count(*) from register where userid='" + uid + "'"
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        if res > 0:
            sts = 0
        else:
            sql = "insert into register values(%s,%s,%s,%s,%s)"
            values = (name,uid, pwd,email,mno)
            cursor.execute(sql, values)
            database.commit()
            sts = 1

        if sts==1:
            return render_template("user.html", msg="Registered Successfully..! Login Here.")


        else:
            return render_template("register.html", msg="User Id already exists..!")



    except Exception as e:
        print(e)

    return ""


@app.route("/userlogin_check",methods =["GET", "POST"])
def userlogin_check():

        uid = request.form.get("unm")
        pwd = request.form.get("pwd")

        database = DBConnection.getConnection()
        cursor = database.cursor()
        sql = "select count(*) from register where userid='" + uid + "' and passwrd='" + pwd + "'"
        cursor.execute(sql)
        res = cursor.fetchone()[0]
        if res > 0:
            session['uid'] = uid

            return render_template("user_home.html")
        else:

            return render_template("user.html", msg2="Invalid Credentials")



        return ""



@app.route("/face2bmi_detection",methods =["GET", "POST"])
def face2bmi_detection():
    try:
        image = request.files['file']
        imgdata = secure_filename(image.filename)
        filename=image.filename

        filelist = [ f for f in os.listdir("testimg") ]
        for f in filelist:
            os.remove(os.path.join("testimg", f))


        image.save(os.path.join("testimg", imgdata))
        print(filename)
        image_path="../Detection/testimg/"+filename

        pred_res=detection(image_path)

        test_img = os.path.join("testimg", filename)
        im = Image.open(test_img)
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())

       
        age=pred_res[1]
        gender=pred_res[2]


        face2bmi_list=[]
        face2bmi_list.clear()
    
        face2bmi_list.append(round(age))
        face2bmi_list.append(gender)
        print(face2bmi_list)

        return render_template("detection_result.html", result=face2bmi_list,img_data=encoded_img_data.decode('utf-8'))



    except Exception as e:
        print(e.args[0])
        tb = sys.exc_info()[2]
        print(tb.tb_lineno)
        print(e)

    return ""


@app.route("/captured_img",methods =["GET", "POST"])
def captured_img():
    image_path = "E:\\MINOR-PROJECT\\Detection\\testimg//testingimg.jpeg"
    im = Image.open("E:\\MINOR-PROJECT\\Detection\\testimg//testingimg.jpeg")
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())


    return render_template("captured_image.html",img_data=encoded_img_data.decode('utf-8'))



@app.route("/face2bmi_detection2",methods =["GET", "POST"])
def face2bmi_detection2():
    try:

        image_path="E:\\MINOR-PROJECT\\Detection\\testimg/testingimg.jpeg"

        pred_res=detection(image_path)

        test_img = os.path.join("E:\\MINOR-PROJECT\\Detection\\testimg", "testingimg.jpeg")
        im = Image.open("E:\\MINOR-PROJECT\\Detection\\testimg//testingimg.jpeg")
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())

        
        age=pred_res[1]
        gender=pred_res[2]

       

        face2bmi_list=[]
        face2bmi_list.clear()
        face2bmi_list.append(round(age))
        face2bmi_list.append(gender)
       
        print(face2bmi_list)

        return render_template("detection_result.html", result=face2bmi_list,img_data=encoded_img_data.decode('utf-8'))



    except Exception as e:
        print(e.args[0])
        tb = sys.exc_info()[2]
        print(tb.tb_lineno)
        print(e)

    return ""


@app.route('/face_bmi_webcam')
def face_bmi_webcam():
    return render_template('camera.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        cv2.imwrite('E:\\MINOR-PROJECT\\Detection\\testimg//testingimg.jpeg', frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result




if __name__ == '__main__':
    app.run(host="localhost", port=2222, debug=True)
