from flask import Flask, render_template, redirect, request, url_for, flash, session
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, TextField
from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart
import os
import sys
import numpy as np
import cv2
import imutils
import pytesseract
import dbconnect
import pandas as pd
import time

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app.secret_key = "asach"

@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        uname = request.form.get("username")
        password = request.form.get("password")
        result = dbconnect.check_login(uname, password)
        if result:
            session['user'] = uname
            return redirect(url_for("uploadimage"))
            #return render_template("tab.html",usname=uname)
        else:
             error = "Invalid credentials,Please try again"
             return render_template("logging.html", error=error)
    else:
        return render_template("logging.html")

@app.route("/info")
def moreinfo():
    return render_template("moreinfo.html")


@app.route("/uploadimage", methods=['GET', 'POST'])
def uploadimage():
    return render_template("upload.html")

@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target)

    for file in request.files.getlist("file"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        file.save(destination)

    def detect(fname):

        path = "C:\\Users\\Chinmay\\PycharmProjects\\upload\\images"
        temp = os.listdir(path)
        print(temp)

        final_path = path + "\\" + fname
        print("Image to be read", final_path)

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

        img = cv2.imread(final_path)
        img = imutils.resize(img, width=500)

        #cv2.imshow("Original Image", img)
        cv2.waitKey(0)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #cv2.imshow("Grayscale Image", gray)
        cv2.waitKey(0)

        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        #cv2.imshow("Bilateral Filtered Image", gray)
        cv2.waitKey(0)

        edges = cv2.Canny(img, 170, 200)
        #cv2.imshow("Canny Edged Image", edges)
        cv2.waitKey(0)

        contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        img1 = img.copy()
        cv2.drawContours(img1, contours, -1, (0, 255, 0), 3)
        #cv2.imshow("All Contours", img1)
        cv2.waitKey(0)

        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
        NumberPlateCnt = None

        img2 = img.copy()
        cv2.drawContours(img2, contours, -1, (0, 255, 0), 3)
        #cv2.imshow("Top 10 Contours", img2)
        cv2.waitKey(0)

        count = 0;
        idx = 7
        for c in contours:
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)

            if len(approx) == 4:
                NumberPlateCnt = approx

                x, y, w, h = cv2.boundingRect(c)
                new_img = img[y:y + h, x:x + w]
                cv2.imwrite('Cropped Images-Text' + str(idx) + '.png', new_img)
                idx += 1

                break

        cv2.drawContours(img, [NumberPlateCnt], -1, (0, 255, 0), 3)
        cv2.imshow("Final Image with Number Plate Detected", img)
        cv2.waitKey(0)

        Cropped_img_loc = cv2.imread('Cropped Images-Text7.png')

        text = pytesseract.image_to_string(Cropped_img_loc, lang='eng')
        print("Number is:- {}".format(text))

        cursor, con = dbconnect.connection()

        cursor.execute("select oname,reg_no,maker,model,vehclass,eng_no,chasis_no,regi_date,state,city from owner_info where reg_no='" + text + "'")

        rs = cursor.fetchall()

        cursor.close()

        return 1, text, rs


    result, number, rs = detect(filename)
    if(result):
        return render_template("Complete.html", n=number, r=rs)
    else:
       return render_template("upload.html")



if __name__ == "__main__":
    app.run(debug=True)