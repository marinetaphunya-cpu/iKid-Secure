import streamlit as st
import time

# ตอน Login ผ่าน
if password == "1234":
    st.session_state["authenticated"] = True # ตั้งค่าตัวนี้
    st.switch_page("pages/1_Dashboard.py") # สลับไปหน้า Dashboard


# ตั้งค่าหน้ากระดาษ
st.set_page_config(page_title="iKid Secure", page_icon="🔐")

# ใส่ CSS เพื่อตกแต่งพื้นหลังและปุ่ม
st.markdown("""
    <style>
    /* บังคับพื้นหลัง */
    .stApp { 
        background-color: #F8F9FA !important; 
    }
    
    /* บังคับสีตัวหนังสือทั้งหมดให้อ่านง่าย */
    h1, h2, h3, p, div, label { 
        color: #212529 !important; 
    }
    
    /* บังคับสีปุ่ม */
    div.stButton > button { 
        background-color: #0D6EFD !important; 
        color: #FFFFFF !important; 
        border: none !important;
        border-radius: 5px !important;
    }
    </style>
""", unsafe_allow_html=True)


# หน้า Login
def login_page():
    st.title("🔐 iKid Secure")
    st.subheader("ยินดีต้อนรับสู่ระบบติดตามพฤติกรรม")
    
    password = st.text_input("โปรดกรอกรหัสผ่านเพื่อเข้าใช้งาน", type="password")
    
    if st.button("เข้าสู่ระบบ"):
        if password == "1234":
            st.session_state["authenticated"] = True # ตั้งค่าตัวนี้
            st.switch_page("pages/1_Dashboard.py") # สลับไปหน้า Dashboard

if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("app.py") # ถ้ายังไม่ Login ให้ดีดกลับทันที

# เช็คสถานะการล็อกอิน
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.switch_page("pages/1_Dashboard.py") # สั่งให้เด้งไปหน้าตาราง
else:
    login_page()

