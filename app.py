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
# 1. การตั้งค่า URL ของ Google Apps Script
# ==========================================
# ⚠️ ใส่ Web App URL ที่ได้จากขั้นตอนการ Deploy ใน Google Apps Script (ใช้ทั้งรับและส่งข้อมูล)
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzwhENUa0dRVKuwJyX8IgoJwszlpsvxWssWXBsATe-cKUjNlsFuFgAtoRIvM39iXKEx/exec" 

# ==========================================
# 2. ข้อมูลแผนกตั้งต้น (อิงจากโครงสร้างโรงพยาบาล)
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
# 3. ฟังก์ชันดึงข้อมูลแบบ Real-time (ผ่าน Apps Script)
# ==========================================
@st.cache_data(ttl=0) # ตั้งแคชเป็น 0 เพื่อบังคับให้ดึงใหม่ทันทีเมื่อมีการอัปเดตหรือกดรีเฟรช
def load_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        
        # ถ้าระบบส่งข้อมูลตารางกลับมา (ต้องมีมากกว่า 1 แถว รวมหัวตาราง)
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# ==========================================
# 4. เมนูด้านข้าง (Sidebar Navigation)
# ==========================================
st.sidebar.title("เมนูหลัก")
page = st.sidebar.radio("เลือกหน้าต่างการทำงาน:", ["📊 Dashboard สรุปผล", "📝 ฟอร์มรายงาน"])
st.sidebar.markdown("---")

# ปุ่มกดสำหรับดึงข้อมูลล่าสุดทันทีแบบ Real-time
if st.sidebar.button("🔄 ดึงข้อมูลล่าสุดเดี๋ยวนี้"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 5. หน้าต่างการทำงาน: Dashboard สรุปผล
# ==========================================
if page == "📊 Dashboard สรุปผล":
    st.title("📊 Dashboard ตรวจสอบระบบเสียงประกาศตามสาย")
    st.markdown("---")
    
    # --- กล่องตัวกรองข้อมูล ---
    with st.container(border=True):
        st.markdown("**🔍 ตัวกรองข้อมูล (Filters)**")
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
                
        with c3: selected_floor = st.selectbox("3. เลือกชั้น", ["ทั้งหมด"] + list(department_data.keys()))
        with c4:
            depts_list = ["ทั้งหมด"] + department_data[selected_floor] if selected_floor != "ทั้งหมด" else ["ทั้งหมด"]
            selected_dept = st.selectbox("4. เลือกแผนก", depts_list)
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not df.empty:
        # บังคับโครงสร้างชื่อคอลัมน์ให้แมปเข้ากับ JSON เพื่อป้องกัน Error
        df.columns = ["วัน/เดือน/ปี", "เวลา", "คุณอยู่ชั้นไหน", "แผนก", "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด", "ข้อมูลเพิ่มเติม"]
        
        # กรองข้อมูลตามฟิลเตอร์
        filtered_df = df.copy()
        if selected_floor != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["คุณอยู่ชั้นไหน"] == selected_floor]
        if selected_dept != "ทั้งหมด":
            filtered_df = filtered_df[filtered_df["แผนก"] == selected_dept]
        
        col_volume = "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด"
        
        total_reports = len(filtered_df)
        
        # เกณฑ์ตรวจสอบ: ต้องมีคำว่า "เสียงดังฟังชัด" เท่านั้น นอกนั้นถือว่าไม่ผ่านเกณฑ์ทั้งหมด
        pass_reports = len(filtered_df[filtered_df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)]) if total_reports > 0 else 0
        fail_reports = total_reports - pass_reports
        pass_percentage = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
        
        # --- กล่องสรุปผลตัวเลข (KPI 4 กล่อง) ---
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            with st.container(border=True): st.metric("🎯 ความพร้อมของระบบ", f"{pass_percentage:.1f}%")
        with kpi2:
            with st.container(border=True): st.metric("🔊 จำนวนจุดทั้งหมด", f"{total_reports}")
        with kpi3:
            with st.container(border=True): st.metric("✅ ผ่านการทดสอบ", f"{pass_reports}")
        with kpi4:
            with st.container(border=True): st.metric("❌ ไม่ผ่านการทดสอบ", f"{fail_reports}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- เลย์เอาต์ส่วนสรุปแผงควบคุมหลักด้านล่าง ---
        chart_col, table_col = st.columns([1, 1.8])
        
        with chart_col:
            with st.container(border=True):
                st.markdown("**สถานะอุปกรณ์ (สัดส่วนภาพรวม)**")
                if total_reports > 0:
                    chart_data = pd.DataFrame({
                        "สถานะ": ["ผ่าน", "ไม่ผ่าน"],
                        "จำนวน": [pass_reports, fail_reports]
                    })
                    fig = px.pie(chart_data, values='จำนวน', names='สถานะ', hole=0.6, color='สถานะ',
                                 color_discrete_map={"ผ่าน": "#28a745", "ไม่ผ่าน": "#dc3545"})
                    fig.update_traces(textinfo='percent+label', textfont_size=14)
                    fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=10, r=10), height=320)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลสัดส่วน")

        with table_col:
            with st.container(border=True):
                st.markdown("**ผลการทดสอบตามพื้นที่**")
                
                # ตารางแสดง HTML/CSS แบบไร้เว้นวรรคเพื่อป้องกันการแสดงเป็น Code Block บั๊กใน Markdown
                html_table = """<style>
.custom-table { width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: center; font-size: 14px; }
.custom-table th { padding: 10px 5px; border-bottom: 2px solid #555; color: #888; font-weight: normal;}
.custom-table td { padding: 10px 5px; border-bottom: 1px solid #333; }
.bar-bg { width: 80px; height: 10px; background-color: #333; border-radius: 5px; display: inline-block; vertical-align: middle; margin-right: 8px; overflow: hidden;}
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
                
                # สรุปรายชั้นอิงตามจำนวนฐานข้อมูล (df หลัก)
                for floor in department_data.keys():
                    floor_df = df[df["คุณอยู่ชั้นไหน"] == floor] if "คุณอยู่ชั้นไหน" in df.columns else pd.DataFrame()
                    f_total = len(floor_df)
                    if f_total == 0:
                        continue 
                        
                    f_pass = len(floor_df[floor_df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)])
                    f_fail = f_total - f_pass
                    f_percent = (f_pass / f_total) * 100
                    
                    # ตั้งค่าสีของแถบความคืบหน้าตามเกณฑ์ความพร้อม %
                    if f_percent == 100: bar_color = "#28a745" # เขียว
                    elif f_percent >= 90: bar_color = "#ffc107" # เหลือง
                    else: bar_color = "#dc3545" # แดง
                    
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
                
                grand_total = len(df)
                grand_pass = len(df[df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)]) if grand_total > 0 else 0
                grand_fail = grand_total - grand_pass
                grand_readiness = (grand_pass / grand_total) * 100 if grand_total > 0 else 0
                
                html_table += f"""<tr style="font-weight: bold; background-color: rgba(255,255,255,0.05);">
