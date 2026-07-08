import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import requests
import pytz
import plotly.express as px
import os

# ==========================================
# 📱 ตั้งค่าหน้าเพจ & โครงสร้าง CSS (สไตล์ Dark Theme/แอปพลิเคชัน)
# ==========================================
st.set_page_config(page_title="Dashboard ระบบเสียง", layout="wide", page_icon="🔊", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@700&family=Prompt:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Oswald', 'Prompt', sans-serif !important;
    }
    
    /* ซ่อนเมนูพื้นฐาน Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ปรับแต่งการ์ด (Containers) */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #333;
    }
    
    /* ปรับตัวเลข KPI */
    [data-testid="stMetricValue"] {
        font-size: 48px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 18px !important;
        color: #AAAAAA !important;
    }
    
    /* ปรับปุ่ม */
    .stButton>button {
        width: 100%;
        height: 50px;
        font-size: 18px !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        background-color: #4CAF50 !important;
        color: white !important;
        border: none !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049 !important;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. การตั้งค่า URL ของ Google Apps Script
# ==========================================
# ⚠️ เปลี่ยน URL ด้านล่างนี้เป็น URL ใหม่ที่ได้จากการ Deploy ล่าสุดของคุณ
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzeszDpSeSlPoLd74PhbOwNgNfise1MHDlUCmkOUIWfHDntutl-_Ewntt4Gq8OFqdI8/exec" 

# ==========================================
# 2. ฟังก์ชันแปลวันที่
# ==========================================
months_th = ["ทั้งหมด", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
eng_to_thai_month = {
    "Jan": "ม.ค.", "Feb": "ก.พ.", "Mar": "มี.ค.", "Apr": "เม.ย.",
    "May": "พ.ค.", "Jun": "มิ.ย.", "Jul": "ก.ค.", "Aug": "ส.ค.",
    "Sep": "ก.ย.", "Oct": "ต.ค.", "Nov": "พ.ย.", "Dec": "ธ.ค."
}

def convert_to_thai_date(date_str):
    try:
        parts = str(date_str).split()
        if len(parts) == 3:
            day, month, year = parts
            thai_m = eng_to_thai_month.get(month, month)
            thai_y = int(year) + 543
            return f"{int(day)} {thai_m} {thai_y}"
    except:
        pass
    return date_str

# ==========================================
# 3. ฟังก์ชันดึงข้อมูล (Get Data)
# ==========================================
@st.cache_data(ttl=0) 
def load_data():
    try:
        response = requests.get(WEB_APP_URL)
        data = response.json()
        
        logs_data = data.get("logs", [])
        depts_data = data.get("departments", [])
        
        df_logs = pd.DataFrame(logs_data[1:], columns=logs_data[0]) if len(logs_data) > 1 else pd.DataFrame()
        df_depts = pd.DataFrame(depts_data[1:], columns=depts_data[0]) if len(depts_data) > 1 else pd.DataFrame()
        
        return df_logs, df_depts
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df, df_depts = load_data()

# ==========================================
# 4. สร้างพจนานุกรมชั้นและแผนกอัตโนมัติ
# ==========================================
department_data = {}
if not df_depts.empty:
    for col in df_depts.columns:
        if str(col).strip() != "":
            depts = df_depts[col].dropna().astype(str).str.strip()
            depts = depts[depts != ""].tolist()
            department_data[str(col)] = depts

# ==========================================
# 5. เมนูด้านข้าง (Sidebar Navigation)
# ==========================================
st.sidebar.markdown("## ⚙️ เมนูหลัก")
page = st.sidebar.radio("เลือกหน้าต่างการทำงาน:", ["📊 Dashboard สรุปผล", "📝 ฟอร์มรายงาน"])
st.sidebar.markdown("---")

if st.sidebar.button("🔄 อัปเดตข้อมูลล่าสุด"):
    st.cache_data.clear()
    st.rerun()

# ==========================================
# 6. หน้าต่างการทำงาน: Dashboard สรุปผล
# ==========================================
if page == "📊 Dashboard สรุปผล":
    st.markdown("## 📊 สรุปผลการทดสอบระบบเสียง")
    
    # 🌟 เช็คว่ามีข้อมูลหรือไม่
    if not df.empty:
        df.columns = ["วัน/เดือน/ปี", "เวลา", "คุณอยู่ชั้นไหน", "แผนก", "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด", "ข้อมูลเพิ่มเติม"]
    
        # ตัวกรองข้อมูล (ซ่อนไว้ใน Expander เพื่อความสะอาดตา)
        with st.expander("🔍 ค้นหา / กรองข้อมูล (Filters)", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            with c1: selected_month = st.selectbox("เลือกเดือน", months_th)
            with c2:
                if selected_month != "ทั้งหมด":
                    current_year = datetime.now().year
                    month_index = months_th.index(selected_month)
                    last_day = calendar.monthrange(current_year, month_index)[1]
                    min_d = date(current_year, month_index, 1)
                    max_d = date(current_year, month_index, last_day)
                    selected_date = st.date_input("เลือกวันที่", value=None, min_value=min_d, max_value=max_d)
                else:
                    selected_date = st.date_input("เลือกวันที่", value=None)
                    
            with c3: selected_floor = st.selectbox("เลือกชั้น", ["ทั้งหมด"] + list(department_data.keys()))
            with c4:
                depts_list = ["ทั้งหมด"] + department_data.get(selected_floor, []) if selected_floor != "ทั้งหมด" else ["ทั้งหมด"]
                selected_dept = st.selectbox("เลือกแผนก", depts_list)
                
        # คัดกรองข้อมูล
        filtered_df = df.copy()
        if isinstance(selected_date, date):
            date_str = selected_date.strftime("%d %b %Y")
            date_str_no_zero = date_str[1:] if date_str.startswith("0") else date_str
            filtered_df = filtered_df[filtered_df["วัน/เดือน/ปี"].isin([date_str, date_str_no_zero])]
        elif selected_month != "ทั้งหมด":
            month_idx = months_th.index(selected_month)
            filtered_df['TempDate'] = pd.to_datetime(filtered_df['วัน/เดือน/ปี'], format='%d %b %Y', errors='coerce')
            filtered_df = filtered_df[filtered_df['TempDate'].dt.month == month_idx]
                
        if selected_floor != "ทั้งหมด": filtered_df = filtered_df[filtered_df["คุณอยู่ชั้นไหน"] == selected_floor]
        if selected_dept != "ทั้งหมด": filtered_df = filtered_df[filtered_df["แผนก"] == selected_dept]
            
        col_volume = "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด"
        total_reports = len(filtered_df)
        
        pass_reports = len(filtered_df[filtered_df[col_volume].astype(str).str.contains("เสียงดังฟังชัด", na=False)]) if total_reports > 0 else 0
        fail_reports = total_reports - pass_reports
        pass_percentage = (pass_reports / total_reports) * 100 if total_reports > 0 else 0
        
        # กล่องสรุปผล KPI
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("🎯 ความพร้อมระบบ", f"{pass_percentage:.0f}%")
        with kpi2:
            st.metric("🔊 จุดทดสอบทั้งหมด", f"{total_reports}")
        with kpi3:
            st.metric("✅ เสียงดังฟังชัด", f"{pass_reports}")
        with kpi4:
            st.metric("❌ พบปัญหา", f"{fail_reports}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        # เลย์เอาต์: กราฟวงกลม ด้านซ้าย และ ตารางรายการล่าสุด ด้านขวา
        col_chart, col_table = st.columns([1, 2.5])
        
        with col_chart:
            st.markdown("#### สถานะภาพรวม")
            if total_reports > 0:
                chart_data = pd.DataFrame({"สถานะ": ["ปกติ", "พบปัญหา"], "จำนวน": [pass_reports, fail_reports]})
                fig = px.pie(chart_data, values='จำนวน', names='สถานะ', hole=0.7, color='สถานะ',
                             color_discrete_map={"ปกติ": "#00E676", "พบปัญหา": "#FF1744"})
                fig.update_traces(textinfo='percent', textfont_size=16)
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                                  margin=dict(t=10, b=10, l=10, r=10), height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ไม่มีข้อมูล")

        with col_table:
            st.markdown("#### รายการแจ้งเหตุล่าสุด")
            if not filtered_df.empty:
                # เลือกโชว์เฉพาะคอลัมน์ที่จำเป็น ดึง 15 รายการล่าสุด และกลับด้านให้ล่าสุดอยู่บน
                display_df = filtered_df[["วัน/เดือน/ปี", "เวลา", "คุณอยู่ชั้นไหน", "แผนก", "ท่านได้ยินระดับเสียงประกาศตามสายเท่าใด"]].tail(15)
                display_df = display_df.iloc[::-1] # เรียงล่าสุดขึ้นก่อน
                display_df.columns = ["วันที่", "เวลา", "ชั้น", "แผนก", "สถานะ"]
                st.dataframe(display_df, use_container_width=True, hide_index=True, height=350)
            else:
                st.info("ไม่มีรายการในเงื่อนไขที่เลือก")
                
    else:
        # ========================================================
        # 🚨 กรณีไม่มีข้อมูล (โชว์รูปภาพ Error แบบในรูป)
        # ========================================================
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # ⚠️ ต้องมีไฟล์รูปภาพชื่อ no_data.png อยู่ในโฟลเดอร์เดียวกันกับไฟล์นี้
            if os.path.exists("no_data.png"):
                st.image("no_data.png", use_container_width=True)
            else:
                st.warning("⚠️ ไม่พบไฟล์รูปภาพ 'no_data.png' กรุณาเซฟรูปใส่โฟลเดอร์เดียวกับโค้ด")
            st.markdown("<h3 style='text-align: center; color: #888;'>ยังไม่มีข้อมูลในระบบ หรือเชื่อมต่อไม่ได้</h3>", unsafe_allow_html=True)

# ==========================================
# 7. หน้าต่างการทำงาน: ฟอร์มกรอกรายงาน
# ==========================================
elif page == "📝 ฟอร์มรายงาน":
    st.markdown("## 📝 ฟอร์มรายงานผลการทดสอบ")
    
    with st.container():
        selected_floor_form = st.selectbox("1. คุณอยู่ชั้นไหน?", list(department_data.keys()) if department_data else ["กำลังโหลด..."])
        selected_dept_form = st.selectbox("2. แผนกของคุณ", department_data.get(selected_floor_form, []) if department_data else [])
        
        selected_volume = st.radio("3. ระดับเสียงที่ได้ยิน", 
            ["เสียงดังฟังชัดดี", "เสียงเบามากๆ", "ไม่ได้ยินเสียงโว้ย!", "เสียงขาดๆ หายๆ เสียง ซ่าๆ", "อื่นๆ"])
        
        is_disabled = True if selected_volume != "อื่นๆ" else False
        additional_info = st.text_area("4. ข้อมูลเพิ่มเติม (เฉพาะกรณีเลือก 'อื่นๆ')", disabled=is_disabled)
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.button("🚀 บันทึกข้อมูล")

        if submit_btn:
            tz = pytz.timezone('Asia/Bangkok')
            current_time = datetime.now(tz)
            date_str = current_time.strftime("%d %b %Y")
            time_str = current_time.strftime("%H:%M:%S")
            
            payload = {
                "date": date_str, "time": time_str, "floor": selected_floor_form,
                "dept": selected_dept_form, "volume": selected_volume, "info": additional_info
            }
            
            try:
                response = requests.post(WEB_APP_URL, data=payload)
                if response.text == "Success":
                    st.success(f"✅ บันทึกข้อมูลของ **{selected_dept_form}** เรียบร้อยแล้ว!")
                    st.cache_data.clear() 
                else:
                    st.error("❌ ไม่สามารถส่งข้อมูลได้ กรุณาตรวจสอบ URL ของคุณ")
            except Exception as e:
                st.error("❌ เกิดข้อผิดพลาดในการเชื่อมต่อ")
