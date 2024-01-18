import streamlit as st
import base64
import mysql.connector
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval
import streamlit.components.v1 as components
import re

st.set_page_config(
    page_title="Home page",
    page_icon=":barber:"
)

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


def select_signup():
    st.session_state.form = 'signup_form'


def user_update(name):
    st.session_state.username = name


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


if 'username' not in st.session_state:
  st.session_state.username = ''
if 'form' not in st.session_state:
  st.session_state.form = ''

with open("style.css") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("THE MAZE BARBERSHOP :scissors:")
st.subheader(f"Добре дошъл,{st.session_state.username.upper()} в нашия уеб сайт")
st.divider()

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
st.markdown(styling, unsafe_allow_html=True)


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
                 st.sidebar.error(':x: Избраното потребителско име не покрива изискванията(Трябва да бъде повече от 2 и по-малко от 20 символа)')
            elif new_username in usernames:
                 st.sidebar.error(':x: Въведеното потребителско име вече съществува')
            elif validate_email(new_user_email) is False:
                 st.sidebar.error(':x: Невалиден имейл адрес')
            elif new_user_email in mails:
                 st.sidebar.error(':x: Въведеният имейл адрес вече съществува')
            elif new_user_pas != user_pas_conf:
                 st.sidebar.error(':x: Паролите не съвпадат')
            elif len(new_user_pas) < 4 and len(new_user_pas) > 20:
                 st.sidebar.error(':x: Избраната парола не покрива изискванията( Трябва да бъде повече от 4 и по-малко от 20 символа)')
            elif len(new_tel_number) != 10:
                 st.sidebar.error(':x: Такъв телефонен номер не съществува')
            else:
                user_update(new_username)
                InsertSQL = f'''INSERT INTO REGISTRATIONS(username, password, first_name, family_name, email, telephone_number, date_of_registration)
                                                  VALUES(%s, %s, %s, %s, %s, %s, %s)'''
                now = datetime.now()
                date_joined = now.strftime('%Y-%m-%d %H:%M:%S')
                values = (new_username, new_user_pas, new_name, new_surname, new_user_email, new_tel_number, date_joined)
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
            #streamlit_js_eval(js_expressions="window.location.reload(true)")
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
        streamlit_js_eval(js_expressions = "parent.window.location.reload()")
# 'Create Account' button
if st.session_state.username == "" and st.session_state.form != 'signup_form':
    signup_request = st.sidebar.button('Създай нов профил', on_click=select_signup)



file1 = open("C:\\Users\\vaset\\PycharmProjects\\BarbershopProject\\LOGO.png", "rb")
contents = file1.read()
data_url1 = base64.b64encode(contents).decode("utf-8")
file1.close()

file2 = open("C:\\Users\\vaset\\PycharmProjects\\BarbershopProject\\promo.png", "rb")
contents = file2.read()
data_url2 = base64.b64encode(contents).decode("utf-8")
file2.close()

file3 = open("C:\\Users\\vaset\\PycharmProjects\\BarbershopProject\\promo2.png", "rb")
contents = file3.read()
data_url3 = base64.b64encode(contents).decode("utf-8")
file3.close()


components.html(
   f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {{box-sizing: border-box;}}
body {{font-family: Times New Roman, sans-serif;}}
.mySlides {{display: none;}}
img {{vertical-align: middle;}}

/* Slideshow container */
.slideshow-container {{
  max-width: 600px;
  position: relative;
  margin: auto;
}}

/* Number text (1/3 etc) */
.numbertext {{
  color: #f2f2f2;
  font-size: 12px;
  padding: 8px 12px;
  position: absolute;
  top: 0;
}}

/* The dots/bullets/indicators */
.dot {{
  height: 15px;
  width: 15px;
  margin: 0 2px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  transition: background-color 0.6s ease;
}}

.active {{
  background-color: #717171;
}}

/* Fading animation */
.fade {{
  animation-name: fade;
  animation-duration: 2s;
}}

@keyframes fade {{
  from {{opacity: 0.2}}
  to {{opacity: 1}}
}}

/* On smaller screens, decrease text size */
@media only screen and (max-width: 300px) {{
  .text {{font-size: 11px}}
}}
</style>
</head>
<body>

<h2>Automatic Slideshow</h2>
<p>Change image every 4 seconds:</p>

<div class="slideshow-container">

<div class="mySlides fade">
  <div class="numbertext">1 / 3</div>
  <img src="data:image/gif;base64,{data_url1}" style="width:100%" >
</div>

<div class="mySlides fade">
  <div class="numbertext">2 / 3</div>
  <img src="data:image/gif;base64,{data_url2}" style="width:100%">
</div>

<div class="mySlides fade">
  <div class="numbertext">3 / 3</div>
  <img src="data:image/gif;base64,{data_url3}" style="width:100%">
</div>

</div>
<br>

<div style="text-align:center">
  <span class="dot"></span> 
  <span class="dot"></span> 
  <span class="dot"></span> 
</div>

<script>
let slideIndex = 0;
showSlides();

function showSlides() {{
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  for (i = 0; i < slides.length; i++) {{
    slides[i].style.display = "none";  
  }}
  slideIndex++;
  if (slideIndex > slides.length) {{slideIndex = 1}}  
  for (i = 0; i < dots.length; i++) {{
    dots[i].className = dots[i].className.replace(" active", "");
  }}
  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";
  setTimeout(showSlides, 4000); // Change image every 4 seconds
}}
</script>
</body>
</html> 

""",
    height=1000,
)
