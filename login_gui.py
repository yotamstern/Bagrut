from tkinter import *
from pymongo import MongoClient
import bcrypt
from bson.objectid import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["LiveStreamApp"]
users_collection = db["users"]
streams_collection = db["streams"]


def register_user(username, password, confirm_password):
    if password != confirm_password:
        return "Passwords do not match!"
    if users_collection.find_one({"username": username}):
        return "Username already exists!"

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user = {"username": username, "password_hash": hashed_pw, "streams": []}
    users_collection.insert_one(user)
    return "User registered successfully!"


def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        return "Login successful!"
    return "Invalid username or password!"


def join_stream(stream_id):
    stream = streams_collection.find_one({"_id": ObjectId(stream_id)})
    if stream:
        return f"Joined stream {stream['name']}"
    else:
        return "Stream not found!"


def show_main_screen():
    clear_screen()
    Label(root, text="Login", font=("Arial", 20)).place(relx=0.5, rely=0.35, anchor=CENTER)
    Button(root, text="Login", fg="red", font=("Arial", 16), command=show_login_screen).place(relx=0.5, rely=0.45,
                                                                                              anchor=CENTER)
    Label(root, text="Sign Up", font=("Arial", 20)).place(relx=0.5, rely=0.55, anchor=CENTER)
    Button(root, text="Sign Up", fg="blue", font=("Arial", 16), command=show_signup_screen).place(relx=0.5, rely=0.65,
                                                                                                  anchor=CENTER)


def show_dashboard():
    clear_screen()
    Button(root, text="Create Stream", font=("Arial", 16), command=create_stream).place(relx=0.3, rely=0.3,
                                                                                        anchor=CENTER)
    Label(root, text="Join Stream", font=("Arial", 16)).place(relx=0.7, rely=0.3, anchor=CENTER)

    # Adding a text box for Stream ID input
    stream_id_label = Label(root, text="Enter Stream ID:", font=("Arial", 14))
    stream_id_label.place(relx=0.7, rely=0.4, anchor=CENTER)

    stream_id_entry = Entry(root, font=("Arial", 14))
    stream_id_entry.place(relx=0.7, rely=0.45, anchor=CENTER)

    # Adding a join button
    def attempt_join_stream():
        stream_id = stream_id_entry.get()
        message = join_stream(stream_id)
        Label(root, text=message, font=("Arial", 14)).place(relx=0.7, rely=0.5, anchor=CENTER)

    join_button = Button(root, text="Join", font=("Arial", 14), command=attempt_join_stream)
    join_button.place(relx=0.7, rely=0.57, anchor=CENTER)


def show_login_screen():
    clear_screen()
    Label(root, text="Welcome to the Login Page", font=("Arial", 24)).place(relx=0.5, rely=0.2, anchor=CENTER)

    Label(root, text="Username:", font=("Arial", 16)).place(relx=0.4, rely=0.4, anchor=CENTER)
    username_entry = Entry(root, font=("Arial", 16))
    username_entry.place(relx=0.55, rely=0.4, anchor=CENTER)

    Label(root, text="Password:", font=("Arial", 16)).place(relx=0.4, rely=0.5, anchor=CENTER)
    password_entry = Entry(root, font=("Arial", 16), show='*')
    password_entry.place(relx=0.55, rely=0.5, anchor=CENTER)

    def attempt_login():
        message = login_user(username_entry.get(), password_entry.get())
        if "successful" in message:
            show_dashboard()
        else:
            Label(root, text=message, font=("Arial", 14)).place(relx=0.5, rely=0.7, anchor=CENTER)

    Button(root, text="Login", font=("Arial", 16), fg="green", command=attempt_login).place(relx=0.5, rely=0.6,
                                                                                            anchor=CENTER)
    Button(root, text="Back", font=("Arial", 16), fg="black", command=show_main_screen).place(relx=0.5, rely=0.8,
                                                                                              anchor=CENTER)


def show_signup_screen():
    clear_screen()
    Label(root, text="Welcome to the Sign Up Page", font=("Arial", 24)).place(relx=0.5, rely=0.2, anchor=CENTER)

    Label(root, text="Username:", font=("Arial", 16)).place(relx=0.4, rely=0.4, anchor=CENTER)
    username_entry = Entry(root, font=("Arial", 16))
    username_entry.place(relx=0.55, rely=0.4, anchor=CENTER)

    Label(root, text="Password:", font=("Arial", 16)).place(relx=0.4, rely=0.5, anchor=CENTER)
    password_entry = Entry(root, font=("Arial", 16), show='*')
    password_entry.place(relx=0.55, rely=0.5, anchor=CENTER)

    Label(root, text="Confirm Password:", font=("Arial", 16)).place(relx=0.4, rely=0.6, anchor=CENTER)
    confirm_password_entry = Entry(root, font=("Arial", 16), show='*')
    confirm_password_entry.place(relx=0.55, rely=0.6, anchor=CENTER)

    def attempt_signup():
        message = register_user(username_entry.get(), password_entry.get(), confirm_password_entry.get())
        if "successfully" in message:
            show_dashboard()
        else:
            Label(root, text=message, font=("Arial", 14)).place(relx=0.5, rely=0.8, anchor=CENTER)

    Button(root, text="Sign Up", font=("Arial", 16), fg="blue", command=attempt_signup).place(relx=0.5, rely=0.7,
                                                                                              anchor=CENTER)
    Button(root, text="Back", font=("Arial", 16), fg="black", command=show_main_screen).place(relx=0.5, rely=0.85,
                                                                                              anchor=CENTER)


def create_stream():
    Label(root, text="Stream Created!", font=("Arial", 14)).place(relx=0.3, rely=0.4, anchor=CENTER)


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


root = Tk()
root.title("Yotam's Project")
root.geometry('1920x1080')

show_main_screen()
root.mainloop()
