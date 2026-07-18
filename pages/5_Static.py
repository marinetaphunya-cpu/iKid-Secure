import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

# 2. เชื่อมต่อ Supabase
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# **จุดสำคัญ 1: กำหนดสีมาตรฐานสำหรับ 3 ระดับ**
# เพื่อให้กราฟทุกตัวใช้สีเดียวกัน (เหลือง, ส้ม, แดง)
LEVEL_COLORS = {1.0: "#FFEB3B", 2.0: "#FF9800", 3.0: "#F44336"} # เหลือง, ส้ม, แดง

# **จุดสำคัญ 2: เปลี่ยนจุดสี Legend ในเชิงสถิติให้เป็นสี่เหลี่ยม**
st.markdown(
    """
    <style>
    /* เปลี่ยนจุด Legend ของ Plotly ให้เป็นสี่เหลี่ยม */
    .legend-item rect {
        rx: 0 !important; /* ทำให้มุมไม่มน */
        ry: 0 !important;
        width: 14px !important;
        height: 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- หัวข้อพร้อมสติกเกอร์ ---
col_title1, col_title2 = st.columns([10, 1])
with col_title1:
    st.title("📊 สถิติภาพรวมความปลอดภัยผู้ป่วย")
with col_title2:
    st.title("✨") # สติกเกอร์วิ้งๆ
st.markdown("---")

try:
    # 3. ดึงข้อมูลจาก Supabase (ดึงข้อมูลจริงทั้งหมดที่นี่)
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # --- ส่วน Clean ข้อมูล (เตรียมข้อมูลมาตรฐาน) ---
        # 1. แปลง created_at เป็น datetime และลบแถวที่ไม่มีวันที่
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df = df.dropna(subset=['created_at']) 

        # 2. แปลง aggression_level ให้เป็นตัวเลข (ลบคำว่า "ระดับ" หรือ "Lv" ออก)
        # ระบบจะดึงข้อมูลมาเองว่ามีค่าอะไรบ้าง (เช่น 1, 2, 3)
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float)

        # 3. แปลง incident_count ให้เป็นตัวเลข (กรณีเก็บเป็น String)
        df["incident_count"] = df["incident_count"].astype(str).str.extract('(\d+)').astype(float).fillna(1.0)

        # กรองเอาเฉพาะเคสที่มีระดับ 1, 2, หรือ 3 ตามที่ไอด้าต้องการ
        df_filtered = df[df["aggression_level"].isin([1.0, 2.0, 3.0])]

        if df_filtered.empty:
             st.info("ยังไม่มีข้อมูลการประเมินระดับ 1-3 ในระบบเจ้า ✨")
        else:
            # --- ส่วนแสดง KPI (ยอดสะสม) ---
            total_cases = int(len(df_filtered))
            max_level = int(df_filtered["aggression_level"].max())
            avg_level = round(df_filtered["aggression_level"].mean(), 1)

            c1, c2, c3 = st.columns(3)
            # 1. จำนวนเคสรวม (ยอดสะสม)
            c1.metric("จำนวนเคสรวม (Lv.1-3)", total_cases)
            # 2. ระดับความรุนแรงสูงสุด
            c2.metric("ระดับความรุนแรงสูงสุด", max_level)
            # 3. ค่าเฉลี่ยความรุนแรง
            c3.metric("ค่าเฉลี่ยความรุนแรง", avg_level)
            
            st.divider()

            # --- 5. แสดงกราฟ (ตาม Flow Chart ใหม่) ---
            
            # **1. กราฟแท่ง (Bar Chart) - แสดงจำนวนครั้งตามระดับความรุนแรง**
            st.subheader("📈 จำนวนครั้งตามระดับความรุนแรง (OAS) 📋") 
            # รวม incident_count ตามระดับจริงที่ดึงมา
            bar_df = df_filtered.groupby("aggression_level")["incident_count"].sum().reset_index()
            
            # ทำให้แกน X เป็นแบบ Category เพื่อให้กราฟไม่เว้นช่องว่าง (เช่น 1.5, 2.5)
            bar_df["aggression_level_str"] = bar_df["aggression_level"].astype(int).astype(str)

            fig_bar = px.bar(bar_df, x="aggression_level_str", y="incident_count",
                             color="aggression_level", # ใช้ระดับจริงเพื่อดึงสีที่กำหนดไว้
                             color_discrete_map=LEVEL_COLORS) # map สีที่กำหนดเอง

            # ปรับแต่ง Layout ของแกน X และปิด Legend เฉพาะกราฟนี้
            fig_bar.update_layout(xaxis_title="ระดับความรุนแรง (OAS)", yaxis_title="จำนวนครั้ง", coloraxis_showscale=False)
            fig_bar.update_xaxes(type='category') # ยืนยันว่าแกน X เป็นหมวดหมู่ (เหลือง, ส้ม, แดง จะอยู่ชิดกัน)
            fig_bar.update_traces(showlegend=False) # ปิด Legend ของกราฟนี้ เพราะจะไปใช้ Legend รวมด้านล่าง
            st.plotly_chart(fig_bar, use_container_width=True)

            # **2. แนวโน้มระยะยาว (แสดงเป็นจุด 3 จุดตามจำนวนครั้ง)**
            st.divider()
            st.subheader("📉 แนวโน้มความรุนแรงระยะยาว 📈") 
            
            df_filtered["month_name"] = df_filtered["created_at"].dt.month_name() # เช่น July
            # **แก้ไข: แปลงปีให้เป็น String และจัดกลุ่มเป็นหมวดหมู่**
            # เพื่อให้แกน X แสดงแค่ "2026" และมีประเภทเป็น "year"
            df_filtered["year_str"] = df_filtered["created_at"].dt.year.astype(int).astype(str) # เช่น 2026
            
            g1, g2 = st.columns(2)
            
            with g1:
                st.write("แนวโน้มรายเดือน")
                # เตรียมข้อมูลรายเดือน (Group by เดือน และ ระดับความรุนแรง) นับจำนวนครั้ง
                monthly_trend = df_filtered.groupby(["month_name", "aggression_level"])["incident_count"].sum().reset_index()
                
                # **แก้ไขจุดสำคัญ: ใช้สี เหลือง ส้ม แดง ตามระดับความรุนแรง**
                # ใช้ Scatter plot เพื่อให้โชว์เป็น 3 จุดในแต่ละเดือน ขนาดจุดเท่ากัน ความสูงบนแกน Y คือจำนวนครั้ง
                fig_m = px.scatter(monthly_trend, x="month_name", y="incident_count",
                                   color="aggression_level", color_discrete_map=LEVEL_COLORS,
                                   size_max=20) # กำหนดขนาดจุดให้เหมาะสมและเท่ากัน

                fig_m.update_layout(xaxis_title="เดือน", yaxis_title="จำนวนครั้ง", coloraxis_showscale=False)
                # ปิด Legend ของกราฟนี้
                fig_m.update(layout_showlegend=False)
                st.plotly_chart(fig_m, use_container_width=True)
                st.caption("*ความสูงของจุดบนแกน Y แสดงจำนวนครั้งที่เกิดเหตุในระดับนั้นๆ ในแต่ละเดือน")
                
            with g2:
                st.write("แนวโน้มรายปี")
                # เตรียมข้อมูลรายปี (Group by ปี และ ระดับความรุนแรง) นับจำนวนครั้ง
                yearly_trend = df_filtered.groupby(["year_str", "aggression_level"])["incident_count"].sum().reset_index()
                # กรองเอาแค่ปี 2026 มาโชว์ (ถ้าใน DB มีปีอื่นๆ ก็จะนับรวมได้อัตโนมัติเจ้า)
                # yearly_2026 = yearly_trend[yearly_trend["year_str"] == "2026"]
                
                # **แก้ไขจุดสำคัญ: แกน X เป็นปี (Year) ที่เป็น String และใช้สี เหลือง ส้ม แดง**
                fig_y = px.scatter(yearly_trend, x="year_str", y="incident_count",
                                   color="aggression_level", color_discrete_map=LEVEL_COLORS,
                                   size_max=20)
                
                # ปรับแต่ง Layout ของแกน X ให้เป็นหมวดหมู่ (เหลือง, ส้ม, แดง จะอยู่ชิดกัน)
                fig_y.update_layout(xaxis_title="ปี (Year)", yaxis_title="จำนวนครั้ง", coloraxis_showscale=False)
                fig_y.update_xaxes(type='category') # ยืนยันว่าแกน X เป็นหมวดหมู่ (2026) ไม่ใช่แกนเวลา
                # ปิด Legend ของกราฟนี้
                fig_y.update(layout_showlegend=False)
                st.plotly_chart(fig_y, use_container_width=True)
                st.caption("*ความสูงของจุดบนแกน Y แสดงจำนวนครั้งที่เกิดเหตุในระดับนั้นๆ ในแต่ละปี")

            # **Legend รวมอธิบายความหมายของสีแบบสี่เหลี่ยม (ใช้ร่วมกันทุกกราฟ)**
            st.divider()
            st.markdown("### ความหมายของสี (Legend)")
            
            # **แก้ไข: เปลี่ยนจากวงกลมเป็นสี่เหลี่ยมเชิงสถิติตามคำสั่ง**
            c_l1, c_l2, c_l3 = st.columns(3)
            
            # พี่ใช้ HTML/CSS สั้นๆ เพื่อทำสี่เหลี่ยมเจ้าไอด้า
            st.markdown(
                """
                <div style="display: flex; gap: 20px; justify-content: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: #FFEB3B; border-radius: 0px;"></div>
                        <span>ระดับ 1 : ต่ำ</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: #FF9800; border-radius: 0px;"></div>
                        <span>ระดับ 2 : ปานกลาง</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: #F44336; border-radius: 0px;"></div>
                        <span>ระดับ 3 : สูง</span>
                    </div>
                </div>
                <br>
                """,
                unsafe_allow_html=True
)

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบเจ้า ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

st.divider()
# ปุ่มกลับ พร้อมสติกเกอร์
if st.button("⬅️ กลับหน้า Dashboard 🏡", use_container_width=True): # เพิ่มสติกเกอร์บ้าน
    st.switch_page("pages/1_Dashboard.py")



