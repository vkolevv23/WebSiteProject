import streamlit as st
import base64
import mysql.connector
from datetime import datetime
from PIL import Image
import re


st.set_page_config(
    page_title="Book appointment",
    page_icon="	:barber:"
)

st.title("Резервиране на часове")
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
st.markdown(styling, unsafe_allow_html=True)

if 'username' not in st.session_state:
  st.session_state.username = ''
if 'form' not in st.session_state:
  st.session_state.form = ''


def select_signup():
    st.session_state.form = 'signup_form'


def user_update(name):
    st.session_state.username = name


if st.session_state.username != '':
    st.sidebar.write(f"Здравейте, {st.session_state.username.upper()}")

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
                ':x: Избраното потребителско име не покрива изискванията(Трябва да бъде повече от 2 и по-малко от 20 символа')
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


hairstyles = st.container()
with hairstyles:
    col1, col2, col3 = st.columns(3)
    with col1:
        row1 = st.container()
        with row1:
          img1 = Image.open("C:/Users/vaset/PycharmProjects/BarbershopProject/buzz_cut.jpg")
          st.image(img1, use_column_width=True)
        row2 = st.container()
        with row2:
          img2 = Image.open("C:/Users/vaset/PycharmProjects/BarbershopProject/caesar_cut.png")
          st.image(img2, use_column_width=True)
        row3 = st.container()
        with row3:
          img3 = Image.open("C:/Users/vaset/PycharmProjects/BarbershopProject/low_taper_fade.png")
          st.image(img3, use_column_width=True)
        row4 = st.container()
        with row4:
          img4 = Image.open("C:/Users/vaset/PycharmProjects/BarbershopProject/mid_fade_cut.png")
          st.image(img4, use_column_width=True)
        row5 = st.container()
        with row5:
          img5 = Image.open("C:/Users/vaset/PycharmProjects/BarbershopProject/mohawk_cut.jpg")
          st.image(img5, use_column_width=True)
        row6 = st.container()
        with row6:
          img6 = Image.open("C:/Users/vaset/PycharmProjects/BarbershopProject/under_cut.jpg")
          st.image(img6, use_column_width=True)
        row7 = st.container()
        with row7:
          img7 = Image.open("C:/Users/vaset/PycharmProjects/BarbershopProject/man-bun-cut.png")
          st.image(img7, use_column_width=True)
    with col2:
        row1 = st.container()
        with row1:
           st.write(':red[Buzz cut hairstyle]')
           st.write('''
           Къс начин на подстригване, с преливка на косата отстрани и отзад. 
           Не всяка прическа "Buzz cut" е една и съща. Това зависи от предпочитанията на клиента. 
           ''')
        st.divider()
        row2 = st.container()
        with row2:
          st.write(':red[Caesar cut hairstyle]')
          st.write('''
          Класически стил, характеризиращ се с късо подстригани страни и по-дълга горна част. 
          Прическата е популярна, поради своята лесна поддръжка.
          ''')
        st.divider()
        row3 = st.container()
        with row3:
          st.write(':red[Low taper fade hairstyle]')
          st.write('''
          Стил на подстригване с преливане дължината на косата на страните и задната част, започващо от по-ниско.
          ''')
        st.divider()
        row4 = st.container()
        with row4:
          st.write(':red[Mid fade hairstyle]')
          st.write('''
          Прическа с преливане на косата, започващо от средата на главата. 
          Създава плавен преход между по-дългата горна част и по-късите страни.
          ''')
        st.divider()
        row5 = st.container()
        with row5:
          st.write(':red[Mohawk cut hairstyle]')
          st.write('''
          Модерна и съвременна прическа, при която косата от двете страни на главата е къса, 
          оставяйки ивица по- дълга коса в средата.
          ''')
        st.divider()
        row6 = st.container()
        with row6:
          st.write(':red[Under cut hairstyle]')
          st.write('''
          Характеризира се с това, че има по-къси или обръснати страни, като запазва косата отгоре по-дълга. 
          Този стил създава рязък контраст между дължината на косата отгоре и по-късите страни и задна част. 
          ''')
        st.divider()
        row7 = st.container()
        with row7:
          st.write(':red[Man bun hairstyle]')
          st.write('''
          Тази прическа включва сресването на косата назад и фиксирането й на кок или възел в горната част на главата.
          ''')

    with col3:
        st.write(':green[Цени:]')
        st.divider()
        st.write('Прическа -> 10BGN')
        st.write('Прическа + Брада -> 20BGN')
        st.markdown('#')
        st.markdown('#')
        st.write(':green[Цени:]')
        st.divider()
        st.write('Прическа -> 12BGN')
        st.write('Haircut + Брада -> 22BGN')
        st.markdown('###')
        st.markdown('##')
        st.markdown('##')
        st.write(':green[Цени:]')
        st.divider()
        st.write('Прическа -> 10BGN')
        st.write('Прическа + Брада -> 20BGN')
        st.markdown('##')
        st.write(':green[Цени:]')
        st.divider()
        st.write('Прическа -> 15BGN')
        st.write('Прическа + Брада -> 30BGN')
        st.markdown('##')
        st.markdown('##')
        st.write(':green[Цени:]')
        st.divider()
        st.write('Прическа -> 15BGN')
        st.write('Прическа + Брада -> 30BGN')
        st.markdown('##')
        st.markdown('##')
        st.write(':green[Цени:]')
        st.divider()
        st.write('Прическа -> 15BGN')
        st.write('Прическа + Брада -> 30BGN')
        st.markdown('###')
        st.markdown('###')
        st.markdown('###')
        st.markdown('##')
        st.write(':green[Цени:]')
        st.divider()
        st.write('Прическа -> 13BGN')
        st.write('Прическа + Брада -> 23BGN')
