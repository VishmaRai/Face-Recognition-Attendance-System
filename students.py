import mysql.connector
from tkinter import END, messagebox
import tkinter as tk
import threading
import cv2
from ttkbootstrap import Style
import ttkbootstrap as ttk
import re

class Student:
    def __init__(self, root):
        # Use the passed root window
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.iconbitmap('icons/face.ico')
        self.root.geometry("1000x700")

        # Create a header frame
        header_frame = ttk.Frame(root, padding="10")
        header_frame.pack(fill="x")

        # Add a header label
        header_label = ttk.Label(header_frame, text="Student Management System", font=("Helvetica", 28, "bold"))
        header_label.pack(pady=10)

        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(expand=True, fill="both")

        # Create the first LabelFrame (left)
        self.label_frame1 = ttk.LabelFrame(self.main_frame, text="Student Information", padding="10")
        self.label_frame1.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Initialize StringVar variables
        self.var_std_id = tk.StringVar()
        self.var_std_name = tk.StringVar()
        self.var_div = tk.StringVar()
        self.var_roll = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_dob = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_address = tk.StringVar()

        # Define a dictionary to loop through and create the entry fields
        student_fields = [
            ("Student ID:", self.var_std_id),
            ("Student Name:", self.var_std_name),
            ("Class and Section:", self.var_div),
            ("Roll No:", self.var_roll),
            ("Gender:", self.var_gender, ["Select Gender", "Male", "Female", "Other"]),
            ("Date of Birth:", self.var_dob),
            ("Email:", self.var_email),
            ("Phone No:", self.var_phone),
            ("Address:", self.var_address)
        ]

        # Generate form fields dynamically
        for i, (label, variable, *combo_options) in enumerate(student_fields):
            ttk.Label(self.label_frame1, text=label, font=("Helvetica", 12, "bold")).grid(row=i, column=0, padx=10, pady=5, sticky=tk.W)
            if combo_options:
                ttk.Combobox(self.label_frame1, textvariable=variable, values=combo_options[0], font=("Helvetica", 12), state="readonly").grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)
            else:
                ttk.Entry(self.label_frame1, textvariable=variable, font=("Helvetica", 12)).grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)

        # Radio buttons
        self.var_radio1 = tk.StringVar()
        radionbtn1 = ttk.Radiobutton(self.label_frame1, variable=self.var_radio1, text="Take a photo sample", value="Yes")
        radionbtn1.grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)
        radionbtn2 = ttk.Radiobutton(self.label_frame1, variable=self.var_radio1, text="No photo sample", value="No")
        radionbtn2.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)

        # Buttons frame
        btn_frame = ttk.Frame(self.label_frame1)
        btn_frame.grid(row=10, column=0, columnspan=2, pady=10)

        # Styled buttons
        ttk.Button(btn_frame, text="Save", style="primary.TButton", command=self.add_data, width=15).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Update", style="warning.TButton", command=self.update_data, width=15).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Delete", style="danger.TButton", command=self.delete_Data, width=15).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Reset", style="secondary.TButton", command=self.reset_data, width=15).grid(row=0, column=3, padx=5, pady=5)

        # Photo buttons frame
        photo_btn_frame = ttk.Frame(self.label_frame1)
        photo_btn_frame.grid(row=11, column=0, columnspan=2, pady=10)
        ttk.Button(photo_btn_frame, text="Take Photo Sample", style="success.TButton", command=self.generate_dataset, width=30).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(photo_btn_frame, text="Update Photo", style="info.TButton", command=self.generate_dataset, width=30).grid(row=0, column=1, padx=5, pady=5)

        # Create the second LabelFrame (right)
        self.label_frame2 = ttk.LabelFrame(self.main_frame, text="Student Details", padding="10")
        self.label_frame2.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Table frame
        table_frame = ttk.Frame(self.label_frame2)
        table_frame.pack(fill="both", expand=True)

        # Create horizontal and vertical scrollbars
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")

        # Create the Treeview widget with correct column configuration
        self.student_table = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Class/Section", "Roll No", "Gender", "DOB", "Email", "Phone", "Address", "Photo Sample Status"),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set
        )

        # Configure the scrollbars to work with the Treeview
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        # Pack the scrollbars
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")

        # Configure the Treeview's columns and headings with a larger font size
        columns = ["ID", "Name", "Class/Section", "Roll No", "Gender", "DOB", "Email", "Phone", "Address", "Photo Sample Status"]
        for col in columns:
            self.student_table.heading(col, text=col, anchor="center")
            self.student_table.column(col, anchor="center", width=150)

        # Show only the headings
        self.student_table["show"] = "headings"

        # Pack the Treeview inside the table_frame
        self.student_table.pack(fill="both", expand=True)

        # Apply alternating row colors for grid-like appearance
        self.student_table.tag_configure('oddrow', background='#E8E8E8')  
        self.student_table.tag_configure('evenrow', background='#DFDFDF')  
        # Bind the Treeview's select event
        self.student_table.bind("<ButtonRelease>", self.get_cursor)

        # Fetch data (this is your custom method to populate the table)
        self.fetch_data()



     #=============Function Declaration(To add data)==============
     
    def add_data(self):
        # Check if any field is empty
        if (not self.var_std_id.get() or not self.var_std_name.get() or
            not self.var_div.get() or not self.var_roll.get() or
            not self.var_gender.get() or not self.var_dob.get() or
            not self.var_email.get() or not self.var_phone.get() or
            not self.var_address.get()or not self.var_radio1.get()):
            messagebox.showerror("ERROR", "All fields are required", parent=self.root)
            return

        # Validate email format using regex
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_pattern, self.var_email.get()):
            messagebox.showerror("ERROR", "Invalid email address!", parent=self.root)
            return

        # Validate phone number (should be numeric and 10 digits)
        if not self.var_phone.get().isdigit() or len(self.var_phone.get()) != 10:
            messagebox.showerror("ERROR", "Phone number must be a 10-digit numeric value!", parent=self.root)
            return

        # Validate date of birth format (DD/MM/YYYY)
        dob_pattern = r"^([0-9]{4})/(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])$"
        if not re.match(dob_pattern, self.var_dob.get()):
            messagebox.showerror("ERROR", "Invalid Date of Birth! Please enter in YYYY/MM/DD format.", parent=self.root)
            return

        # If all validations pass, add data to the database
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='', database='attendence')
            my_cursor = conn.cursor()
            
            # Insert data into the student table
            my_cursor.execute("INSERT INTO student VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                            (self.var_std_id.get(), 
                            self.var_std_name.get(), 
                            self.var_div.get(), 
                            self.var_roll.get(), 
                            self.var_gender.get(), 
                            self.var_dob.get(), 
                            self.var_email.get(), 
                            self.var_phone.get(), 
                            self.var_address.get(), 
                            self.var_radio1.get()))
            
            conn.commit()
            self.fetch_data()
            conn.close()

            messagebox.showinfo("Success", "Student Details have been added successfully", parent=self.root)

        except Exception as es:
            messagebox.showerror("Error", f"Due to: {str(es)}", parent=self.root)

    #==========Fetch Data===============
    def fetch_data(self):
        conn=mysql.connector.connect(host='localhost',    user='root',    password='',    database='attendence')
        my_cursor=conn.cursor()
        my_cursor.execute("SELECT * FROM student")
        data = my_cursor.fetchall()

        if len(data)!=0:
            self.student_table.delete(*self.student_table.get_children())
            for i in data:
                self.student_table.insert("",END,values=i)
            conn.commit()
        conn.close()
        
    #=============Get Cursor==============
    def get_cursor(self,event=""):
        cursor_focus=self.student_table.focus()
        content = self.student_table.item(cursor_focus)
        data=content["values"]
        self.var_std_id.set(data[0]),
        self.var_std_name.set(data[1]),
        self.var_div.set(data[2]),
        self.var_roll.set(data[3]),
        self.var_gender.set(data[4]),
        self.var_dob.set(data[5]),
        self.var_email.set(data[6]),
        self.var_phone.set(data[7]),
        self.var_address.set(data[8]),
        self.var_radio1.set(data[9])
        
    #==============Update Function=================
    def update_data(self): #ERROR
        if self.var_std_id.get()=="Select Student_id" or self.var_std_name.get()==""or self.var_radio1.get()=="":
            messagebox.showerror("ERROR","All fields are required",parent=self.root)
        else:
            try:
                Update = messagebox.askyesno("Update","Do you want to update this student details?", parent = self.root)
                if Update>0:
                    conn = mysql.connector.connect(host='localhost',    user='root',    password='',    database='attendence')

                    my_cursor=conn.cursor()
                    my_cursor.execute("Update student SET  Name=%s , Division=%s , Roll=%s , Gender=%s , Dob=%s , Email=%s , Phone=%s , Address=%s , PhotoSample=%s where Student_id=%s",(self.var_std_name.get(),self.var_div.get(),self.var_roll.get(),self.var_gender.get(),self.var_dob.get(),self.var_email.get(),self.var_phone.get(),self.var_address.get(),self.var_radio1.get(),self.var_std_id.get()))
                else:
                    if not Update:
                        return
                messagebox.showinfo("Success","Student Details Successfully Updated.",parent = self.root)
                conn.commit()
                self.fetch_data() 
                conn.close()
            except Exception as es:
                messagebox.showerror("Error",f"Due to : {str(es)}", parent=self.root)

    #===================Delete Function============
    def delete_Data(self):
        if self.var_std_id.get()=="":
            messagebox.showerror("Error", "Student ID is required!", parent=self.root)
        else:
            try:
                delete=messagebox.askyesno("Student Delete Page","Do you want to delete this student details?", parent=self.root)
                if delete>0:
                    conn=mysql.connector.connect(host='localhost',    user='root',    password='',    database='attendence')
                    my_cursor=conn.cursor()
                    sql="DELETE FROM student WHERE Student_id=%s"
                    val=(self.var_std_id.get(),)
                    my_cursor.execute(sql,val)
                else:
                    if not delete:
                        return
                conn.commit()
                self.fetch_data()
                conn.close()
                messagebox.showinfo("Success","Student Details Successfully Deleted.",parent = self.root)
            except Exception as es:
                messagebox.showerror("Error",f"Due to : {str(es)}", parent=self.root)
    
    #Reset Function
    def reset_data(self):
        self.var_std_id.set(""),
        self.var_std_name.set(""),
        self.var_div.set(""),
        self.var_roll.set(""),
        self.var_gender.set("Select Gender"),
        self.var_dob.set(""),
        self.var_email.set(""),
        self.var_phone.set(""),
        self.var_address.set(""),
        self.var_radio1.set("")

        
    #===================Ganerate data set and Take Photo Sample===============
    def generate_dataset(self):
        if self.var_std_id.get()=="Select Student_id" or self.var_std_name.get()==""or self.var_radio1.get()=="":
            messagebox.showerror("ERROR", "All fields are required", parent=self.root)
        else:
            # Start the threading process for capturing images
            capture_thread = threading.Thread(target=self.capture_images_and_update_database)
            capture_thread.start()

    def capture_images_and_update_database(self):
        try:
            conn = mysql.connector.connect(
                host='localhost', user='root', password='', database='attendence'
            )
            my_cursor = conn.cursor()

            # Update the student record
            my_cursor.execute("""
                UPDATE Student 
                SET Name=%s, Division=%s, Roll=%s, 
                    Gender=%s, Dob=%s, Email=%s, Phone=%s, Address=%s, PhotoSample=%s 
                WHERE Student_id=%s
                """, (
                    self.var_std_name.get(), self.var_div.get(), self.var_roll.get(), 
                    self.var_gender.get(), self.var_dob.get(), self.var_email.get(), 
                    self.var_phone.get(), self.var_address.get(),  
                    self.var_radio1.get(), self.var_std_id.get()
                )
            )
            conn.commit()

            # Load predefined data on face frontals from OpenCV
            face_classifier = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

            def face_cropped(img):
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_classifier.detectMultiScale(gray, 1.3, 5)
                if len(faces) == 0:
                    return None
                for (x, y, w, h) in faces:
                    face_cropped = img[y:y+h, x:x+w]
                    return face_cropped

            cap = cv2.VideoCapture(1)
            img_id = 0
            while True:
                ret, my_frame = cap.read()
                if face_cropped(my_frame) is not None:
                    img_id += 1
                    face = cv2.resize(face_cropped(my_frame), (550, 550))
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                    file_name_path = f"data/user.{self.var_std_id.get()}.{img_id}.jpg"
                    cv2.imwrite(file_name_path, face)
                    cv2.putText(face, str(img_id), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 2)
                    cv2.imshow("Capture Face", face)

                if cv2.waitKey(1) == 13 or int(img_id) == 100:
                    break
            cap.release()
            cv2.destroyAllWindows()

            # Show a success message on the main thread
            self.root.after(0, lambda: messagebox.showinfo("Result", "Generating data sets completed!"))

        except Exception as es:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Due to : {str(es)}", parent=self.root))
        finally:
            conn.close()


if __name__ == "__main__":
    root = tk.Tk()  # Create the Tk instance
    app = Student(root)  # Pass the Tk instance to the Student class
    root.mainloop()  # Start the main event loop
