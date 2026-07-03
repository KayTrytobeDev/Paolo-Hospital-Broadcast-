import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import requests
import pytz
import plotly.express as px

# ตั้งค่าหน้าเพจ
st.set_page_config(page_title="Dashboard ระบบเสียง", layout="wide", page_icon="🔊")

# ==========================================
# 1. การตั้งค่า URL (ก๊อปปี้มาใส่ให้ถูกต้อง)
# ==========================================
# ⚠️ 1. ใส่ Web App URL ที่ได้จาก Google Apps Script (ตอน Deploy)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwhENUa0dRVKuwJyX8IgoJwszlpsvxWssWXBsATe-cKUjNlsFuFgAtoRIvM39iXKEx/exec" 

# ⚠️ 2. ใส่ ลิงก์ CSV ที่ได้จากการ Publish Google Sheets เป็น CSV
PUBLIC_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSc1aDjn_PYGYPV2JZBJvns8mAoVKGAkL2Yb1nWOKQAcgYHukN7X_eKJf8KEYbEbSyJ-YmGlOpreZXv/pubhtml?gid=0&single=true"

# ==========================================
# 2. ข้อมูลตั้งต้น
# ==========================================
department_data = {
    "ชั้น G": ["แผนกรับส่งผู้ป่วยและรักษาความปลอดภัย", "แผนกต้อนรับลงทะเบียน", "แผนกประเมินสิทธิ์และพรบ.", "แผนกคลอเซ็นเตอร์", "แผนกห้องฉุกเฉิน", "แผนกศัลยกรรม", "แผนกกระดูกและข้อ", "แผนก X-Ray (MRI)", "แผนกการเงินนอก", "แผนกห้องยา", "แผนกตรวจสุขภาพ", "แผนก X-Ray (ทั่วไป)", "แผนกห้อง Lab"],
    "ชั้น 2": ["ห้อง Lab กลาง", "แผนกทันตกรรม", "แผนกOPD MED", "แผนกOPD PED/Sick", "แผนกOPD PED/Well", "แผนกสูตินรีเวช", "แผนกการเงินใน", "ห้องผ้า", "ห้องพักแพทย์"],
    "ชั้น 3": ["แผนก ICU", "แผนก OR", "แผนก LR/NSY", "แผนกห้องยาใน", "แผนก N - Health"],
    "ชั้น 4": ["แผนกไตเทียม", "แผนกโภชนาการ Sodexso", "ห้องคลังพัสดุ", "แผนกQMS", "แผนกทรัพยากรบุคคล", "แผนกกายภาพ", "สำนักบริหาร", "แผนกไอที", "ฝ่ายการพยาบาล", "การตลาด", "สำนักผู้อำนวยการ", "ประกันสุขภาพ"],
    "ชั้น 5": ["หอพักผู้ป่วยใน Ward5"],
    "ชั้น 6": ["หอพักผู้ป่วยใน Ward6", "แผนกEENT", "แผนกบริหารลูกค้าองค์กร", "แผนก UM NURSE", "แผนกเวชระเบียน", "แผนกพิมพ์ผล"],
    "ชั้น 7": ["หอพักผู้ป่วยใน Ward7"],
    "ชั้น 8": ["หอพักผู้ป่วยใน Ward8"],
    "ชั้น R": ["แผนกวิศวกรรม"]
}
months_th = ["ทั้งหมด", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

# ==========================================
# 3. ฟังก์ชันดึงข้อมูลมาทำ Dashboard
# ==========================================
@st.cache_data(ttl=10) # ดึงข้อมูลใหม่ทุก 10 วินาที
def load_data():
    try:
        df = pd.read_csv(PUBLIC_CSV_URL)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# ==========================================
# 4. เมนูด้านข้าง (Sidebar Navigation)
# ==========================================
st.sidebar.title("เมนูหลัก")
page = st.sidebar.radio("เลือกหน้าต่างการทำงาน:", ["📊 Dashboard สรุปผล", "📝 ฟอร์มรายงาน"])
st.sidebar.markdown("---")

# ==========================================
# 5. หน้าต่างการทำงาน: Dashboard
# ==========================================
if page == "📊 Dashboard สรุปผล":
    st.title("📊 Dashboard สรุปความพร้อมระบบเสียงประกาศตามสาย")
    st.markdown("---")
    
    st.subheader("🔍 ตัวกรองข้อมูล (Filters)")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        selected_month = st.selectbox("1. เลือกเดือน", months_th)
    with c2:
        if selected_month != "ทั้งหมด":
            current_year = datetime.now().year
            month_index = months_th.index(selected_month)
            last_day = calendar.monthrange(current_year, month_index)[1]
