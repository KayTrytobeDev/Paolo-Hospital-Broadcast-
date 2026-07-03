import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import requests
import pytz

st.set_page_config(page_title="Dashboard ระบบเสียง", layout="wide", page_icon="🔊")

# ==========================================
# 1. ข้อมูลตั้งต้น และตั้งค่า
# ==========================================
# ก๊อปปี้ Web App URL ที่ได้จากขั้นตอนที่ 1 มาวางตรงนี้ครับ!
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwhENUa0dRVKuwJyX8IgoJwszlpsvxWssWXBsATe-cKUjNlsFuFgAtoRIvM39iXKEx/exec" 

# URL ของ CSV ของ Sheet1 ที่ตั้งค่าเป็น "ผู้มีสิทธิ์อ่านทุกคนที่มีลิงก์" ไว้ (เพื่อให้ Dashboard ดึงไปทำกราฟได้)
# วิธีทำ: ใน Google Sheets ไปที่ ไฟล์ > แชร์ > เผยแพร่ไปยังเว็บ > เลือก Sheet1 แบบ CSV แล้วก๊อปปี้ลิงก์มาวาง
PUBLIC_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSc1aDjn_PYGYPV2JZBJvns8mAoVKGAkL2Yb1nWOKQAcgYHukN7X_eKJf8KEYbEbSyJ-YmGlOpreZXv/pub?gid=0&single=true&output=csv"

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
# 2. ฟังก์ชันดึงข้อมูลมาทำ Dashboard (ดึงผ่าน CSV สาธารณะ)
# ==========================================
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(PUBLIC_CSV_URL)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

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
    with c1: selected_month = st.selectbox("1. เลือกเดือน", months_th)
    with c2: selected_date = st.date_input("2. เลือกวันที่", value=None)
    with c3: selected_floor = st.selectbox("3. เลือกชั้น", ["ทั้งหมด"] + list(department_data.keys()))
    with c4:
        depts_list = ["ทั้งหมด"] + department_data[selected_floor] if selected_floor != "ทั้งหมด" else ["ทั้งหมด"]
        selected_dept = st.selectbox("4. เลือกแผนก", depts_list)
        
    st.markdown("---")
    
    if not df.empty:
        col_volume = "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" if "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" in df.columns else df.columns[-2]
        
        total_reports = len(df)
        pass_reports = len(df[df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)])
        fail_reports = total_reports - pass_reports
        pass_percentage = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📝 จำนวนรายงานทั้งหมด", f"{total_reports} รายการ")
        col2.metric("✅ ผ่านเกณฑ์ (เสียงดังฟังชัด)", f"{pass_reports} รายการ")
        col3.metric("🎯 เปอร์เซ็นต์ความพร้อม", f"{pass_percentage:.2f} %")
    else:
        st.info("ℹ️ ยังไม่มีข้อมูลในระบบ หรือลืมใส่ PUBLIC_CSV_URL ในโค้ด")

# ==========================================
# 5. หน้าต่างการทำงาน: Form
# ==========================================
elif page == "📝 ฟอร์มรายงาน":
    st.title("📝 ฟอร์มรายงานผลการทดสอบระบบเสียง")
    st.markdown("---")
    
    selected_floor_form = st.selectbox("1. คุณอยู่ชั้นไหน?", list(department_data.keys()))
    
    with st.form("report_form", clear_on_submit=True):
        selected_dept_form = st.selectbox("2. แผนกของคุณ", department_data.get(selected_floor_form, []))
        selected_volume = st.radio("3. ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด?", 
            ["เสียงดังฟังชัด", "เบาเล็กน้อยแต่พอได้ยิน", "เบามากจับใจความไม่ได้", "ไม่ได้ยินเลย", "อื่นๆ"])
        additional_info = st.text_area("4. ข้อมูลเพิ่มเติม (ถ้ามี)")
        
        submit_btn = st.form_submit_button("🚀 บันทึกและส่งรายงาน")

        if submit_btn:
            tz = pytz.timezone('Asia/Bangkok')
            current_time = datetime.now(tz)
            date_str = current_time.strftime("%d %b %Y")
            time_str = current_time.strftime("%H:%M:%S")
            
            # เตรียมข้อมูลส่งไปที่ Apps Script
            payload = {
                "date": date_str,
                "time": time_str,
                "floor": selected_floor_form,
                "dept": selected_dept_form,
                "volume": selected_volume,
                "info": additional_info
            }
            
            # ยิงข้อมูลไปที่ Google Sheets!
            try:
                response = requests.post(WEB_APP_URL, data=payload)
                if response.text == "Success":
                    st.success(f"✅ บันทึกข้อมูลของ **{selected_dept_form}** เข้าสู่ระบบเรียบร้อยแล้ว!")
                    st.cache_data.clear()
                else:
                    st.error("❌ ไม่สามารถส่งข้อมูลได้ ลองตรวจสอบ WEB_APP_URL ดูครับ")
            except Exception as e:
                st.error("❌ เกิดข้อผิดพลาดในการเชื่อมต่อ")