<td style="text-align: left;">รวมทั้งหมด</td>
<td style="color: #17a2b8;">{grand_total}</td>
<td style="color: #28a745;">{grand_pass}</td>
<td style="color: #dc3545;">{grand_fail}</td>
<td style="text-align: left; color: #28a745;">{grand_readiness:.1f}%</td>
</tr>
</table>"""
                st.markdown(html_table, unsafe_allow_html=True)
            
    else:
        st.warning("⚠️ ยังไม่มีข้อมูลในระบบ หรือเกิดข้อผิดพลาดในการเชื่อมต่อกรุณาตรวจสอบการเปิดใช้งาน doGet บน Apps Script")

# ==========================================
# 6. หน้าต่างการทำงาน: ฟอร์มกรอกรายงาน
# ==========================================
elif page == "📝 ฟอร์มรายงาน":
    st.title("📝 ฟอร์มรายงานผลการทดสอบระบบเสียง")
    st.markdown("---")
    
    with st.container(border=True):
        # ออกแบบส่วนควบคุมปกติไม่ผ่าน st.form เพื่อให้กล่องข้อความเปิด-ปิดตามทางเลือกได้ทันที (Interactive UI)
        selected_floor_form = st.selectbox("1. คุณอยู่ชั้นไหน?", list(department_data.keys()))
        selected_dept_form = st.selectbox("2. แผนกของคุณ", department_data.get(selected_floor_form, []))
        
        selected_volume = st.radio("3. ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด?", 
            ["เสียงดังฟังชัดดี" ,"เสียงดังฟังชัด", "เบาเล็กน้อยแต่พอได้ยิน", "เบามากจับใจความไม่ได้", "ไม่ได้ยินเลย", "อื่นๆ"])
        
        # เงื่อนไข: ช่องกรอกจะถูกปิดสีเทา (disabled=True) หากผู้ใช้เลือกหัวข้ออื่นๆ ที่ไม่ใช่คำว่า "อื่นๆ"
        is_disabled = True if selected_volume != "อื่นๆ" else False
        additional_info = st.text_area("4. ข้อมูลเพิ่มเติม (เปิดให้กรอกเฉพาะกรณีเลือกตัวเลือก 'อื่นๆ')", disabled=is_disabled)
        
        st.markdown("<br>", unsafe_allow_html=True)
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
                    st.cache_data.clear() # เคลียร์แคชระบบเพื่อพร้อมดึงตารางใหม่มาแสดงผล
                else:
                    st.error("❌ ไม่สามารถส่งข้อมูลได้ กรุณาตรวจสอบสิทธิ์และสถานะ URL เว็บแอปของคุณอีกครั้ง")
            except Exception as e:
                st.error("❌ เกิดข้อผิดพลาดในการเชื่อมต่อส่งข้อมูล กรุณาลองใหม่อีกครั้ง")
