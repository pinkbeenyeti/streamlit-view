import pymysql as sql
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import streamlit as st
from streamlit_option_menu import option_menu

from xgboost import XGBClassifier # model
from sklearn.model_selection import train_test_split # train/test
import pandas as pd


conn = sql.connect(host = '127.0.0.1', user = 'root', password = '4056', db = 'diabates', charset='utf8')
cur = conn.cursor()

def movePage(page): 
    st.session_state.page = page

def login():  
    who = ["default", "관리자", "사용자"] 
    selected = st.selectbox("당신은 누구인가요?", who)
    
    if selected == "관리자":
        adminid = st.text_input('관리자 아이디')
        adminpassd = st.text_input('패스워드')
        
        sql = 'SELECT admin_id, admin_password FROM admin'
        cur.execute(sql)
        res = cur.fetchall()
        
        if (st.button("confirm")):
            for data in res:
                if data[0] == adminid:
                    if data[1] == adminpassd:
                        movePage(1)
                        break
                    else:
                        st.warning("잘못된 패스워드 입니다.")
                        break
                else:
                    st.warning("잘못된 아이디 입니다.")
                    break
                    
    if selected == "사용자":
        if st.button("confirm"):
            movePage(2)
            
def admin():
    
    what = ["default", "insert", "delete", "view"] 
    selected = st.selectbox("실행할 작업을 선택하세요", what)
    
    if selected == "insert":
        insert()
        if(st.button("home")):
            movePage(0)
    
    elif selected == "delete":
        delete()
        
    elif selected == "view":
        view()

def insert():
    sql = 'SELECT max(Patient_Id) from body_state'
    cur.execute(sql)
    res = cur.fetchall()
    
    patient_id = res[0][0] + 1
    preg = st.number_input('pregnancies',0)
    blood = st.number_input('bloodpressure',0)
    ins = st.number_input('insulin',0)
    gls = st.number_input('glucose',0)
    age = st.number_input('age',0)
    bmi = st.number_input('bmi')
    skin = st.number_input('skinthickness',0)
    dia = st.number_input('is_diabates', 0, 1)
    
    if st.button("confirm"):
        body = "INSERT INTO body_state ({0}, {1} , {2})".format(patient_id, preg, blood)
        hormone = "INSERT INTO hormone ({0}, {1}, {2})".format(patient_id, ins, gls)
        physical = "INSERT INTO physical ({0}, {1}, {2}, {3})".format(patient_id, age, bmi, skin)
        diabates = "INSERT INTO is_diabate ({0}, {1})".format(patient_id, dia)
        
        cur.execute(body)
        cur.execute(hormone)
        cur.execute(physical)
        cur.execute(diabates)

def delete():
    table = st.sidebar.selectbox("모든 데이터를 보실건가요?", ["default", "테이블"])
    if table == "테이블":
        df = make_pd()
        df

    delete = st.number_input("삭제할 Patient_Id를 입력하세요")
    sql = 'DELETE FROM hormone WHERE Patient_Id = {0}'.format(delete)
    sql1 = 'DELETE FROM body_state WHERE Patient_Id = {0}'.format(delete)
    sql2 = 'DELETE FROM physical WHERE Patient_Id = {0}'.format(delete)
    sql3 = 'DELETE FROM is_diabate WHERE Patient_Id = {0}'.format(delete)
    
    cur.execute(sql)
    cur.execute(sql1)
    cur.execute(sql2)
    cur.execute(sql3)

def view():
    df = make_pd()
    df
    
