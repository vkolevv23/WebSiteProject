import streamlit as st
import base64
import mysql.connector
from datetime import datetime
import pandas as pd
import plotly_express as px
import re


st.set_page_config(
    page_title="Info",
    page_icon="	:barber:"
)
st.title("Статистика и информация за клиенти на салона :bar_chart:")
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


def load_data():
    query = "SELECT * FROM COMMENTS;"
    data = pd.read_sql(query, connection)
    connection.close()
    return data


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

get_role_sql = f'''
SELECT role FROM REGISTRATIONS 
WHERE username = '{st.session_state.username}'
'''
cursor.execute(get_role_sql)
get_role = cursor.fetchone()
#role = [lis[-1] for lis in get_roles]

if st.session_state.username == "":
    st.info(":information_source: ...За да видите съдържанието на тази страница, първо трябва да влезнете в профила си!")
elif get_role[0] != "admin":
    st.info(":information_source: ...Страница с ограничен достъп. Нямате право да виждате съдържанието! ")
else:
  comments_form = st.form(key="c_form", clear_on_submit=False)
  with comments_form:
    st.subheader(":green[Коментари от клиенти] :memo:")
    df_query = '''
               SELECT username, email, comment_text, date_of_registration as date_of_comment, 
                      if(is_answered = 0, 'not answered', 'answered') as answer 
               FROM COMMENTS
               ORDER BY date_of_registration ASC
             '''
    comments = pd.read_sql(df_query, connection)
    connection.commit()
    # Load data into a Pandas DataFrame
    #comments_df = st.dataframe(comments)
    editable_df = st.data_editor(data= comments, disabled=["username", "email", "date_of_comment"])
    sbmt_button = st.form_submit_button(label= "Запиши промени")
    if sbmt_button:
        try:
           for index, row in editable_df.iterrows():
             sql_update = f'''
                    UPDATE COMMENTS
                    SET is_answered = 
                    CASE WHEN '{row['answer']}' = 'answered' THEN 1
                    ELSE 0 END
                    WHERE username = '{row['username']}'
                      AND date_of_registration = '{row['date_of_comment']}'
                   '''
             cursor.execute(sql_update)
             connection.commit()
           st.success(":heavy_check_mark: Таблицата с коментари от базата данни е обновена успешно!")
        except:
           st.error(":x: Грешка!!! Таблицата с коментари от базата данни не беше обновена!")


  customers_form = st.form(key="user_form", clear_on_submit=False)
  with customers_form:
    st.subheader(":green[Регистрирани потребители] :clipboard:")
    df_query = '''
                 SELECT username, date_of_registration as 'Registration date'
                 FROM REGISTRATIONS
                 ORDER BY date_of_registration DESC
               '''
    users_board = pd.read_sql(df_query, connection)
    connection.commit()
    users_df = st.dataframe(data=users_board)
    sbmt_button = st.form_submit_button(label="Покажи повече информация")
    if sbmt_button:
        try:
             sql_top_10 = f'''
                    SELECT first_name as Name, family_name as Surname, username as Username, 
                    email as 'E-mail' , date_of_registration as 'Registration date'
                    FROM REGISTRATIONS
                    ORDER BY date_of_registration DESC
                   '''
             sql = pd.read_sql(sql_top_10, connection)
             connection.commit()
             details_df = st.dataframe(data=sql)
        except:
           st.error(":x: Грешка при опит за визуализиране на повече информация!")

  st.divider()

  st.subheader(":green[Предстоящи резервации] :clipboard:")
  sql_appointments = '''
  SELECT Username, Name, Surname, Date, CAST(Time AS CHAR) as Time, Hairstyle, Beard_Included, Payment_Method, Cost,
         CASE WHEN LEFT(Date,10) = CURRENT_DATE() THEN 'Today' 
              ELSE 'Upcoming Days' 
         END AS 'When'
  FROM V_BOOKED_APPOINTMENTS a      
  WHERE LEFT(a.Date,10) >= CURRENT_DATE()
  '''
  df_appointments = pd.read_sql(sql_appointments, connection)
  connection.commit()
  appointments_df = st.dataframe(data=df_appointments)

  st.divider()

  st.subheader(":green[История на резервациите] :clipboard:")
  sql_appointments_past = '''
           SELECT Username, Name, Surname, Date, CAST(Time AS CHAR) as Time, 
                  Hairstyle, Beard_Included, Payment_Method, Cost
           FROM V_BOOKED_APPOINTMENTS a      
           WHERE LEFT(a.Date,10) < CURRENT_DATE()
           '''
  df_past = pd.read_sql(sql_appointments_past, connection)
  connection.commit()
  past_df = st.dataframe(data=df_past)

  st.divider()
  st.subheader(":green[Диаграма за броя на резервации по дни или месеци] :bar_chart:")
  if "s_key" not in st.session_state:
      st.session_state.s_key = None

  sql_start_months = '''
  SELECT db_date 
  FROM calendar_table
  GROUP BY db_date 
  '''
  cursor.execute(sql_start_months)
  get_s_months = cursor.fetchall()
  s_months = [lis[-1] for lis in get_s_months]
  s_months_select = st.selectbox(label="Начална дата(YYYY-MM-DD):",
                                 options=s_months,
                                 placeholder="моля, направете вашия избор",
                                 index=0,
                                 key='s_key'
                                )
  selected_s_month = st.session_state.s_key

  if "e_key" not in st.session_state:
      st.session_state.e_key = None

  sql_end_months = f'''
    SELECT db_date 
    FROM calendar_table
    WHERE db_date > cast('{selected_s_month}' as date)
    GROUP BY db_date  
    '''
  cursor.execute(sql_end_months)
  get_e_months = cursor.fetchall()
  e_months = [lis[-1] for lis in get_e_months]
  e_months_select = st.selectbox(label="Крайна дата(YYYY-MM-DD):",
                                 options=e_months,
                                 placeholder="моля, направете вашия избор",
                                 index=0,
                                 key='e_key'
                                 )
  selected_e_month = st.session_state.e_key
  st.write(f"Изберете някоя от двете опции, отдолу, за да видите резултати за периода между '{selected_s_month}' и '{selected_e_month}'.")
  col1,col2,col3 = st.columns(3)
  with col1:
      chart_btn = st.button("Покажи резултати по дни")
  if chart_btn:
      sql_count_appointments = f'''
      SELECT  CAST(LEFT(date_of_appointment,10) AS DATE) as 'Ден',
              COUNT(appointment_id)  as 'Брой резервации'
      FROM APPOINTMENTS 
      WHERE CAST(LEFT(date_of_appointment,10) AS DATE) BETWEEN cast('{selected_s_month}' as date)  
                                                           AND cast('{selected_e_month}' as date) 
      GROUP BY CAST(LEFT(date_of_appointment,10) AS DATE)            
      '''
      df_count = pd.read_sql(sql_count_appointments, connection)
      connection.commit()
      bar_chart_d = px.bar(df_count,
                         x="Ден",
                         y="Брой резервации"
                        )
      bar_chart_d
  with col3:
      chart_btn2 = st.button("Покажи резултат по месеци")
  if chart_btn2:
      sql_count_appointments2 = f'''
      SELECT CONCAT(CASE WHEN month(date_of_appointment) = 1  THEN 'January'
				   WHEN month(date_of_appointment) = 2  THEN 'February'
                   WHEN month(date_of_appointment) = 3  THEN 'March'
				   WHEN month(date_of_appointment) = 4  THEN 'April'
                   WHEN month(date_of_appointment) = 5  THEN 'May'
                   WHEN month(date_of_appointment) = 6  THEN 'June'
                   WHEN month(date_of_appointment) = 7  THEN 'July'
                   WHEN month(date_of_appointment) = 8  THEN 'August'
                   WHEN month(date_of_appointment) = 9  THEN 'September'
                   WHEN month(date_of_appointment) = 10 THEN 'October'
                   WHEN month(date_of_appointment) = 11 THEN 'November'
                   WHEN month(date_of_appointment) = 12 THEN 'December' end, ' , ' , YEAR(date_of_appointment)) as 'Месец',
      COUNT(appointment_id)  as 'Брой резервации'
      FROM APPOINTMENTS  
      WHERE CAST(LEFT(date_of_appointment,10) AS DATE) BETWEEN cast('{selected_s_month}' as date)  
                                                           AND cast('{selected_e_month}' as date) 
      GROUP BY CONCAT(CASE WHEN month(date_of_appointment) = 1  THEN 'January'
				   WHEN month(date_of_appointment) = 2  THEN 'February'
                   WHEN month(date_of_appointment) = 3  THEN 'March'
				   WHEN month(date_of_appointment) = 4  THEN 'April'
                   WHEN month(date_of_appointment) = 5  THEN 'May'
                   WHEN month(date_of_appointment) = 6  THEN 'June'
                   WHEN month(date_of_appointment) = 7  THEN 'July'
                   WHEN month(date_of_appointment) = 8  THEN 'August'
                   WHEN month(date_of_appointment) = 9  THEN 'September'
                   WHEN month(date_of_appointment) = 10 THEN 'October'
                   WHEN month(date_of_appointment) = 11 THEN 'November'
                   WHEN month(date_of_appointment) = 12 THEN 'December' end, ' , ' , YEAR(date_of_appointment))            
      '''
      df_count2 = pd.read_sql(sql_count_appointments2, connection)
      connection.commit()
      bar_chart_m = px.bar(df_count2,
                           x="Месец",
                           y="Брой резервации"
                           )
      bar_chart_m