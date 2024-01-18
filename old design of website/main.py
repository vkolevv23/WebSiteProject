import streamlit as st
import mysql.connector
from streamlit_option_menu import option_menu
import base64
from streamlit_calendar import calendar
from datetime import datetime
import re

def sql_connection():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="501219admin$",
            database="barbershop_db"
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as e:
        st.error(f"Грешка при свързването с базата данни: {e}")
        return None


connection = sql_connection()
cursor = connection.cursor()

sql_query = "SELECT username FROM REGISTRATIONS"
cursor.execute(sql_query)
get_usernames = cursor.fetchall()

sql_query = "SELECT password FROM REGISTRATIONS"
cursor.execute(sql_query)
get_passwords = cursor.fetchall()

sql_query = "SELECT email FROM REGISTRATIONS"
cursor.execute(sql_query)
get_emails = cursor.fetchall()

passwords = [lis[-1] for lis in get_passwords]
usernames = [lis[-1] for lis in get_usernames]
mails = [lis[-1] for lis in get_emails]


def main_page():
    img_path = "C:\\Users\\vaset\\PycharmProjects\\BarbershopProject\\sidebar_photo4.png"
    # img_path2 = "C:\\Users\\vaset\\PycharmProjects\\BarbershopProject\\bb1.png"
    bg = "png"

    styling = f'''
   <style>
    [data-testid="stAppViewContainer"]
    {{
     background-color: rgba(246, 246, 246);
     background-position: center ;
     background-size: cover;
     text-align: center;
    }}

    [data-testid="stSidebar"]
    {{
     background: url(data:image/{bg};base64,{base64.b64encode(open(img_path, "rb").read()).decode()});
     background-position: left ;
     background-size: cover;
     text-align: left;
    }}

    [data-testid="StyledLinkIconContainer"]
    {{
      color: black;
      font-family: "Georgia";
      font-style: normal;

    }}
   </style>
   '''

    st.markdown(styling, unsafe_allow_html=True)
    title = st.header("THE MAZE BARBERSHOP :scissors:", divider="gray")

    with st.sidebar:
        selected = option_menu("Main Menu", ["Home", "Book appointment", "Contacts"],
                               icons=['house', '', 'phone'], menu_icon="cast", default_index=0)

    if selected == "Home":
        st.subheader("This is the home page")
    elif selected == "Book appointment":
        st.subheader("You can book appointment here:")

        calendar_options = {
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
            },
            "slotMinTime": "09:00",
            "slotMaxTime": "18:00",
            "initialView": "resourceTimelineDay",
            "resourceGroupField": "barber",
            "resources": [
                {"id": "a", "title": "barber 1"},
                {"id": "b", "title": "barber 2"},
                {"id": "c", "title": "barber 3"},
            ],
        }
        calendar_events = [
            {
                "title": "Event 1",
                "start": "2023-07-31T08:30:00",
                "end": "2023-07-31T10:30:00",
                "resourceId": "a",
            },
            {
                "title": "Event 2",
                "start": "2023-07-31T07:30:00",
                "end": "2023-07-31T10:30:00",
                "resourceId": "b",
            },
            {
                "title": "Event 3",
                "start": "2023-07-31T10:40:00",
                "end": "2023-07-31T12:30:00",
                "resourceId": "c",
            }
        ]
        custom_css = """
           .fc-event-past {
               opacity: 0.8;
           }
           .fc-event-time {
               font-style: italic;
           }
           .fc-event-title {
               font-weight: 700;
           }
           .fc-toolbar-title {
               font-size: 2rem;
           }
        """

       # calendar = calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)
        #st.write(calendar)

    elif selected == "Contacts":
        st.subheader("Here are our contacts")

        appointments = {}
        st.title('Appointment Calendar')

        selected_date = st.date_input('Select a date', datetime.today())

        # Display existing appointments for the selected date, if any
        if selected_date in appointments:
            st.write(f"Appointments for {selected_date.date()}:")
            for appointment in appointments[selected_date]:
                st.write(f"- {appointment}")
        else:
            st.write("No appointments for the selected date.")

        new_appointment = st.text_input("Enter new appointment:")

        if st.button("Add Appointment"):
            if new_appointment:
                # Check if appointments already exist for the selected date
                if selected_date in appointments:
                    appointments[selected_date].append(new_appointment)
                else:
                    appointments[selected_date] = [new_appointment]
                st.success("Appointment added successfully!")
            else:
                st.warning("Please enter an appointment.")

        appointments