def diabates_features():
    select = st.sidebar.selectbox("그래프를 선택하세요", ["default", "히스토그램"])
    
    if select == "히스토그램":
        feature = st.sidebar.selectbox("특징을 선택하세요.", ["default","age", "bmi", "bloodpressure", "skinthickness", "insulin", "glucose","pregnancies"])
        
        if feature == "age":
            st.write("파란색 막대기는 당뇨병 환자를, 주황색은 일반인을 나타냅니다.")
            st.write("각 구간별 당뇨병 환자의 비율을 볼 수 있어요.")
            
            sql = 'SELECT physical.Age, is_diabate.Outcome FROM physical INNER JOIN is_diabate ON physical.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 1'
            sql2 ='SELECT physical.Age, is_diabate.Outcome FROM physical INNER JOIN is_diabate ON physical.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 0'
            
            cur.execute(sql)
            res = cur.fetchall()
            
            cur.execute(sql2) 
            res2 = cur.fetchall()
    
            list1 = []
            list2 = []
    
            for data in list(res):
                list1.append(data[0])
                
            for data in list(res2):
                list2.append(data[0])    

            fig = plt.figure()
            plt.hist((list1, list2), bins = 12, rwidth = 0.8, label = ["Patient", "public"])
            plt.legend()
            st.pyplot(fig)
            
        if feature == "bmi":
            st.write("파란색 막대기는 당뇨병 환자를, 주황색은 일반인을 나타냅니다.")
            st.write("각 구간별 당뇨병 환자의 비율을 볼 수 있어요.")
            
            sql = 'SELECT physical.BMI, is_diabate.Outcome FROM physical INNER JOIN is_diabate ON physical.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 1'
            sql2 = 'SELECT physical.BMI, is_diabate.Outcome FROM physical INNER JOIN is_diabate ON physical.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 0'
            
            cur.execute(sql)
            res = cur.fetchall()
            
            cur.execute(sql2) 
            res2 = cur.fetchall()
    
            list1 = []
            list2 = []
    
            for data in list(res):
                list1.append(data[0])
                
            for data in list(res2):
                list2.append(data[0])     

            ax=plt.axes()
            ax.xaxis.set_major_locator(ticker.MultipleLocator(3))
            
            fig = plt.figure()
            plt.hist((list1, list2), bins = 10, rwidth = 0.8, label = ["Patient", "public"])
            plt.legend()
            st.pyplot(fig)
            
            st.write("bmi : 자신의 몸무게를 키의 제곱으로 나누는 것으로 비만도를 나타냅니다.")
            
        if feature == "skinthickness":
            st.write("파란색 막대기는 당뇨병 환자를, 주황색은 일반인을 나타냅니다.")
            st.write("각 구간별 당뇨병 환자의 비율을 볼 수 있어요.")
            
            sql = 'SELECT physical.SkinThisckness, is_diabate.Outcome FROM physical INNER JOIN is_diabate ON physical.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 1'
            sql2 = 'SELECT physical.SkinThisckness, is_diabate.Outcome FROM physical INNER JOIN is_diabate ON physical.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 0'
            
            cur.execute(sql)
            res = cur.fetchall()
            
            cur.execute(sql2)
            res2 = cur.fetchall()
    
            list1 = []
            list2 = []
    
            for data in list(res):
                list1.append(data[0])
                
            for data in list(res2):
                list2.append(data[0])    

            fig = plt.figure()
            plt.hist((list1, list2), bins = 15, rwidth = 0.8, label = ["Patient", "public"])
            plt.legend()
            st.pyplot(fig)
            
            st.write("skinthickness : 피부의 두께를 말한답니다.")
            
        if feature == "bloodpressure":
            st.write("파란색 막대기는 당뇨병 환자를, 주황색은 일반인을 나타냅니다.")
            st.write("각 구간별 당뇨병 환자의 비율을 볼 수 있어요.")
            
            sql = 'SELECT body_state.BloodPressure, is_diabate.Outcome FROM body_state INNER JOIN is_diabate ON body_state.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 1'
            sql2 = 'SELECT body_state.BloodPressure, is_diabate.Outcome FROM body_state INNER JOIN is_diabate ON body_state.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 0'
            
            cur.execute(sql)
            res = cur.fetchall()
            
            cur.execute(sql2)
            res2 = cur.fetchall()
    
            list1 = []
            list2 = []
    
            for data in list(res):
                list1.append(data[0])
                
            for data in list(res2):
                list2.append(data[0])    

            fig = plt.figure()
            plt.hist((list1, list2), bins = 15, rwidth = 0.8, label = ["Patient", "public"])
            plt.legend()
            st.pyplot(fig)
            
            st.write("bloodpressure : 혈압을 나타냅니다.")
            
        if feature == "pregnancies":
            st.write("파란색 막대기는 당뇨병 환자를, 주황색은 일반인을 나타냅니다.")
            st.write("각 구간별 당뇨병 환자의 비율을 볼 수 있어요.")
            
            sql = 'SELECT body_state.Pregnancies, is_diabate.Outcome FROM body_state INNER JOIN is_diabate ON body_state.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 1'
            sql2 = 'SELECT body_state.Pregnancies, is_diabate.Outcome FROM body_state INNER JOIN is_diabate ON body_state.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 0'
            
            cur.execute(sql)
            res = cur.fetchall()
            
            cur.execute(sql2)
            res2 = cur.fetchall()
    
            list1 = []
            list2 = []
    
            for data in list(res):
                list1.append(data[0])
                
            for data in list(res2):
                list2.append(data[0])    

            fig = plt.figure()
            plt.hist((list1, list2), bins = 15, rwidth = 0.8, label = ["Patient", "public"])
            plt.legend()
            st.pyplot(fig)
            
            st.write("pregnancies : 임신의 횟수를 나타냅니다.")
        
        if feature == "insulin":
            st.write("파란색 막대기는 당뇨병 환자를, 주황색은 일반인을 나타냅니다.")
            st.write("각 구간별 당뇨병 환자의 비율을 볼 수 있어요.")
            
            sql = 'SELECT hormone.Insulin, is_diabate.Outcome FROM hormone INNER JOIN is_diabate ON hormone.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 1'
            sql2 = 'SELECT hormone.Insulin, is_diabate.Outcome FROM hormone INNER JOIN is_diabate ON hormone.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 0'
            
            cur.execute(sql)
            res = cur.fetchall()
            
            cur.execute(sql2)
            res2 = cur.fetchall()
    
            list1 = []
            list2 = []
    
            for data in list(res):
                list1.append(data[0])
                
            for data in list(res2):
                list2.append(data[0])    

            fig = plt.figure()
            plt.hist((list1, list2), bins = 15, rwidth = 0.8, label = ["Patient", "public"])
            plt.legend()
            st.pyplot(fig)
            
            st.write("인슐린 : 호르몬의 한 종류로 체내의 혈당을 낮추는 역할을 합니다.")
        
        if feature == "glucose":
            st.write("파란색 막대기는 당뇨병 환자를, 주황색은 일반인을 나타냅니다.")
            st.write("각 구간별 당뇨병 환자의 비율을 볼 수 있어요.")
            
            sql = 'SELECT hormone.Glucose, is_diabate.Outcome FROM hormone INNER JOIN is_diabate ON hormone.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 1'
            sql2 = 'SELECT hormone.Glucose, is_diabate.Outcome FROM hormone INNER JOIN is_diabate ON hormone.Patient_Id = is_diabate.Patient_Id AND is_diabate.Outcome = 0'
            
            cur.execute(sql)
            res = cur.fetchall()
            
            cur.execute(sql2)
            res2 = cur.fetchall()
    
            list1 = []
            list2 = []
    
            for data in list(res):
                list1.append(data[0])
                
            for data in list(res2):
                list2.append(data[0])    

            fig = plt.figure()
            plt.hist((list1, list2), bins = 15, rwidth = 0.8, label = ["Patient", "public"])
            plt.legend()
            st.pyplot(fig)
            
            st.write("혈당 : 혈액 내 포도당의 양을 말하며 당뇨병의 검사를 위해 많이 사용합니다.")

