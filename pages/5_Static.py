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

st.title("📊 สถิติภาพรวม")
st.markdown("---")

try:
    # 3. ดึงข้อมูลจาก Supabase
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # --- ส่วน Clean ข้อมูล (มาตรฐานเดียวจบ!) ---
        # 1. แปลง created_at เป็น datetime และลบค่าว่าง
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df = df.dropna(subset=['created_at']) 

        # 2. แปลง aggression_level ให้เป็นตัวเลข 1, 2, 3 เท่านั้น (ลบคำว่า "ระดับ" ออก)
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float)
        # กรองเอาเฉพาะระดับ 1, 2, 3 ตามที่ไอด้าสั่ง (ไม่เอา 0 หรือค่าอื่น)
        df = df[df["aggression_level"].isin([1.0, 2.0, 3.0])]

        # 3. แปลง incident_count ให้เป็นตัวเลข
        df["incident_count"] = df["incident_count"].astype(str).str.extract('(\d+)').astype(float).fillna(1.0)

        if df.empty:
             st.info("ยังไม่มีข้อมูลการประเมินระดับ 1-3 ในระบบเจ้า ✨")
        else:
            # --- ส่วนแสดง KPI ---
            total_incidents = df["incident_count"].sum()
            max_level = int(df["aggression_level"].max())
            avg_level = round(df["aggression_level"].mean(), 1)

            c1, c2, c3 = st.columns(3)
            c1.metric("จำนวนเคส (Lv.1-3)", int(len(df)))
            c2.metric("ระดับความรุนแรงสูงสุด", max_level)
            c3.metric("ค่าเฉลี่ยความรุนแรง", avg_level)
            
            st.divider()

            # --- 5. แสดงกราฟ (เวอร์ชัน Final ตามไอด้าสั่ง) ---
            
            # **บนซ้าย: กราฟแท่ง (Bar Chart) - มีแค่ 3 ระดับ 1, 2, 3 พร้อม Legend สี**
            st.subheader("📈 จำนวนครั้งตามระดับความรุนแรง (OAS)")
            bar_df = df.groupby("aggression_level")["incident_count"].sum().reset_index()
            # กำหนดสีเฉพาะ Lv. 1, 2, 3
            bar_colors = {1.0: "#FFEB3B", 2.0: "#FF9800", 3.0: "#F44336"}
            
            fig_bar = px.bar(bar_df, x="aggression_level", y="incident_count",
                             color="aggression_level", # ใช้ระดับเพื่อแบ่งสี
                             color_discrete_map=bar_colors) # map สีที่กำหนดเอง

            fig_bar.update_layout(xaxis_title="ระดับความรุนแรง (OAS)", yaxis_title="จำนวนครั้ง", coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)
            # **Legend อธิบายสีสำหรับ Bar Chart**
            st.caption("🟡 ระดับ 1 (เหลือง) | 🟠 ระดับ 2 (ส้ม) | 🔴 ระดับ 3 (แดง)")

            # **บนขวา: แผนภูมิวงกลม (Pie Chart) - แยกสี, มี % และ Legend อธิบายพฤติกรรม**
            st.divider()
            st.subheader("📊 สัดส่วนพฤติกรรม (OSA) - ตามข้อมูลจริง")
            
            pie_df = df.groupby("behavior_note")["incident_count"].sum().reset_index()
            
            # กำหนดสีที่แตกต่างกันสำหรับแต่ละพฤติกรรม (สูงสุด 5 สี)
            behavior_color_map = {
                "ไม่มีพฤติกรรมก้าวร้าวต่อผู้อื่น": "#2196F3",
                "พูดจาตะคอกเสียงดัง": "#F44336",
                "ขว้างปาสิ่งของ": "#FF9800",
                "ระดับ 2: ด่าคำหยาบคาย แสดงท่าทางคุกคาม...": "#9C27B0",
                # เพิ่มพฤติกรรมอื่นๆ ตามข้อมูลจริง
            }
            
            fig_pie = px.pie(pie_df, names="behavior_note", values="incident_count", hole=0.4,
                             color="behavior_note", color_discrete_map=behavior_color_map)
            
            # แก้ Layout ให้ Pie เห็นชัดบนมือถือ
            fig_pie.update_layout(
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1),
                margin=dict(t=10, b=10, l=10, r=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # **ล่าง: แนวโน้มระยะยาว (แสดงเป็นจุดเดียวในปัจจุบัน)**
            st.divider()
            st.subheader("📉 แนวโน้มความรุนแรงระยะยาว")
            
            df["month_name"] = df["created_at"].dt.month_name() # เช่น July
            df["year_str"] = df["created_at"].dt.year.astype(str) # เช่น 2026
            
            g1, g2 = st.columns(2)
            
            with g1:
                st.write("แนวโน้มรายเดือน")
                # ใช้ Scatter plot เพื่อให้โชว์เป็นจุดเดียวสำหรับเดือนล่าสุดที่มีข้อมูล
                monthly_avg = df.groupby(["month_name", "created_at"])["aggression_level"].mean().reset_index()
                # เลือกเอาแค่วันที่ล่าสุดที่มีข้อมูลมาโชว์
                latest_date_in_month = monthly_avg.loc[monthly_avg.groupby("month_name")["created_at"].idxmax()]

                fig_m = px.scatter(latest_date_in_month, x="month_name", y="aggression_level", size=[20]*len(latest_date_in_month),
                                    color_discrete_sequence=['#FF9800'])
                fig_m.update_layout(xaxis_title="เดือน", yaxis_title="ระดับเฉลี่ย")
                st.plotly_chart(fig_m, use_container_width=True)
                st.caption("*ปัจจุบันแสดงผลเป็นค่าเฉลี่ยของแต่ละเดือนที่มีข้อมูล")
                
            with g2:
                st.write("แนวโน้มภาพรวมปี 2026")
                # ใช้ Scatter plot เพื่อโชว์เป็นจุดเดียวสำหรับปี 2026
                yearly_data = df[df["created_at"].dt.year == 2026]
                avg_2026 = yearly_data["aggression_level"].mean()
                
                fig_y = px.scatter(x=["2026"], y=[avg_2026], size=[30],
                                  color_discrete_sequence=['#2196F3'])
                fig_y.update_layout(xaxis_title="ปี", yaxis_title="ระดับเฉลี่ย")
                fig_y.update_xaxes(type='category')
                st.plotly_chart(fig_y, use_container_width=True)
                st.caption("*ปัจจุบันแสดงผลเป็นค่าเฉลี่ยรวมของปี 2026")

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

st.divider()
# ปุ่มกลับ
if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")