def login_form():
    st.session_state.reg_form = False
    st.session_state.login_form = True
    with st.form(key="login", clear_on_submit=True):
        st.subheader(":green[LogIn]")
        username = st.text_input(label="Username", placeholder="Enter your username", value="")
        password = st.text_input(label="Password", value="", placeholder="Enter your password", type="password")
        st.info("If you don't have an account, yet, you can double click on 'Create new account' button to sign up!")
        log_button = st.form_submit_button("LogIn", on_click=print_vars())

        if log_button:
            st.session_state.login_form = True
            st.session_state['clicked'] = True
            if username in usernames and password in passwords:
                # st.session_state["login"] = True
                st.success("Successfully logged into your account !!!")
                st.balloons()
                main_page()
                st.session_state.reg_form = False
                st.session_state.login_form = False
            elif len(username) < 1 or len(password) < 1:
                st.warning("Please fill in both username and password fields to proceed !")
            else:
                # st.session_state["login"] = False
                st.error("incorrect creds")
                st.rerun()


def register_form():
    st.session_state.login_form = False
    st.session_state.reg_form = True

    with st.form(key="register", clear_on_submit=True):
        st.subheader(":green[Registration]")
        fir_name = st.text_input(label="Name", placeholder="Enter your name", value="")
        sur_name = st.text_input(label="Surname", placeholder="Enter your surname", value="")
        mail = st.text_input(label="Email", placeholder="Enter a valid email address", value="")
        phone = st.text_input(label="Phone", placeholder="Enter a valid phone number", value="")
        username = st.text_input(label="Username", placeholder="Enter a username", value="")
        password = st.text_input(label="Password", value="", placeholder="Enter a password", type="password")
        password_confirm = st.text_input(label="Confirm Password", value="", placeholder="Confirm the password",
                                         type="password")
        reg_button = st.form_submit_button("SignUp")
        # if not username in usernames:
        # user_pattern = "^[a-zA-Z0-9]*$"
        # if re.match(username, user_pattern):
        #  if not mail in mails:
        #  mail_pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        ## if re.match(mail,mail_pattern):
        now = datetime.now()
        date_joined = now.strftime('%Y-%m-%d %H:%M:%S')
        date_joined

        if reg_button:
            InsertSQL = f'''INSERT INTO REGISTRATIONS(username, password, first_name, family_name, email, telephone_number, date_of_registration)
                                  VALUES(%s, %s, %s, %s, %s, %s, %s)
              '''
            # '{username}, {password}, {fir_name}, {sur_name}, {mail}, {phone}, {date_joined}
            # %s, %s, %s, %s, %s, %s, %s
            values = (username, password, fir_name, sur_name, mail, phone, date_joined)
            cursor.execute(InsertSQL, values)
            connection.commit()
            st.success("You have successfully created your account !")
            st.balloons()
            #  else:
            #    st.error("error occurred when trying to create new account, please try again !")
            # else:
            # st.warning("This email is not correct !")
            # else:
            # st.warning("This email already exists !")
            # else:
            # st.warning("Inserted name is not correct")
        # else:
        # st.warning("this username already exists")


#with st.container():
#    st.markdown('''
#   <!DOCTYPE html>
#   <html>
#   <body>
#   <h1> THE MAZE BARBERSHOP </h1>
#   <style>
#         body {background-color: black;}
#         h1 {color: white; text-align: center; font-family: Times New Roman;}
#
#   </style>
#   </body>
#   </html>
#   ''', unsafe_allow_html=True)
#with st.container():
#    st.markdown('''
#       <!DOCTYPE html>
#       <html>
#       <body>
#       <h4> Welcome to the best barbershop around! </h4>
#       <style>
#             h4 {color: white; text-align: center; font-family: Times New Roman;}
#
#       </style>
#       </body>
#       </html>
#       ''', unsafe_allow_html=True)
#st.divider()


#with st.container():
#    col1, col2, col3, col4 = st.columns(4)
#    with col1:
#        loginButton = st.button("Log into you account") ##, on_click= click_button())
#    with col4:
#        registerButton = st.button("Create a new account") ##, on_click= click_button())



#if 'login_form' not in st.session_state:
#    st.session_state.login_form = False
#if 'reg_form' not in st.session_state:
#    st.session_state.reg_form = False
#
#if loginButton or st.session_state.login_form:
#   login_form()
#elif registerButton or st.session_state.reg_form:
#    register_form()

main_page()


