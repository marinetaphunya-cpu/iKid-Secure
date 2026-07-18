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
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        df["incident_count"] = df["incident_count"].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        # กำหนดสีพฤติกรรมให้คงที่
        behavior_colors = {
            "ไม่มีพฤติกรรมก้าวร้าวต่อผู้อื่น": "#2196F3", # ฟ้า
            "พูดจาตะคอกเสียงดัง": "#F44336",          # แดง
            "ขว้างปาสิ่งของ": "#FF9800",             # ส้ม
            "ระดับ 2: ด่าคำหยาบคาย แสดงท่าทางคุกคาม": "#9C27B0" # ม่วง
        }

        # KPI
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสรวม", int(len(df)))
        c2.metric("ระดับสูงสุด", int(df["aggression_level"].max()))
        c3.metric("รวมจำนวนครั้ง", int(df["incident_count"].sum()))
        st.divider()

        # กราฟบน
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.subheader("📈 จำนวนเคสตามระดับ")
            bar_df = df.groupby("aggression_level")["incident_count"].sum().reset_index()
            fig_bar = px.bar(bar_df, x="aggression_level", y="incident_count", color="aggression_level",
                             color_continuous_scale=["#FFEB3B", "#FF9800", "#F44336"])
            fig_bar.update_layout(xaxis_title="ระดับความรุนแรง", yaxis_title="จำนวนครั้ง", coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.caption("เหลือง: ระดับ 1 | ส้ม: ระดับ 2 | แดง: ระดับ 3")

        with col2:
            st.subheader("📊 สัดส่วนพฤติกรรม (OSA)")
            pie_df = df.groupby("behavior_note")["incident_count"].sum().reset_index()
            # ใช้ color_discrete_map เพื่อล็อคสีให้ตรงกับพฤติกรรม
            fig_pie = px.pie(pie_df, names="behavior_note", values="incident_count", 
                             color="behavior_note", color_discrete_map=behavior_colors, hole=0.4)
            fig_pie.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1))
            st.plotly_chart(fig_pie, use_container_width=True)

        # กราฟล่าง
        st.divider()
        st.subheader("📉 แนวโน้มระยะยาว")
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
            avg_val = [df[df["created_at"].dt.year == 2026]["aggression_level"].mean()]
            fig_y = px.scatter(x=["2026"], y=avg_val, size=[20])
            fig_y.update_xaxes(type='category')
            fig_y.update_layout(xaxis_title="ปี", yaxis_title="ระดับเฉลี่ย")
            st.plotly_chart(fig_y, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูล ✨")
except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")


