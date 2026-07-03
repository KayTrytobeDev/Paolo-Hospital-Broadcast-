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
    
    if not df.empty:
        # กรองข้อมูลตามที่เลือก
        filtered_df = df.copy()
        if selected_floor != "ทั้งหมด" and "คุณอยู่ชั้นไหน" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["คุณอยู่ชั้นไหน"] == selected_floor]
        if selected_dept != "ทั้งหมด" and "แผนก" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["แผนก"] == selected_dept]
        
        # ค้นหาคอลัมน์ระดับเสียง
        col_volume = "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" if "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" in filtered_df.columns else filtered_df.columns[-2]
        
        total_reports = len(filtered_df)
        pass_reports = len(filtered_df[filtered_df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)]) if total_reports > 0 else 0
        fail_reports = total_reports - pass_reports
        pass_percentage = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
        
        # 1. แสดงตัวเลขสรุป
        col1, col2, col3 = st.columns(3)
        col1.metric("📝 จำนวนรายงานทั้งหมด", f"{total_reports} รายการ")
        col2.metric("✅ ผ่านเกณฑ์ (เสียงดังฟังชัด)", f"{pass_reports} รายการ")
        col3.metric("🎯 เปอร์เซ็นต์ความพร้อม", f"{pass_percentage:.2f} %")
        
        st.markdown("---")
        
        # 2. สร้างกราฟโดนัท
        if total_reports > 0:
            st.subheader("📊 กราฟสัดส่วนความพร้อมของระบบเสียง")
            
            chart_data = pd.DataFrame({
                "สถานะ": ["ผ่านเกณฑ์ (เสียงดังฟังชัด)", "ไม่ผ่านเกณฑ์ (อื่นๆ)"],
                "จำนวน": [pass_reports, fail_reports]
            })
            
            fig = px.pie(
                chart_data, 
                values='จำนวน', 
                names='สถานะ', 
                hole=0.5, 
                color='สถานะ',
                color_discrete_map={
                    "ผ่านเกณฑ์ (เสียงดังฟังชัด)": "#28a745", 
                    "ไม่ผ่านเกณฑ์ (อื่นๆ)": "#dc3545"      
                }
            )
            
            fig.update_traces(textinfo='percent+label', textfont_size=16)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ ไม่มีข้อมูลที่ตรงกับเงื่อนไขที่คุณเลือกครับ")
            
    else:
        st.warning("⚠️ ยังไม่มีข้อมูลในระบบ หรือยังไม่ได้ตั้งค่า PUBLIC_CSV_URL ให้ถูกต้อง")

# ==========================================
# 6. หน้าต่างการทำงาน: Form
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
            
            payload = {
                "date": date_str,
                "time": time_str,
                "floor": selected_floor_form,
                "dept": selected_dept_form,
                "volume": selected_volume,
                "info": additional_info
            }
            
            try:
                response = requests.post(WEB_APP_URL, data=payload)
                if response.text == "Success":
                    st.success(f"✅ บันทึกข้อมูลของ **{selected_dept_form}** เข้าสู่ระบบเรียบร้อยแล้ว!")
                    st.cache_data.clear() # รีเซ็ตแคชเพื่อให้กราฟอัปเดตใหม่
                else:
                    st.error("❌ ไม่สามารถส่งข้อมูลได้ กรุณาตรวจสอบ WEB_APP_URL")
            except Exception as e:
                st.error("❌ เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง")
