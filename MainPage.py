import PySimpleGUI as sg
import sqlite3
import cv2
import os
import shutil
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import functions

con = sqlite3.connect('uservisit.db')


def view_users():
    sg.theme('DarkBlue2')
    con = sqlite3.connect('uservisit.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM user")
    data = cur.fetchall()
    if len(data) > 0:
        headings = ['User ID', 'Full Name', 'Mobile', 'Email ID', 'Address']
        layout = [[sg.Text("VIEW USERS", size=(30, 1), justification='center', font='Helvetica 22')],
                  [sg.Frame(layout=[[sg.Table(values=data, headings=headings, alternating_row_color='blue',
                                              enable_events=True, key='--row--')]], title='VIEW SECURITY',
                            relief=sg.RELIEF_GROOVE)]]
        view_user_window = sg.Window('View Users', layout)
        while True:
            event, values = view_user_window.read()
            if event in (None, 'Exit'):
                break
    else:
        sg.popup_error("No Users Found! Please Add Users!")


def userUpdate():
    layout = [
        [sg.Text('USER DETAILS UPDATE', font=('Century Gothic', 18), justification='center', size=(30, 2))],
        [sg.Frame(layout=[
            [sg.Text("Enter User ID", size=(15, 1)), sg.Input('', key='uid'), sg.Button('Search', key='--search--')]],
            title='ENTER USER ID', relief=sg.RELIEF_GROOVE)],
        [sg.Frame(title='UPDATE DETAILS', layout=[
            [sg.Text('Full Name'), sg.Input('', key='-FLNAME-')],
            [sg.Text('Email ID'), sg.Input('', key='-EMAIL-')],
            [sg.Text('Mobile No'), sg.Input('', key='-MOBILE-')],
            [sg.Text('Address'), sg.Input('', key='-ADDRESS-')],
            [sg.Multiline('', key='-NOTES-')],
            [sg.Submit(), sg.Cancel()]
        ], element_justification='center')]
    ]
    update_user = sg.Window('UPDATE USER', layout, element_justification='center')
    while True:
        events, values = update_user.Read()
        if events in (None, 'Exit'):
            break
        elif events == '--search--':
            uid = values['uid']
            print(uid)
            if (uid == ''):
                sg.popup_error("Please Enter UID!")
            else:
                con = sqlite3.connect('uservisit.db')
                cur = con.cursor()
                cur.execute("SELECT user.*,Notes.* FROM user,Notes WHERE user.user_id=? AND Notes.user_id=user.user_id",
                            (uid,))
                data = cur.fetchall()
                if len(data) > 0:
                    for lol in data:
                        update_user['-FLNAME-'].update(lol[1])
                        update_user['-EMAIL-'].update(lol[2])
                        update_user['-MOBILE-'].update(lol[3])
                        update_user['-ADDRESS-'].update(lol[4])
                        update_user['-NOTES-'].update(lol[7])
                else:
                    sg.PopupError("User Not Found!")
    update_user.Close()


def userRegister():
    layout = [
        [sg.Text('VISITOR REGISTRATION', font=('Century Gothic', 18), justification='center', size=(30, 1))],
        [sg.Frame(title='REGISTER', layout=[
            [sg.Text('Enter Full Name', size=(15, 1)), sg.Input('', key='-FLNAME-')],
            [sg.Text('Enter Email ID', size=(15, 1)), sg.Input('', key='-EMAIL-')],
            [sg.Text('Enter Mobile No', size=(15, 1)), sg.Input('', key='-MOBILE-')],
            [sg.Text('Enter Address', size=(15, 1)), sg.Input('', key='-ADDRESS-')],
            [sg.Text('Enter Notes', size=(15, 1)), sg.Multiline('', key='-NOTES-')],
            [sg.Submit(), sg.Cancel()]
        ], element_justification='center')]
    ]
    user_register_window = sg.Window('VISITOR REGISTER', layout, element_justification='center')
    while True:
        events, values = user_register_window.Read()
        if events in (None, 'Exit'):
            break
        elif events == 'Submit':
            flname = values['-FLNAME-']
            email = values['-EMAIL-']
            mobile = values['-MOBILE-']
            address = values['-ADDRESS-']
            notes = values['-NOTES-']
            if flname == '' or email == '' or mobile == '' or address == '':
                sg.PopupError("Please enter all Details!")
            else:
                if notes == '':
                    notes = "HI"
                cur = con.cursor()
                cur.execute("INSERT INTO user(user_flname,user_email,user_mobile,user_address) VALUES(?,?,?,?)",
                            (flname, email, mobile, address))
                con.commit()
                if cur.rowcount == 1:
                    lastid = cur.lastrowid
                    cur.close()
                    cur = con.cursor()
                    cur.execute("INSERT INTO Notes(user_id,note) VALUES(?,?)", (lastid, notes))
                    con.commit()
                    sg.PopupQuickMessage("USER DATA SAVED SUCCESSFULLY \n Opening Camera to Start Capture Images...",
                                         background_color='green', font=('Century Gothic', 14), text_color='white')
                    message = functions.TakeImages(lastid)
                    if message == "SUCCESS":
                        sg.PopupQuickMessage("DATASET CREATED SUCCESSFULLY FOR NAME " + flname,
                                             background_color='green', text_color='white')
                        user_register_window.Close()
                    elif message == "ERRORFOLDER":
                        sg.PopupQuickMessage("DATASET ALREADY CREATED!", background_color='red', text_color='white')
                else:
                    sg.PopupError("Something Went Wrong! Please Try Again!")
        elif events == 'Cancel':
            user_register_window['-FLNAME-'].Update('')
            user_register_window['-EMAIL-'].Update('')
            user_register_window['-MOBILE-'].Update('')
            user_register_window['-ADDRESS-'].Update('')
            user_register_window['-NOTES-'].update('')
    user_register_window.Close()


def admin_main_page():
    layout = [
        [sg.Text('ADMIN DASHBOARD', justification='center')],
        [sg.Frame(title='OPTIONS', layout=[
            [sg.Button('ADD USER', key='-ADD-', size=(30, 3))],
            [sg.Button('UPDATE USER', key='-UPDATEUSER-', size=(30, 3))],
            [sg.Button('VIEW USERS', key='-VIEWUSER-', size=(30, 3))],
            [sg.Button('TRAIN', key='-TRAIN-', size=(30, 3))],
            [sg.Button('START DOOR CAM', key='-RECOGNIZE-', size=(30, 3))],
            [sg.Button('UPDATE DETAILS', key='-UPDATE-', size=(30, 3))],
            [sg.Button('LOGOUT', key='-LOGOUT-', size=(30, 3))],
        ], element_justification='center')]
    ]
    admin_main_window = sg.Window('ADMIN DASHBOARD', layout, element_justification='center')
    while True:
        events, values = admin_main_window.Read()
        if events in (None, 'Exit'):
            break
        elif events == '-LOGOUT-':
            admin_main_window.Close()
        elif events == '-ADD-':
            userRegister()
        elif events == '-TRAIN-':
            sg.PopupQuickMessage("TRAINING THE DATA... \n PLEASE WAIT...",
                                 background_color='green', font=('Century Gothic', 14), text_color='white')
            functions.TrainImages()
            sg.PopupQuickMessage("TRAINING COMPLETE",
                                 background_color='green', font=('Century Gothic', 20), text_color='white')
        elif events == '-UPDATEUSER-':
            userUpdate()
        elif events == '-RECOGNIZE-':
            sg.PopupQuickMessage("STARTING FACE RECOGNITION... \n PLEASE WAIT...",
                                 background_color='green', font=('Century Gothic', 14), text_color='white')
            functions.FaceRecognition()
        elif events == '-VIEWUSER-':
            view_users()
    admin_main_window.Close()


def admin_login():
    layout = [
        [sg.Text('ADMIN LOGIN', justification='center')],
        [sg.Text('Username '), sg.Input('', key='-UNAME-')],
        [sg.Text('Password'), sg.Input('', key='-PASSWORD-', password_char="*")],
        [sg.Button('Login'), sg.Cancel()]
    ]
    admin_login_window = sg.Window('ADMIN LOGIN', layout, element_justification='center')
    while True:
        events, values = admin_login_window.Read()
        if events in (None, 'Exit'):
            break
        elif events == 'Cancel':
            admin_login_window['-UNAME-'].Update('')
            admin_login_window['-PASSWORD-'].Update('')
        elif events == 'Login':
            username = str(values['-UNAME-'])
            password = str(values['-PASSWORD-'])
            if username == '' or password == '':
                sg.PopupError("Please Enter All the Fields!")
            else:
                cur = con.cursor()
                cur.execute("SELECT * FROM admin WHERE admin_uname=? AND admin_password=?", (username, password))
                result = len(cur.fetchall())
                if result == 1:
                    sg.PopupOK("Login Successful!")
                    admin_login_window.Close()
                    main_window.Close()
                    admin_main_page()
                else:
                    sg.PopupError("Invalid Login Credentials!")

    admin_login_window.Close()
    main_window.UnHide()


sg.theme('DarkRed21')
layout = [
    [sg.Image('mainimage.png')],
    [sg.Text('VISITOR RECOGNIZER', font=('Century Gothic', 25), justification='center', size=(30, 1))],
    [sg.Button('ADMIN LOGIN', key='-LOGIN-', size=(30, 3)), sg.Exit(size=(30, 3))]
]
main_window = sg.Window('Main Window', layout, element_justification='center')
while True:
    events, values = main_window.Read()
    if events in (None, 'Exit'):
        break
    if events == '-LOGIN-':
        main_window.Hide()
        admin_login()

main_window.Close()
