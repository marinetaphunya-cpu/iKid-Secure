import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py")

@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# สีมาตรฐาน
LEVEL_COLORS = {"1": "#FFEB3B", "2": "#FF9800", "3": "#F44336"}
LEVEL_ORDER = ["1", "2", "3"]

st.title("📊 สถิติภาพรวม ✨")
st.markdown("---")

try:
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df = df.dropna(subset=['created_at'])
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract(r'(\d+)').astype(float)
        df["incident_count"] = df["incident_count"].astype(str).str.extract(r'(\d+)').astype(float).fillna(1.0)
        df_filtered = df[df["aggression_level"].isin([1.0, 2.0, 3.0])].copy()
        df_filtered["level_str"] = df_filtered["aggression_level"].astype(int).astype(str)

        if df_filtered.empty:
            st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")
        else:
            # KPI ด้านบน
            c1, c2, c3 = st.columns(3)
            c1.metric("จำนวนเคสรวม (Lv.1-3)", int(len(df_filtered)))
            c2.metric("ระดับความรุนแรงสูงสุด", int(df_filtered["aggression_level"].max()))
            st.divider()

            # กราฟแท่ง (Bar Chart) อย่างเดียว
            st.subheader("📈 จำนวนครั้งตามระดับความรุนแรง (OAS) 📋")
            bar_df = df_filtered.groupby("level_str")["incident_count"].sum().reindex(LEVEL_ORDER, fill_value=0).reset_index()

            fig_bar = px.bar(
                bar_df, x="level_str", y="incident_count",
                color="level_str",
                category_orders={"level_str": LEVEL_ORDER},
                color_discrete_map=LEVEL_COLORS
            )
            fig_bar.update_layout(xaxis_title="ระดับความรุนแรง (OAS)", yaxis_title="จำนวนครั้ง", showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

            # Legend ด้านล่าง
            st.divider()
            st.markdown("ความหมายของสีตามระดับความรุนแรง")
            st.markdown(
                f"""
                <div style="display: flex; gap: 20px; justify-content: center; margin-top: 10px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: {LEVEL_COLORS["1"]};"></div>
                        <span>ระดับ 1 : กึ่งเร่งด่วน</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: {LEVEL_COLORS["2"]};"></div>
                        <span>ระดับ 2 : เร่งด่วน</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: {LEVEL_COLORS["3"]};"></div>
                        <span>ระดับ 3 : ฉุกเฉิน</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

st.divider()
if st.button("⬅️ กลับหน้า Dashboard 🏡", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")



