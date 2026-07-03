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
# 1. การตั้งค่า URL
# ==========================================
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwhENUa0dRVKuwJyX8IgoJwszlpsvxWssWXBsATe-cKUjNlsFuFgAtoRIvM39iXKEx/exec" 
PUBLIC_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSc1aDjn_PYGYPV2JZBJvns8mAoVKGAkL2Yb1nWOKQAcgYHukN7X_eKJf8KEYbEbSyJ-YmGlOpreZXv/pub?gid=0&single=true&output=csv"

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
@st.cache_data(ttl=10) 
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
    
    with c1: selected_month = st.selectbox("1. เลือกเดือน", months_th)
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
        depts_list = ["ทั้งหมด"] + department_data[selected_floor] if selected_floor != "ทั้งหมด" else ["ทั้งหมด"]
        selected_dept = st.selectbox("4. เลือกแผนก", depts_list)
        
    st.markdown("---")
    
    if not df.empty:
        filtered_df = df.copy()
        if selected_floor != "ทั้งหมด" and "คุณอยู่ชั้นไหน" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["คุณอยู่ชั้นไหน"] == selected_floor]
        if selected_dept != "ทั้งหมด" and "แผนก" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["แผนก"] == selected_dept]
        
        col_volume = "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" if "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด" in filtered_df.columns else filtered_df.columns[-2]
        
        total_reports = len(filtered_df)
        pass_reports = len(filtered_df[filtered_df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)]) if total_reports > 0 else 0
        fail_reports = total_reports - pass_reports
        pass_percentage = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
        
        # --- แสดงตัวเลขสรุปภาพรวม ---
        col1, col2, col3 = st.columns(3)
        col1.metric("📝 จำนวนรายงานทั้งหมด", f"{total_reports} รายการ")
        col2.metric("✅ ผ่านเกณฑ์ (เสียงดังฟังชัด)", f"{pass_reports} รายการ")
        col3.metric("🎯 เปอร์เซ็นต์ความพร้อม", f"{pass_percentage:.2f} %")
        
        st.markdown("---")
        
        # --- แบ่งเลย์เอาต์ซ้าย-ขวา สำหรับกราฟโดนัท และ ตารางสรุปรายชั้น ---
        chart_col, table_col = st.columns([1, 1.5])
        
        with chart_col:
            if total_reports > 0:
                st.subheader("📊 สัดส่วนภาพรวม")
                chart_data = pd.DataFrame({
                    "สถานะ": ["ผ่านเกณฑ์", "ไม่ผ่านเกณฑ์"],
                    "จำนวน": [pass_reports, fail_reports]
                })
                fig = px.pie(chart_data, values='จำนวน', names='สถานะ', hole=0.5, color='สถานะ',
                             color_discrete_map={"ผ่านเกณฑ์": "#28a745", "ไม่ผ่านเกณฑ์": "#dc3545"})
                fig.update_traces(textinfo='percent+label', textfont_size=16)
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ไม่มีข้อมูลสัดส่วน")

        with table_col:
            st.subheader("🏢 ผลการทดสอบตามพื้นที่ (รายชั้น)")
            
            # --- สร้างตาราง HTML/CSS (เอาเว้นวรรคด้านหน้าออกเพื่อไม่ให้ Streamlit มองเป็น Code Block) ---
            html_table = """<style>
.custom-table { width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; font-size: 14px; }
.custom-table th { padding: 12px 8px; border-bottom: 2px solid #555; color: #888; font-weight: normal;}
.custom-table td { padding: 12px 8px; border-bottom: 1px solid #333; }
.bar-bg { width: 100px; height: 10px; background-color: #333; border-radius: 5px; display: inline-block; vertical-align: middle; margin-right: 10px; overflow: hidden;}
.bar-fill { height: 100%; border-radius: 5px; }
</style>
<table class="custom-table">
<tr>
<th style="text-align: left;">พื้นที่ / อาคาร</th>
<th>ทั้งหมด (จุด)</th>
<th>ผ่าน</th>
<th>ไม่ผ่าน</th>
<th style="text-align: left;">ความพร้อม</th>
</tr>"""
            
            # วนลูปสร้างข้อมูลแต่ละชั้น
            for floor in department_data.keys():
                floor_df = df[df["คุณอยู่ชั้นไหน"] == floor] if "คุณอยู่ชั้นไหน" in df.columns else pd.DataFrame()
                f_total = len(floor_df)
                
                if f_total == 0:
                    continue 
                    
                f_pass = len(floor_df[floor_df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)])
                f_fail = f_total - f_pass
                f_percent = (f_pass / f_total) * 100
                
                if f_percent == 100:
                    bar_color = "#28a745" # สีเขียว
                elif f_percent >= 90:
                    bar_color = "#ffc107" # สีเหลือง
                else:
                    bar_color = "#dc3545" # สีแดง
                
                fail_color = "#dc3545" if f_fail > 0 else "inherit"
                
                html_table += f"""<tr>
<td style="text-align: left; font-weight: bold;">{floor}</td>
<td>{f_total}</td>
<td>{f_pass}</td>
<td style="color: {fail_color};">{f_fail}</td>
<td style="text-align: left;">
<div class="bar-bg">
<div class="bar-fill" style="width: {f_percent}%; background-color: {bar_color};"></div>
</div>
<span>{f_percent:.1f}%</span>
</td>
</tr>"""
            
            # เพิ่มแถวสรุปยอดรวมด้านล่างสุด
            grand_readiness = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
            html_table += f"""<tr style="font-weight: bold; background-color: rgba(255,255,255,0.05);">
<td style="text-align: left;">รวมทั้งหมด</td>
<td style="color: #17a2b8;">{total_reports}</td>
<td style="color: #28a745;">{pass_reports}</td>
<td style="color: #dc3545;">{fail_reports}</td>
<td style="text-align: left; color: #28a745;">{grand_readiness:.1f}%</td>
</tr>
</table>"""
            
            # เรนเดอร์ HTML ลงบน Streamlit
            st.markdown(html_table, unsafe_allow_html=True)
            
    else:
        st.warning("⚠️ ยังไม่มีข้อมูลในระบบ หรือยังไม่ได้ตั้งค่า PUBLIC_CSV_URL ให้ถูกต้อง")