def make_pd():
    sql = 'SELECT body_state.Pregnancies, hormone.Glucose FROM body_state INNER JOIN hormone ON body_state.Patient_Id = hormone.Patient_Id'
    sql2 = 'SELECT body_state.BloodPressure, physical.SkinThisckness FROM body_state INNER JOIN physical ON body_state.Patient_Id = physical.Patient_Id'
    sql3 = 'SELECT hormone.Insulin FROM hormone '
    sql4 = 'SELECT physical.BMI FROM physical'
    sql5 = 'SELECT physical.Age, is_diabate.Outcome FROM physical INNER JOIN is_diabate ON physical.Patient_Id = is_diabate.Patient_Id'
    sql6 = 'SELECT physical.Patient_Id FROM physical'

    cur.execute(sql)
    res = cur.fetchall()

    cur.execute(sql2)
    res2 = cur.fetchall()

    cur.execute(sql3)
    res3 = cur.fetchall()

    cur.execute(sql4)
    res4 = cur.fetchall()
    
    cur.execute(sql5)
    res5 = cur.fetchall()
    
    cur.execute(sql6)
    res6 = cur.fetchall()

    df = pd.DataFrame(list(res), columns=['Pregnancies', 'Glucose'])
    df2 = pd.DataFrame(list(res2), columns=['BloodPressure', 'SkinThickness'])
    df = df.join(df2)

    df3 = pd.DataFrame(list(res3), columns=['Insulin'])
    df4 = pd.DataFrame(list(res4), columns=['BMI'])
    df3 = df3.join(df4)
    
    df4 = pd.DataFrame(list(res5), columns=['Age','Outcome'])
    df5 = pd.DataFrame(list(res6), columns=['Patient_Id'])
    
    df = df.join(df3)
    df = df.join(df4)
    df = df.join(df5)
    df = df.astype({'BMI':'float'})
    
    return df
            
