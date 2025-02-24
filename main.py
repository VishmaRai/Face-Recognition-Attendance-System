from datetime import datetime
import os
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
import cv2
import numpy as np
from ttkbootstrap import Style
import ttkbootstrap as ttk
from attendance import Attendance
from students import Student
import mysql.connector
import threading

class Face_Recognition_System:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.iconbitmap('icons/face.ico')
        self.root.geometry("1000x700")

        # Apply the dark style
        style = Style(theme="solar")
        style.theme_use()
        
        # Configure the Treeview style for alternating row colors
        style.configure("Treeview", rowheight=25, font=("Helvetica", 11))  # General row style
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), background="#4a4a4a", foreground="white")  # For headings
        style.map("Treeview", background=[("selected", "#2a9d8f")])  # Highlight se

        # Create a header frame
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill="x")

        # Add a header label
        header_label = ttk.Label(header_frame, text="Face Recognition Attendance System", font=("Helvetica", 25, "bold"))
        header_label.pack(pady=10)

        # Create a frame to hold the buttons
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True, fill="both")

        # Load and resize icons using Pillow
        icon_size = (100, 100)
        self.manage_icon = ImageTk.PhotoImage(Image.open("icons/manage.png").resize(icon_size))
        self.recognition_icon = ImageTk.PhotoImage(Image.open("icons/recognize.png").resize(icon_size))
        self.attendance_icon = ImageTk.PhotoImage(Image.open("icons/attendance.png").resize(icon_size))
        self.training_icon = ImageTk.PhotoImage(Image.open("icons/training.png").resize(icon_size))

        # Create a custom button style
        style.configure('Large.TButton', font=('Helvetica', 15, 'bold'), foreground=style.colors.success, background=style.colors.dark, bordercolor=style.colors.success, relief="solid", borderwidth=5)

        # Change the hover color
        style.map(
            "Large.TButton",
            background=[("active", style.colors.light)],
            foreground=[("active", style.colors.dark)],
            bordercolor=[("active", style.colors.success)]
        )

        # Create the buttons with icons
        btn_manage = ttk.Button(frame, text="Manage Students", image=self.manage_icon, compound=tk.LEFT, style="Large.TButton", width=20,command=self.student_details, cursor="hand2")
        btn_recognition = ttk.Button(frame, text="Face Recognition", image=self.recognition_icon, compound=tk.LEFT, style="Large.TButton", width=20, cursor="hand2",command=self.face_recog)
        btn_attendance = ttk.Button(frame, text="Attendance", image=self.attendance_icon, compound=tk.LEFT, style="Large.TButton", width=20, cursor="hand2", command=self.attendance_data)
        btn_training = ttk.Button(frame, text="Face Training", image=self.training_icon, compound=tk.LEFT, style="Large.TButton", width=20, cursor="hand2", command=self.train_classifier)

        # Place the buttons in the frame
        btn_manage.pack(pady=10)
        btn_recognition.pack(pady=10)
        btn_attendance.pack(pady=10)
        btn_training.pack(pady=10)

        # Create a footer frame
        footer_frame = ttk.Frame(self.root, padding="10")
        footer_frame.pack(fill="x", side="bottom")

        # Add a footer label
        footer_label = ttk.Label(footer_frame, text="Version 1.0.0", font=("Helvetica", 10))
        footer_label.pack(side="right")
        
        
#===========training data==============
    def train_classifier(self):
        data_dir=("data")
        path=[os.path.join(data_dir,file) for file in os.listdir(data_dir)]
        faces=[]
        ids=[]
        for image in path:
            img=Image.open(image).convert('L') #GreyScale Img
            imageNp = np.array(img,'uint8')
            id=int(os.path.split(image)[1].split('.')[1])
            faces.append(imageNp)
            ids.append(id)
            cv2.imshow("Training...",imageNp)
            cv2.waitKey(1)==13
        ids=np.array(ids)

#====== Train Classifier and Save ======
        clf= cv2.face.LBPHFaceRecognizer_create()
        clf.train(faces,ids)
        clf.write("classifier.xml")
        cv2.destroyAllWindows()
        messagebox.showinfo("Result","Training datasets completed.")
        
   
#=============Attendance===============
    def mark_attendance(self,i,r,n):
        with open("attendance/Attendance.csv","r+",newline="\n") as f:
            myDataList = f.readlines()
            name_list=[]
            for line in myDataList:
                entry=line.split((","))
                name_list.append(entry[0])
            if((i not in name_list) and (r not in name_list) and (n not in name_list)):
                now = datetime.now()
                d1=now.strftime("%d/%m/%y")
                dtString=now.strftime("%H:%M:%S")
                f.writelines(f"\n{i},{r},{n},{dtString},{d1},Present")     

#=================Face Recognization=======================
    def face_recog(self):
        def draw_boundary(img,classifier,scaleFactor,minNeighbour,color,text,clf):
            gray_image=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            features=classifier.detectMultiScale(gray_image,scaleFactor,minNeighbour)
            
            coord=[]
            for(x,y,w,h) in features:
                cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                id,predict=clf.predict(gray_image[y:y+h,x:x+w])
                confidence=int((100*(1-predict/300)))
                conn= mysql.connector.connect(host='localhost',    user='root',    password='',    database='attendence')
                # Fetch the name from the database
                my_cursor = conn.cursor()
                my_cursor.execute("SELECT Name FROM student WHERE Student_id = " + str(id))
                n = my_cursor.fetchone()
                if n:  # Check if a result was returned
                    n = n[0]  # Extract the first element from the tuple

                # Fetch the roll from the database
                my_cursor.execute("SELECT Roll FROM student WHERE Student_id = " + str(id))
                r = my_cursor.fetchone()
                if r:  # Check if a result was returned
                    r = r[0]  # Extract the first element from the tuple
        

                my_cursor.execute("SELECT Student_id FROM student where Student_id="+str(id))
                i = my_cursor.fetchone()
                if i:  # Check if a result was returned
                    i = i[0]  # Extract the first element from the tuple

                if confidence>80:
                    cv2.putText(img,f"Name:{n}",(x,y-55),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),1)
                    cv2.putText(img,f"Roll_no:{r}",(x,y-30),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),1)
                    # cv2.putText(img,f"Stuent_id:{i}",(x,y-80),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),1)                    self.mark_attendance(i,r,n,d)
                    self.mark_attendance(i,r,n)
                else:
                    cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
                    cv2.putText(img,"Unknown Face",(x,y-5),cv2.FONT_HERSHEY_COMPLEX,0.8,(255,255,255),1)
                    
                coord=[x,y,w,h]

            return coord
        def recognize(img,clf,faceCascade):
            coord =draw_boundary(img,faceCascade,1.1,10,(255,255,255),"Face",clf)
            return img

        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("classifier.xml")

        video_cap=cv2.VideoCapture(1)

        while True:
            ret,img=video_cap.read()
            img=recognize(img,clf,faceCascade)
            cv2.imshow("Welcome To Face Recognition",img)
            
            if cv2.waitKey(1) == 13:
                break
    
        video_cap.release()
        cv2.destroyAllWindows()

        
        
    #===============FUNCTIONS BUTTONS=================
    # In the Face_Recognition_System class
    def student_details(self):
        self.new_window = tk.Toplevel(self.root)
        self.app = Student(self.new_window)
        
    def attendance_data(self):
        self.new_window = tk.Toplevel(self.root)
        self.app = Attendance(self.new_window)
        
    

if __name__ == "__main__":
    root = tk.Tk()
    app = Face_Recognition_System(root)
    root.mainloop()