# ==========================================
# 6. หน้าต่างการทำงาน: Form
# ==========================================
elif page == "📝 ฟอร์มรายงาน":
    st.title("📝 ฟอร์มรายงานผลการทดสอบระบบเสียง")
    st.markdown("---")
    
    with st.container(border=True):
        # 1. เลือกชั้น
        selected_floor_form = st.selectbox("1. คุณอยู่ชั้นไหน?", list(department_data.keys()))
        
        # 2. เลือกแผนก
        selected_dept_form = st.selectbox("2. แผนกของคุณ", department_data.get(selected_floor_form, []))
        
        # 3. เลือกระดับเสียง
        selected_volume = st.radio("3. ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด?", 
            ["เสียงดังฟังชัดดี", "เสียงดังฟังชัด", "เบาเล็กน้อยแต่พอได้ยิน", "เบามากจับใจความไม่ได้", "ไม่ได้ยินเลย", "อื่นๆ"])
        
        # 4. ข้อมูลเพิ่มเติม (ล็อคการพิมพ์ หากไม่ได้เลือก "อื่นๆ")
        # เช็คเงื่อนไข: ถ้าไม่ได้เลือก "อื่นๆ" ตัวแปร is_disabled จะเป็น True (ล็อค)
        is_disabled = True if selected_volume != "อื่นๆ" else False
        additional_info = st.text_area("4. ข้อมูลเพิ่มเติม (เฉพาะกรณีเลือก 'อื่นๆ')", disabled=is_disabled)
        
        # 5. ปุ่มส่งข้อมูล (เปลี่ยนจาก st.form_submit_button เป็น st.button ปกติ)
        submit_btn = st.button("🚀 บันทึกและส่งรายงาน")

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
                    st.cache_data.clear() 
                else:
                    st.error("❌ ไม่สามารถส่งข้อมูลได้ กรุณาตรวจสอบ WEB_APP_URL")
            except Exception as e:
                st.error("❌ เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง")
