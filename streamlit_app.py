import streamlit as st
import pandas as pd
from io import StringIO
from datetime import date

st.set_page_config(page_title="ระบบจัดการข้อมูล Transfer Pricing", layout="wide")
st.title("ระบบจัดการข้อมูล Transfer Pricing")

# Session state for data
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=[
        'วันที่', 'หน่วยงานให้บริการ', 'ชื่อบริการ', 'ราคาต่อหน่วย', 'หน่วยงานรับบริการ', 'จำนวน', 'ยอดรวม'
    ])

sample_providers = ['IT แผนก', 'HR แผนก', 'การเงิน แผนก', 'การตลาด แผนก']
sample_receivers = ['สำนักงานใหญ่', 'สาขา A', 'สาขา B', 'สาขา C', 'โรงงาน 1', 'โรงงาน 2']
sample_services = ['บริการ IT Support', 'บริการจัดการทรัพยากรบุคคล', 'บริการทางการเงิน', 'บริการการตลาด', 'บริการปรึกษา']

# Navigation
view = st.radio(
    "",
    ["เพิ่มข้อมูลใหม่", "รายการข้อมูล", "Crosstab"],
    horizontal=True,
    index=0
)

# Import/Export buttons
col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("นำเข้าข้อมูล (CSV)", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if set(['วันที่', 'หน่วยงานให้บริการ', 'ชื่อบริการ', 'ราคาต่อหน่วย', 'หน่วยงานรับบริการ', 'จำนวน', 'ยอดรวม']).issubset(df.columns):
                st.session_state['data'] = pd.concat([st.session_state['data'], df], ignore_index=True)
                st.success(f"นำเข้าข้อมูลสำเร็จ {len(df)} รายการ")
            else:
                st.error("ไฟล์ CSV ไม่ถูกต้อง กรุณาตรวจสอบหัวตาราง")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
with col2:
    csv = st.session_state['data'].to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="ส่งออกข้อมูล (CSV)",
        data=csv,
        file_name=f'transfer_pricing_{date.today()}.csv',
        mime='text/csv'
    )

# --- Form View ---
if view == "เพิ่มข้อมูลใหม่":
    st.subheader("เพิ่มข้อมูลใหม่")
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            input_date = st.date_input("วันที่", value=date.today(), format="%m/%d/%Y")
        with c2:
            service_provider = st.selectbox("หน่วยงานให้บริการ", ["เลือกหน่วยงาน"] + sample_providers)
        with c3:
            service_name = st.selectbox("ชื่อบริการ", ["เลือกบริการ"] + sample_services)
        c4, c5, c6 = st.columns(3)
        with c4:
            price = st.number_input("ราคาต่อหน่วย (บาท)", min_value=0.0, step=0.01, format="%.2f")
        with c5:
            service_receiver = st.selectbox("หน่วยงานรับบริการ", ["เลือกหน่วยงาน"] + sample_receivers)
        with c6:
            quantity = st.number_input("จำนวนการใช้งาน", min_value=0.0, step=1.0, format="%.0f")
        submitted = st.form_submit_button("เพิ่มข้อมูล")
        if submitted:
            if (service_provider == "เลือกหน่วยงาน" or service_name == "เลือกบริการ" or service_receiver == "เลือกหน่วยงาน"):
                st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
            else:
                total = price * quantity
                new_row = pd.DataFrame({
                    'วันที่': [input_date.strftime('%Y-%m-%d')],
                    'หน่วยงานให้บริการ': [service_provider],
                    'ชื่อบริการ': [service_name],
                    'ราคาต่อหน่วย': [price],
                    'หน่วยงานรับบริการ': [service_receiver],
                    'จำนวน': [quantity],
                    'ยอดรวม': [total]
                })
                st.session_state['data'] = pd.concat([st.session_state['data'], new_row], ignore_index=True)
                st.success("เพิ่มข้อมูลสำเร็จ!")

# --- List View ---
elif view == "รายการข้อมูล":
    st.subheader("รายการข้อมูลทั้งหมด")
    if st.session_state['data'].empty:
        st.info("ยังไม่มีข้อมูล")
    else:
        st.dataframe(st.session_state['data'], use_container_width=True, hide_index=True)

# --- Crosstab View ---
elif view == "Crosstab":
    st.subheader("ตารางแสดงข้อมูลแบบ Crosstab")
    if st.session_state['data'].empty:
        st.info("ยังไม่มีข้อมูลสำหรับแสดงผล")
    else:
        df = st.session_state['data']
        crosstab = pd.pivot_table(
            df,
            index=['หน่วยงานให้บริการ', 'ชื่อบริการ', 'ราคาต่อหน่วย'],
            columns='หน่วยงานรับบริการ',
            values='จำนวน',
            aggfunc='sum',
            fill_value=0
        )
        st.dataframe(crosstab, use_container_width=True)
