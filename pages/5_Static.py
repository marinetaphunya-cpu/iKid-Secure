import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

st.title("📊 สถิติภาพรวม")
st.markdown("---")

try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Clean ข้อมูล
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        df["incident_count"] = df["incident_count"].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        # KPI
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสรวม", int(len(df)))
        c2.metric("ระดับสูงสุดที่พบ", int(df["aggression_level"].max()))
        c3.metric("รวมจำนวนครั้งที่เกิด", int(df["incident_count"].sum()))
        st.divider()

        # กราฟบน
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.subheader("📈 จำนวนครั้งตามระดับ")
            bar_df = df.groupby("aggression_level")["incident_count"].sum().reset_index()
            # ใช้ชุดสี เหลือง -> ส้ม -> แดง
            fig_bar = px.bar(bar_df, x="aggression_level", y="incident_count", color="aggression_level", 
                             color_continuous_scale=["#FFEB3B", "#FF9800", "#F44336"])
            fig_bar.update_layout(coloraxis_showscale=False) # ซ่อนแถบสีข้างๆ ให้ดูสะอาดตา
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col2:
            st.subheader("📊 สัดส่วนพฤติกรรม (OSA)")
            pie_df = df.groupby("behavior_note")["incident_count"].sum().reset_index()
            fig_pie = px.pie(pie_df, names="behavior_note", values="incident_count", hole=0.4)
            # ย้าย Legend ไปไว้ด้านล่าง เพื่อแก้ปัญหาตัวหนังสือตกขอบ
            fig_pie.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_pie, use_container_width=True)

        # กราฟล่าง: แนวโน้ม
        st.divider()
        st.subheader("📉 แนวโน้มความรุนแรงระยะยาว")
        df["month_year"] = df["created_at"].dt.strftime('%b %Y')
        
        g1, g2 = st.columns(2)
        with g1:
            st.write("แนวโน้มรายเดือน")
            monthly = df.groupby("month_year")["aggression_level"].mean().reset_index()
            fig_m = px.line(monthly, x="month_year", y="aggression_level", markers=True)
            fig_m.update_traces(line_color='#FF9800')
            st.plotly_chart(fig_m, use_container_width=True)
        with g2:
            st.write("แนวโน้มภาพรวมปี 2026")
            # กรองเอาแค่ปี 2026 มาโชว์
            yearly_data = df[df["created_at"].dt.year == 2026]
            # ให้โชว์แค่จุดเดียว หรือค่าเฉลี่ยของปีนั้น
            fig_y = px.scatter(x=["2026"], y=[yearly_data["aggression_level"].mean()], size=[20])
            fig_y.update_layout(xaxis_title="Year", yaxis_title="Average Level")
            st.plotly_chart(fig_y, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")