def predict():
    choice = st.sidebar.selectbox("예측기를 선택하세요!", ["best 예측기", "간이 예측기"])
    
    st.sidebar.write("자신의 bmi를 모르겠나요?")
    height = st.sidebar.number_input("키를 입력하세요(단위는 미터입니다.)",0.1)
    wei = st.sidebar.number_input("몸무게를 입력하세요(단위는 kg입니다.)",0.1)
    
    st.sidebar.write(wei/(height * height))
    
    if choice == "best 예측기":
        diabates = make_pd()
        cols = list(diabates.columns)

        col_x = cols[:7]
        col_y = cols[-2]

        diabates_train, diabates_test = train_test_split(diabates, test_size=0.2, random_state=123)

        model = XGBClassifier()
        model.fit(X=diabates_train[col_x], y=diabates_train[col_y])
        model

        preg = st.number_input('pregnancies', 0)
        blood = st.number_input('bloodpressure',0)
        ins = st.number_input('insulin',0)
        gls = st.number_input('glucose',0)
        age = st.number_input('age',0)
        bmi = st.number_input('bmi',0.0)
        skin = st.number_input('skinthickness',0)
        
        list1 = []
        
        list1.append(preg)
        list1.append(gls)
        list1.append(blood)
        list1.append(skin)
        list1.append(ins)
        list1.append(bmi)
        list1.append(age)
        
        df = pd.DataFrame([list1], columns=col_x)
        test = model.predict(df)
        
        if(st.button("confirm")):
            if(test[0] == 0):
                st.success('당신이 당뇨병일 확률은 낮습니다!')
            if(test[0] == 1):
                st.warning('당신이 당뇨병일 확률은 높습니다! 건강관리에 신경 써 주세요')
        
    if choice == "간이 예측기":
        diabates = make_pd()
        cols = list(diabates.columns)

        col_x = []
        col_x.append(cols[2])
        col_x.append(cols[5])
        col_x.append(cols[6])
        col_y = cols[-2]

        diabates_train, diabates_test = train_test_split(diabates, test_size=0.2, random_state=123)

        model = XGBClassifier()
        model.fit(X=diabates_train[col_x], y=diabates_train[col_y])
        model

        blood = st.number_input('bloodpressure',0)
        age = st.number_input('age',0)
        bmi = st.number_input('bmi',0.0)
        
        list1 = []
        
        list1.append(blood)
        list1.append(bmi)
        list1.append(age)
        
        df = pd.DataFrame([list1], columns=col_x)
        test = model.predict(df)
        
        if(st.button("confirm")):
            if(test[0] == 0):
                st.success('당신이 당뇨병일 확률은 낮습니다!')
            if(test[0] == 1):
                st.warning('당신이 당뇨병일 확률은 높습니다! 건강관리에 신경 써 주세요')
    
    

if 'page' not in st.session_state: 
    st.session_state.page = 0

ph = st.empty()    

if st.session_state.page == 0:
    with ph.container():    
        login()
        
        
if st.session_state.page == 1:
    with ph.container():
        admin()
        
if st.session_state.page == 2:
    with ph.container():
        with st.sidebar:
            choice = option_menu("Menu", ["그래프", "예측"],
                         icons=['kanban', 'bi bi-robot'],
                         menu_icon="app-indicator", default_index=0,
                         styles={"container": {"padding": "4!important", "background-color": "#fafafa"},
                                 "icon": {"color": "black", "font-size": "25px"},
                                 "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#fafafa"},
                                 "nav-link-selected": {"background-color": "#08c7b4"},
                                 }
                                 )
        if choice == "그래프":
            diabates_features()
            
        if choice == "예측":
            predict()
            
