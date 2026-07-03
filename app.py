import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pytz

st.set_page_config(page_title="Dashboard ระบบเสียง", layout="wide", page_icon="🔊")

st.title("🔊 Dashboard ตรวจสอบความพร้อมระบบเสียงประกาศตามสาย")
st.markdown("---")

# เชื่อมต่อ Google Sheets
@st.cache_resource
def init_connection():
    creds_dict = st.secrets["gcp_service_account"]
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=5)
def load_data():
    client = init_connection()
    # URL ของ Google Sheet ของคุณ
    sheet_url = "https://docs.google.com/spreadsheets/d/1FEuRJgW1et1EWeqFTlKJZa22nYfwcUWf3KsbTZdj1i0/edit"
    sheet = client.open_by_url(sheet_url).worksheet("Sheet1")
    data = sheet.get_all_records()
    return sheet, pd.DataFrame(data)

try:
    sheet, df = load_data()
    
    # ==========================================
    # ส่วนที่ 1: Dashboard ภาพรวมความพร้อม
    # ==========================================
    st.header("📊 ส่วนที่ 1: สรุปภาพรวมความพร้อม")
    if not df.empty:
        col_volume = "ระดับเสียงประกาศ" 
        for col in df.columns:
            if "เสียง" in col or "ระดับ" in col:
                col_volume = col
                break
                
        total_reports = len(df)
        
        if col_volume in df.columns:
            pass_reports = len(df[df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)])
        else:
            pass_reports = 0
            
        fail_reports = total_reports - pass_reports
        pass_percentage = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("📝 จำนวนรายงานทั้งหมด", f"{total_reports} รายการ")
        c2.metric("✅ ผ่านเกณฑ์ (เสียงดังฟังชัด)", f"{pass_reports} รายการ")
        c3.metric("🎯 เปอร์เซ็นต์ความพร้อม", f"{pass_percentage:.2f} %")
        
        st.markdown("<br>", unsafe_allow_html=True)
        c_chart, c_data = st.columns([2, 1])
        with c_chart:
            chart_df = pd.DataFrame({
                "สถานะ": ["ผ่านเกณฑ์ (เสียงดังฟังชัด)", "ไม่ผ่านเกณฑ์ (อื่นๆ)"], 
                "จำนวน": [pass_reports, fail_reports]
            })
            st.bar_chart(chart_df.set_index("สถานะ"))
    else:
        st.info("ℹ️ ยังไม่มีข้อมูลในระบบ")
        
    st.markdown("---")
    
    # ==========================================
    # ส่วนที่ 2: ฟอร์มกรอกรายงาน
    # ==========================================
    st.header("📝 ส่วนที่ 2: ฟอร์มรายงานผลการทดสอบ")
    
    with st.form("report_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            floor = st.selectbox("คุณอยู่ชั้นไหน?", ["ชั้น G", "ชั้น 2", "ชั้น 3", "ชั้น 4", "ชั้น 5", "ชั้น 6"])
        with c2:
            dept = st.text_input("แผนกของคุณ")
            
        volume = st.radio(
            "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด?", 
            ["เสียงดังฟังชัด", "เบาเล็กน้อยแต่พอได้ยิน", "เบามากจับใจความไม่ได้", "ไม่ได้ยินเลย", "อื่นๆ"]
        )
        info = st.text_area("ข้อมูลเพิ่มเติม (ถ้ามี)")
        submit_btn = st.form_submit_button("🚀 ส่งรายงาน")
        
        if submit_btn:
            if floor == "" or dept == "":
                st.warning("⚠️ กรุณากรอกข้อมูลชั้นและแผนกให้ครบถ้วน")
            else:
                tz = pytz.timezone('Asia/Bangkok')
                timestamp = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
                
                # ส่งข้อมูลลง Google Sheet
                sheet.append_row([timestamp, floor, dept, volume, info])
                st.success("✅ บันทึกข้อมูลเข้า Google Sheets เรียบร้อยแล้ว!")
                st.cache_data.clear()
            
except Exception as e:
    st.error("กรุณาตรวจสอบการตั้งค่า Service Account")
