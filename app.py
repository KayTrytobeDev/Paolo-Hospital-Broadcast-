import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import gspread
from google.oauth2.service_account import Credentials
import pytz

st.set_page_config(page_title="Dashboard ระบบเสียง", layout="wide", page_icon="🔊")

# ==========================================
# 1. ข้อมูลตั้งต้น (Data Dictionary)
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
# 2. ฟังก์ชันเชื่อมต่อ Google Sheets
# ==========================================
@st.cache_resource
def init_connection():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        return None

@st.cache_data(ttl=10)
def load_data():
    client = init_connection()
    if not client:
        return None, pd.DataFrame()
    sheet_url = "https://docs.google.com/spreadsheets/d/1FEuRJgW1et1EWeqFTlKJZa22nYfwcUWf3KsbTZdj1i0/edit"
    try:
        sheet = client.open_by_url(sheet_url).worksheet("Sheet1")
        data = sheet.get_all_records()
        return sheet, pd.DataFrame(data)
    except Exception as e:
        return None, pd.DataFrame()

sheet, df = load_data()

# ==========================================
# 3. เมนูด้านข้าง (Sidebar Navigation)
# ==========================================
st.sidebar.title("เมนูหลัก")
page = st.sidebar.radio("เลือกหน้าต่างการทำงาน:", ["📊 Dashboard สรุปผล", "📝 ฟอร์มรายงาน"])
st.sidebar.markdown("---")

# ==========================================
# 4. หน้าต่างการทำงาน: Dashboard
# ==========================================
if page == "📊 Dashboard สรุปผล":
    st.title("📊 Dashboard สรุปความพร้อมระบบเสียงประกาศตามสาย")
    st.markdown("---")
    
    st.subheader("🔍 ตัวกรองข้อมูล (Filters)")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        selected_month = st.selectbox("1. เลือกเดือน", months_th)
    with c2:
        # ระบบจำกัดปฏิทินตามเดือนที่เลือก
        if selected_month != "ทั้งหมด":
            current_year = datetime.now().year
            month_index = months_th.index(selected_month)
            last_day = calendar.monthrange(current_year, month_index)[1]
            min_d = date(current_year, month_index, 1)
            max_d = date(current_year, month_index, last_day)
            
            selected_date = st.date_input("2. เลือกวันที่ (ปฏิทิน)", value=None, min_value=min_d, max_value=max_d)
        else:
            selected_date = st.date_input("2. เลือกวันที่ (ปฏิทิน)", value=None)
            
    with c3:
        floors_list = ["ทั้งหมด"] + list(department_data.keys())
        selected_floor = st.selectbox("3. เลือกชั้น", floors_list)
        
    with c4:
        if selected_floor != "ทั้งหมด":
            depts_list = ["ทั้งหมด"] + department_data[selected_floor]
        else:
            depts_list = ["ทั้งหมด"]
        selected_dept = st.selectbox("4. เลือกแผนก", depts_list)
        
    st.markdown("---")
    
    # ถ้ามีข้อมูล ให้แสดงผล
    if not df.empty:
        # TODO: ใส่โค้ดส่วนการดึงข้อมูลมาตัดเกรด (Filter Dataframe) ตามตัวกรองที่เลือกไว้ที่นี่
        # เพื่อป้องกัน Error เบื้องต้นตอนนี้จะแสดงข้อมูลทั้งหมดก่อน
        filtered_df = df.copy() 
        
        # ค้นหาคอลัมน์ที่เก็บข้อมูลระดับเสียง
        col_volume = "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" if "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" in df.columns else df.columns[-2]
        
        total_reports = len(filtered_df)
        pass_reports = len(filtered_df[filtered_df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)])
        fail_reports = total_reports - pass_reports
        pass_percentage = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📝 จำนวนรายงานทั้งหมด", f"{total_reports} รายการ")
        col2.metric("✅ ผ่านเกณฑ์ (เสียงดังฟังชัด)", f"{pass_reports} รายการ")
        col3.metric("🎯 เปอร์เซ็นต์ความพร้อม", f"{pass_percentage:.2f} %")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("**สัดส่วนผลการประเมิน (ผ่าน vs ไม่ผ่าน)**")
        chart_df = pd.DataFrame({
            "สถานะ": ["ผ่านเกณฑ์", "ไม่ผ่านเกณฑ์"], 
            "จำนวน": [pass_reports, fail_reports]
        })
        st.bar_chart(chart_df.set_index("สถานะ"))
    else:
        st.info("ℹ️ ยังไม่มีข้อมูลในระบบ หรือไม่สามารถเชื่อมต่อ Google Sheets ได้")

# ==========================================
# 5. หน้าต่างการทำงาน: Form
# ==========================================
elif page == "📝 ฟอร์มรายงาน":
    st.title("📝 ฟอร์มรายงานผลการทดสอบระบบเสียง")
    st.markdown("---")
    
    st.markdown("กรุณาเลือกชั้นก่อน ระบบจึงจะแสดงชื่อแผนกในชั้นนั้นให้ท่านเลือก")
    
    selected_floor_form = st.selectbox("1. คุณอยู่ชั้นไหน?", list(department_data.keys()))
    
    with st.form("report_form", clear_on_submit=True):
        dept_list_form = department_data.get(selected_floor_form, [])
        selected_dept_form = st.selectbox("2. แผนกของคุณ", dept_list_form)
        
        selected_volume = st.radio(
            "3. ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด?", 
            ["เสียงดังฟังชัด", "เบาเล็กน้อยแต่พอได้ยิน", "เบามากจับใจความไม่ได้", "ไม่ได้ยินเลย", "อื่นๆ"]
        )
        
        additional_info = st.text_area("4. ข้อมูลเพิ่มเติม (ถ้ามี)")
        
        submit_btn = st.form_submit_button("🚀 บันทึกและส่งรายงาน")

        if submit_btn:
            tz = pytz.timezone('Asia/Bangkok')
            current_time = datetime.now(tz)
            date_str = current_time.strftime("%d %b %Y")
            time_str = current_time.strftime("%H:%M:%S")
            
            new_row = [date_str, time_str, selected_floor_form, selected_dept_form, selected_volume, additional_info]
            
            if sheet:
                sheet.append_row(new_row)
                st.success(f"✅ บันทึกข้อมูลของ **{selected_dept_form} ({selected_floor_form})** เข้าสู่ระบบเรียบร้อยแล้ว!")
                st.cache_data.clear() # ล้างแคชเพื่อให้หน้า Dashboard อัปเดตข้อมูลใหม่ทันที
            else:
                st.error("❌ ไม่สามารถส่งข้อมูลได้ กรุณาตรวจสอบการตั้งค่า Service Account")
