import streamlit as st
import base64
import mysql.connector
from datetime import datetime
import pandas as pd
import re


st.set_page_config(
    page_title="Contacts",
    page_icon="	:barber:"
)
st.title("Контакти :phone:")
st.divider()
with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


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
        st.error(f":x: Грешка при свързването с базата данни: {e}")
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


img_path = "C:\\Users\\vaset\\PycharmProjects\\BarbershopProject\\sidebar_photo4.png"
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

    [data-testid="stSidebarContent"]
    {{
     background: url(data:image/{bg};base64,{base64.b64encode(open(img_path, "rb").read()).decode()});
     background-position: left ;
     background-size: cover;
     text-align: left;
    }}

    [data-testid="StyledLinkIconContainer"]
    {{
      color: white;
      font-family: "Georgia";
      font-style: normal;

    }}
   </style>
   '''


def validate_email(email):
    """
    Check Email Validity
    :param email:
    :return True if email is valid else False:
    """
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$" #tesQQ12@gmail.com

    if re.match(pattern, email):
        return True
    return False


st.markdown(styling, unsafe_allow_html=True)

if 'username' not in st.session_state:
  st.session_state.username = ''
if 'form' not in st.session_state:
  st.session_state.form = ''
if 'email' not in st.session_state:
    st.session_state.email = ''
def select_signup():
    st.session_state.form = 'signup_form'


def user_update(name):
    st.session_state.username = name


def get_email():
    sql = f'''
                    SELECT email FROM REGISTRATIONS 
                    WHERE username = '{st.session_state.username}'
                    '''
    cursor.execute(sql)
    get_email = cursor.fetchone()
    return get_email[0]


if st.session_state.username != '':
    st.sidebar.write(f"Здравейте,  {st.session_state.username.upper()}")

# Initialize Sing In or Sign Up forms
if st.session_state.form == 'signup_form' and st.session_state.username == '':
    st.sidebar.subheader(":green[Регистрация]")
    signup_form = st.sidebar.form(key='signup_form', clear_on_submit=False)
    new_name = signup_form.text_input(label='Име*')
    new_surname = signup_form.text_input(label='Фамилия*')
    new_username = signup_form.text_input(label='Потребителско име*')
    new_user_email = signup_form.text_input(label='Имейл адрес*')
    new_user_pas = signup_form.text_input(label='Парола*', type='password')
    user_pas_conf = signup_form.text_input(label='Потвърди парола*', type='password')
    new_tel_number = signup_form.text_input(label='Валиден телефонен номер*')
    note = signup_form.markdown('**Задължителни полета*')
    signup = signup_form.form_submit_button(label='Регистрация')

    if signup:
        if '' in [new_username, new_user_email, new_user_pas, new_tel_number, new_name, new_surname, user_pas_conf]:
            st.sidebar.error(':x: Някои полета все още не са попълнени')
        else:
            if len(new_username) < 2 and len(new_username) > 21:
                st.sidebar.error(
                    ':x: Избраното потребителско име не покрива изискванията(Трябва да бъде повече от 2 и по-малко от 20 символа)')
            elif new_username in usernames:
                st.sidebar.error(':x: Въведеното потребителско име вече съществува')
            elif validate_email(new_user_email) is False:
                st.sidebar.error(':x: Невалиден имейл адрес')
            elif new_user_email in mails:
                st.sidebar.error(':x: Въведеният имейл адрес вече съществува')
            elif new_user_pas != user_pas_conf:
                st.sidebar.error(':x: Паролите не съвпадат')
            elif len(new_user_pas) < 4 and len(new_user_pas) > 20:
                st.sidebar.error(
                    ':x: Избраната парола не покрива изискванията( Трябва да бъде повече от 4 и по-малко от 20 символа)')
            elif len(new_tel_number) != 10:
                st.sidebar.error(':x: Такъв телефонен номер не съществува')
            else:
                user_update(new_username)
                InsertSQL = f'''INSERT INTO REGISTRATIONS(username, password, first_name, family_name, email, telephone_number, date_of_registration)
                                                  VALUES(%s, %s, %s, %s, %s, %s, %s)'''
                now = datetime.now()
                date_joined = now.strftime('%Y-%m-%d %H:%M:%S')
                values = (
                new_username, new_user_pas, new_name, new_surname, new_user_email, new_tel_number, date_joined)
                insert = cursor.execute(InsertSQL, values)
                connection.commit()
                st.sidebar.success(':heavy_check_mark: Успешна регистрация!')
                st.sidebar.success(f" :heavy_check_mark: Добре дошли, {new_username.upper()}")
                del new_user_pas, user_pas_conf

elif st.session_state.username == '':
    st.sidebar.subheader(":green[Вход]")
    login_form = st.sidebar.form(key='signin_form', clear_on_submit=True)
    username = login_form.text_input(label='Въведете потребителско име')
    user_pas = login_form.text_input(label='Въведете парола', type='password')

    if username in usernames and user_pas in passwords:
        login = login_form.form_submit_button(label='Вход', on_click=user_update(username))
        if login:
            st.sidebar.success(f":heavy_check_mark: Здравейте отново, {username.upper()}")
            del user_pas
    else:
        login = login_form.form_submit_button(label='Вход')
        if login:
            st.sidebar.error(":x: Въдедените потребителско име и парола са грешни! Моля опитайте отново, или създайте нов акаунт.")
else:
    logout = st.sidebar.button(label='Изход')
    if logout:
        user_update('')
        st.session_state.form = ''

# 'Create Account' button
if st.session_state.username == "" and st.session_state.form != 'signup_form':
    signup_request = st.sidebar.button('Създай нов профил', on_click=select_signup)


st.write("Последвайте ни в социалните мрежи и научите първи за новини и промоции!")
st.write('🎥 YouTube Канал - https://www.youtube.com/@MazeBarber')
st.write('🌐 Facebook Страница - https://www.facebook.com/MazeBarber')
st.write('📧 Свържете се с нас чрез електонна поща - MazeBarbershop_support@gmail.com')
st.divider()
st.write('Локация на фризьорския салон :round_pushpin::world_map:')
data = pd.DataFrame({
    'latitude': [42.016740],
    'longitude': [23.086580]
})
st.map(data)
st.link_button(label='Виж местоположението в Google Maps', url = "https://maps.app.goo.gl/V95dnisCPXSXUK4C8")
st.divider()

comment_form = st.form(key='Comments_section', clear_on_submit=True)
with comment_form:
  txt_area = st.text_area(max_chars=500,
                          value="",
                          label="Изпрати ни своя коментар или мнение за фризьорския салон :speaking_head_in_silhouette:",
                          height=50
                          )
  apply_form = st.form_submit_button(label = "Изпрати")
  if apply_form:
    if st.session_state.username != "":
        InsertSQL = f'''
        INSERT INTO COMMENTS(username, email, comment_text, date_of_registration, is_answered)
        VALUES(%s, %s, %s, %s, %s)
        '''
        now = datetime.now()
        date_joined = now.strftime('%Y-%m-%d %H:%M:%S')
        values = (st.session_state.username, get_email(), txt_area, date_joined, '0')
        insert = cursor.execute(InsertSQL, values)
        connection.commit()
        st.success(":heavy_check_mark: Коментарът Ви беше успешно изпратен! Благодарим Ви!")

    else:
        st.error(":x: Моля, влезте в акаунта си, за да изпратите коментар!")