st.divider()

st.subheader(":green[Можеш да запазиш своя час от тук !]")

if "haircuts_key" not in st.session_state:
    st.session_state.haircuts_key = None


cuts_box = st.selectbox(placeholder="Направете своя избор",
                        label="Изберете вид прическа",
                        options=[" ",
                                 "Buzz cut hairstyle",
                                 "Caesar cut hairstyle",
                                 "Low taper fade hairstyle",
                                 "Mid fade hairstyle",
                                 "Mohawk cut hairstyle",
                                 "Under cut hairstyle",
                                 "Man bun hairstyle"
                                 ],
                        index=0,
                        key="haircuts_key"
                        )
selected_cut = st.session_state.haircuts_key

if "beards_key" not in st.session_state:
    st.session_state.beards_key = None

beard_box = st.selectbox(placeholder="Направете своя избор",
                         label="Имате ли нужда от оформяне и подстригване на брадата?",
                         options=[" ",
                                  "Hairstyle with beard",
                                  "Hairstyle without beard"
                                 ],
                         index=0,
                         key="beards_key"
                        )
selected_beard = st.session_state.beards_key

dates_sql = '''
            SELECT null 
            union
            SELECT DISTINCT CONCAT(db_date,' , ',day_name) AS date_of_appointment 
            FROM calendar_table 
            WHERE db_date BETWEEN CURRENT_DATE() 
                              AND DATE_ADD(CURRENT_DATE(), INTERVAL 14 DAY)
'''
cursor.execute(dates_sql)
get_dates = cursor.fetchall()
dates = [lis[-1] for lis in get_dates]

if "date_key" not in st.session_state:
    st.session_state.date_key = None

dates_box = st.selectbox(label="Изберете удобна за вас дата(YYYY-MM-DD):",
                         options=dates,
                         placeholder="Направете своя избор",
                         index = 0,
                         key='date_key'
                        )
selected_date = st.session_state.date_key

times_sql = f'''
            SELECT time_of_appointment
            FROM barbershop_db.calendar_table
            WHERE CONCAT(db_date,' , ',day_name) = '{selected_date}'
              AND b_appointment IS NULL
        '''
cursor.execute(times_sql)
get_times = cursor.fetchall()
times = [lis[-1] for lis in get_times]

if "time_key" not in st.session_state:
    st.session_state.time_key = None

times_box = st.selectbox(label="Изберете час за резервацията:",
                         options=times,
                         placeholder="Направете своя избор",
                         index=0,
                         key="time_key"
                         )
selected_time = st.session_state.time_key

if "card_pay" not in st.session_state:
    st.session_state.card_pay = False

on = st.toggle(label='Плати с карта :credit_card:',key="card_pay")
if on:
  st.divider()
  if "card_info" not in st.session_state:
      st.session_state.card_info = False
  #st.session_state.card_pay = True
  st.subheader(":green[Информация за кредитна карта]")
  card_number = st.text_input(label="Номер на карта")
  col1, col2 = st.columns(2)
  with col1:
    exp_date = st.date_input(label="Дата на валидност", format='DD/MM/YYYY')
  with col2:
    cvv_code = st.text_input(label= "CVV код")
  if len(card_number) != 16:
      st.error(":x: Грешен номер на карта( Дължината на номера трябва да е 16 цифри)")
  elif exp_date.strftime("%m/%y") < datetime.now().strftime("%m/%y"):
      st.error(":x: Избраната карта не е валидна!")
  elif len(cvv_code) != 3:
      st.error(":x: Грешен CVV код( Трябва да е точно 3 цифри !")
  else:
      st.success(":heavy_check_mark: Информацията, предоставена за кредитаната карта е вярна !")
      st.session_state.card_info = True

