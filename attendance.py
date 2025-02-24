import os
import mysql.connector
from tkinter import END, StringVar, messagebox
import tkinter as tk
import threading
import cv2
from ttkbootstrap import Style
import ttkbootstrap as ttk
from tkinter import filedialog
import csv

mydata = []
class Attendance:
    def __init__(self, root):
        # Use the passed root window
        self.root = root
        self.root.title("Attendance Management System")
        self.root.iconbitmap('icons/face.ico')
        self.root.geometry("1000x700")
        
        # Apply the dark style
        

        #==========Variables==========
        self.var_atten_id = StringVar()
        self.var_atten_roll = StringVar()  # For later use
        self.var_atten_name = StringVar()
        self.var_atten_time = StringVar()
        self.var_atten_date = StringVar()
        self.var_atten_attendance = StringVar()

        # Create a header frame
        header_frame = ttk.Frame(root, padding="10")
        header_frame.pack(fill="x")

        # Add a header label
        header_label = ttk.Label(header_frame, text="Attendance Management System", font=("Helvetica", 28, "bold"))
        header_label.pack(pady=10)

        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(expand=True, fill="both")

        # Create the first LabelFrame (left)
        self.label_frame1 = ttk.LabelFrame(self.main_frame, text="Student Attendance Details", padding="10")
        self.label_frame1.pack(side="left", expand=True, fill="both", padx=10, pady=10)

        # Inside left frame: Attendance ID
        attendanceId_label = ttk.Label(self.label_frame1, text="Attendance ID:", font=("times new roman", 12, "bold"), foreground="white")
        attendanceId_label.grid(row=0, column=0, padx=10, sticky=tk.W)

        attendanceID_entry = ttk.Entry(self.label_frame1, width=15, textvariable=self.var_atten_id, font=("times new roman", 12, "bold"))
        attendanceID_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Roll No
        roll_label = ttk.Label(self.label_frame1, text="Roll No:", font=("times new roman", 12, "bold"), foreground="white")
        roll_label.grid(row=0, column=2, padx=10, sticky=tk.W)

        roll_entry = ttk.Entry(self.label_frame1, width=15, textvariable=self.var_atten_roll, font=("times new roman", 12, "bold"))
        roll_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

        # Name
        name_label = ttk.Label(self.label_frame1, text="Name:", font=("times new roman", 12, "bold"), foreground="white")
        name_label.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        name_entry = ttk.Entry(self.label_frame1, width=15, textvariable=self.var_atten_name, font=("times new roman", 12, "bold"))
        name_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Time
        time_label = ttk.Label(self.label_frame1, text="Time:", font=("times new roman", 12, "bold"), foreground="white")
        time_label.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        time_entry = ttk.Entry(self.label_frame1, width=15, textvariable=self.var_atten_time, font=("times new roman", 12, "bold"))
        time_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Date
        date_label = ttk.Label(self.label_frame1, text="Date:", font=("times new roman", 12, "bold"), foreground="white")
        date_label.grid(row=2, column=2, padx=10, pady=5, sticky=tk.W)

        date_entry = ttk.Entry(self.label_frame1, width=15, textvariable=self.var_atten_date, font=("times new roman", 12, "bold"))
        date_entry.grid(row=2, column=3, padx=10, pady=5, sticky=tk.W)

        # Attendance Status
        attendance_label = ttk.Label(self.label_frame1, text="Attendance Status:", font=("times new roman", 12, "bold"), foreground="white")
        attendance_label.grid(row=3, column=0, padx=10, sticky=tk.W)

        attendance_combo = ttk.Combobox(self.label_frame1, textvariable=self.var_atten_attendance, font=("times new roman", 12, "bold"), width=13, state="readonly")
        attendance_combo["values"] = ("Status", "Present", "Absent")
        attendance_combo.current(0)
        attendance_combo.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        # Button Frame
        btn_frame = ttk.Frame(self.label_frame1)
        btn_frame.grid(row=4, column=0, columnspan=4, pady=20)

        # Buttons
        import_btn = ttk.Button(btn_frame, text="Import CSV", command=self.import_csv, width=15, bootstyle="success")
        import_btn.grid(row=0, column=0, padx=5, pady=5)

        update_btn = ttk.Button(btn_frame, text="Update", command=self.update_data, width=15, bootstyle="primary")
        update_btn.grid(row=0, column=2, padx=5, pady=5)

        reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset_data, width=15, bootstyle="warning")
        reset_btn.grid(row=0, column=3, padx=5, pady=5)

       # Create the second LabelFrame (right) for Attendance Details
        self.label_frame2 = ttk.LabelFrame(self.main_frame, text="Attendance Details", padding="10")
        self.label_frame2.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        # Table Frame
        table_frame = ttk.Frame(self.label_frame2)
        table_frame.pack(expand=True, fill="both")

        # Scroll Bars
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")

        # TreeView Table for Attendance Data
        self.AttendanceReportTable = ttk.Treeview(
            table_frame,
            columns=("ID", "Roll", "Name", "Time", "Date", "Attendance"),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set
        )

        # Configure Scroll Bars
        scroll_x.config(command=self.AttendanceReportTable.xview)
        scroll_y.config(command=self.AttendanceReportTable.yview)

        # Pack Scroll Bars
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")

        # Configure TreeView Headings and Columns
        columns = ["ID", "Roll", "Name", "Time", "Date", "Attendance"]
        heading_names = ["Attendance ID", "Roll No", "Name", "Time", "Date", "Attendance"]

        for col, heading_name in zip(columns, heading_names):
            self.AttendanceReportTable.heading(col, text=heading_name, anchor="center")
            self.AttendanceReportTable.column(col, anchor="center", width=150)

        # Show only the headings
        self.AttendanceReportTable["show"] = "headings"

        # Pack the TreeView inside the table_frame
        self.AttendanceReportTable.pack(fill="both", expand=True)

        # Apply alternating row colors for a grid-like appearance
        self.AttendanceReportTable.tag_configure('oddrow', background='#E8E8E8') 
        self.AttendanceReportTable.tag_configure('evenrow', background='#DFDFDF')  

        # Bind the TreeView's select event
        self.AttendanceReportTable.bind("<ButtonRelease>", self.get_cursor)
        
    #=======Fetch Data========
    def fetchData(self,rows):
        self.AttendanceReportTable.delete(*self.AttendanceReportTable.get_children())
        for i in rows:
            self.AttendanceReportTable.insert("",END,values=i)

    # Function to handle importing CSV
    def import_csv(self):
        global mydata
        mydata.clear()
        fln=filedialog.askopenfilename(initialdir=os.getcwd(),title="Open CSV", filetypes=(("CSV File","*.csv"),("ALL File","*.*")),parent=self.root)
        with open(fln) as myfile:
            csvread=csv.reader(myfile,delimiter=",")
            for i in csvread:
                mydata.append(i)
            self.fetchData(mydata)
            
    # Function to handle clicking on a row in the table
    def get_cursor(self, event):
        cursor_row=self.AttendanceReportTable.focus()
        content = self.AttendanceReportTable.item(cursor_row)
        rows=content["values"]
        self.var_atten_id.set(rows[0]),
        self.var_atten_roll.set(rows[1]),
        self.var_atten_name.set(rows[2]),
        self.var_atten_time.set(rows[3]),
        self.var_atten_date.set(rows[4]),
        self.var_atten_attendance.set(rows[5])
            
    # Function to reset data
    def reset_data(self):
        self.var_atten_id.set(""),
        self.var_atten_roll.set(""),
        self.var_atten_name.set(""),
        self.var_atten_time.set(""),
        self.var_atten_date.set(""),
        self.var_atten_attendance.set("Status")
       

    # Function to handle updating data
    def update_data(self):
        id = self.var_atten_id.get()
        roll = self.var_atten_roll.get()
        name = self.var_atten_name.get()
        time = self.var_atten_time.get()
        date = self.var_atten_date.get()
        attendn = self.var_atten_attendance.get()

        # Write only data to CSV file (without headers)
        try:
            fln = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                title="Save CSV",
                filetypes=(("CSV file", "*.csv"), ("All Files", "*.*")),
                parent=self.root
            )

            # Open file in append mode without writing headers
            with open(fln, mode="a", newline="\n") as f:
                dict_writer = csv.DictWriter(f, fieldnames=["ID", "Roll", "Name", "Time", "Date", "Attendance"])
                
                # Only write the row (no header)
                dict_writer.writerow({
                    "ID": id,
                    "Roll": roll,
                    "Name": name,
                    "Time": time,
                    "Date": date,
                    "Attendance": attendn
                })
            
            messagebox.showinfo("Data Exported", "Your data was exported to " + os.path.basename(fln) + " successfully", parent=self.root)
            self.reset_data()

        except Exception as es:
            messagebox.showerror("Error", f"Due to: {str(es)}", parent=self.root)





if __name__ == "__main__":
    root = tk.Tk()  # Create the Tk instance
    app = Attendance(root)  # Pass the Tk instance to the Student class
    root.mainloop()