if "prc_btn" not in st.session_state:
    st.session_state.prc_btn = False


def callback():
  st.session_state.prc_btn = True


proceed_btn = st.button(label="Продължи", on_click= callback)
if proceed_btn or st.session_state.prc_btn:
    book_form = st.form(key="b_form", clear_on_submit=True)
    with book_form:
      st.write(f"Вид прическа: {selected_cut} :man-getting-haircut:")
      st.write(f"Дата: {selected_date} :calendar:")
      st.write(f"Час: {selected_time} :clock5:")
      if selected_beard == 'Hairstyle with beard':
          st.write("Прическа с оформяне на брадата :bearded_person:")
      elif selected_beard == 'Hairstyle without beard':
          st.write("Прическа без оформяне на брадата :bearded_person:")
      else:
          st.write("Все още не сте избрали опция за брадата")
      pay_method = ''
      if st.session_state.card_pay == True and st.session_state.card_info == True:
         pay_method = "Payment with card"
         st.write(f"Плащане с карта :credit_card:")
      elif st.session_state.card_pay == False or st.session_state.card_info == False:
         pay_method = "Payment in cash"
         st.write(f'Плащане в брой :money_with_wings:')
      st.divider()
      cut_cost = ''
      st.write("Обща цена на процедурата:")
      if selected_cut == 'Buzz cut hairstyle':
          if selected_beard == "Hairstyle with beard":
              cut_cost = "20 BGN"
              st.write(cut_cost)
          else:
              cut_cost = "10 BGN"
              st.write(cut_cost)
      elif selected_cut == 'Caesar cut hairstyle':
          if selected_beard == "Hairstyle with beard":
              cut_cost = "22 BGN"
              st.write(cut_cost)
          else:
              cut_cost = "12 BGN"
              st.write(cut_cost)
      elif selected_cut == 'Low taper fade hairstyle':
          if selected_beard == "Hairstyle with beard":
              cut_cost = "20 BGN"
              st.write(cut_cost)
          else:
              cut_cost = "10 BGN"
              st.write(cut_cost)
      elif selected_cut == 'Mid fade hairstyle':
          if selected_beard == "Hairstyle with beard":
              cut_cost = "30 BGN"
              st.write(cut_cost)
          else:
              cut_cost = "15 BGN"
              st.write(cut_cost)
      elif selected_cut == 'Mohawk cut hairstyle':
          if selected_beard == "Hairstyle with beard":
              cut_cost = "30 BGN"
              st.write(cut_cost)
          else:
              cut_cost = "15 BGN"
              st.write(cut_cost)
      elif selected_cut == 'Under cut hairstyle':
          if selected_beard == "Hairstyle with beard":
              cut_cost = "30 BGN"
              st.write(cut_cost)
          else:
              cut_cost = "15 BGN"
              st.write(cut_cost)
      elif selected_cut == 'Man bun hairstyle':
          if selected_beard == "Hairstyle with beard":
              cut_cost = "23 BGN"
              st.write(cut_cost)
          else:
              cut_cost = "13 BGN"
              st.write(cut_cost)
      book_button = st.form_submit_button(label='Запази час')
      if book_button:
            if st.session_state.username != "":
              if selected_date is not None:
                if selected_time is not None:
                  if selected_cut is not None:
                    if selected_beard is not None:
                      st.write(pay_method)
                      InsertSQL = f'''
                      INSERT INTO APPOINTMENTS(username_of_customer, date_of_appointment, time_of_appointment,
                                               type_haircut, with_beard_trim, payment_method, haircut_cost
                                              )
                      VALUES(%s, %s, %s, %s, %s, %s, %s)
                      '''
                      values = (st.session_state.username, selected_date , selected_time, selected_cut, selected_beard, pay_method, cut_cost)
                      insert = cursor.execute(InsertSQL, values)
                      updateSQL = f'''
                      UPDATE CALENDAR_TABLE
                      SET b_appointment = '{st.session_state.username}'
                      WHERE CONCAT(db_date,' , ',day_name) = '{selected_date}'
                        AND cast(time_of_appointment as char) = '{selected_time}'
                      '''
                      cursor.execute(updateSQL)
                      connection.commit()
                      st.success(":heavy_check_mark: Резервацията е успешно записана! Благодарим ви за доверието!")
                    else:
                      st.error(":x: Моля, направете своят избор от опцията за оформяне на брада!")
                  else:
                    st.error(":x: Моля, изберете вида на желаната от вас прическа!")
                else:
                  st.error(":x: Моля, изберете час за вашата резервация")
              else:
                st.error(":x: Моля, изберете дата за вашата резервация !")
            else:
                st.error(":x: Моля, влезте в профила си, за да резервирате час!")