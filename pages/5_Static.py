import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# 1. ตั้งค่าหน้าเพจ
st.set_page_config(layout="wide", page_title="iKid Secure | Statistics")
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    st.warning("กรุณาเข้าสู่ระบบก่อน! 🐈‍⬛")
    st.switch_page("app.py")

# 2. เชื่อมต่อ Supabase
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# **จุดสำคัญ 1: กำหนดสีมาตรฐานสำหรับ 3 ระดับ (ใช้ key เป็น string "1","2","3")**
LEVEL_COLORS = {"1": "#FFEB3B", "2": "#FF9800", "3": "#F44336"}  # เหลือง, ส้ม, แดง
LEVEL_ORDER = ["1", "2", "3"]

# **จุดสำคัญ 2: เปลี่ยนจุดสี Legend ในเชิงสถิติให้เป็นสี่เหลี่ยม**
st.markdown(
    """
    <style>
    .legend-item rect {
        rx: 0 !important;
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
    st.title("📊 สถิติภาพรวม ✨")
with col_title2:
    pass
st.markdown("---")

try:
    # 3. ดึงข้อมูลจาก Supabase
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # --- ส่วน Clean ข้อมูล ---
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df = df.dropna(subset=['created_at'])

        df["aggression_level"] = df["aggression_level"].astype(str).str.extract(r'(\d+)').astype(float)
        df["incident_count"] = df["incident_count"].astype(str).str.extract(r'(\d+)').astype(float).fillna(1.0)

        df_filtered = df[df["aggression_level"].isin([1.0, 2.0, 3.0])].copy()

        # **แปลง aggression_level เป็น string ตั้งแต่ต้น เพื่อให้ Plotly ใช้สีแบบ discrete ตาม color_discrete_map**
        df_filtered["level_str"] = df_filtered["aggression_level"].astype(int).astype(str)

        if df_filtered.empty:
            st.info("ยังไม่มีข้อมูลการประเมินระดับ 1-3 ในระบบ ✨")
        else:
            # --- ส่วนแสดง KPI ---
            total_cases = int(len(df_filtered))
            max_level = int(df_filtered["aggression_level"].max())
            

            c1, c2, c3 = st.columns(3)
            c1.metric("จำนวนเคสรวม (Lv.1-3)", total_cases)
            c2.metric("ระดับความรุนแรงสูงสุด", max_level)
            

            st.divider()

            # --- 5. แสดงกราฟ ---

            # **1. กราฟแท่ง (Bar Chart)**
            st.subheader("📈 จำนวนครั้งตามระดับความรุนแรง (OAS) 📋")
            bar_df = df_filtered.groupby("level_str")["incident_count"].sum().reindex(LEVEL_ORDER, fill_value=0).reset_index()

            fig_bar = px.bar(
                bar_df, x="level_str", y="incident_count",
                color="level_str",
                category_orders={"level_str": LEVEL_ORDER},
                color_discrete_map=LEVEL_COLORS
            )

            fig_bar.update_layout(xaxis_title="ระดับความรุนแรง (OAS)", yaxis_title="จำนวนครั้ง")
            fig_bar.update_xaxes(type='category')
            fig_bar.update_traces(showlegend=True, legendgroup="level")
            st.plotly_chart(fig_bar, use_container_width=True)

            # **2. แนวโน้มระยะยาว**
            st.divider()
            st.subheader("📉 แนวโน้มความรุนแรงระยะยาว 📈")

            df_filtered["month_name"] = df_filtered["created_at"].dt.month_name()
            df_filtered["year_str"] = df_filtered["created_at"].dt.year.astype(int).astype(str)

            g1, g2 = st.columns(2)

            with g1:
                st.write("แนวโน้มรายเดือน")
                monthly_trend = df_filtered.groupby(["month_name", "level_str"])["incident_count"].sum().reset_index()

                fig_m = px.scatter(
                    monthly_trend, x="month_name", y="incident_count",
                    color="level_str",
                    category_orders={"level_str": LEVEL_ORDER},
                    color_discrete_map=LEVEL_COLORS,
                    size_max=20
                )

                fig_m.update_layout(xaxis_title="เดือน", yaxis_title="จำนวนครั้ง")
                # **แก้ไขแกน Y ให้เพิ่มทีละ 2 (ต้องระบุ tickmode="linear" ด้วย ไม่งั้น dtick จะถูกมองข้าม)**
                fig_m.update_yaxes(tickmode="linear", tick0=0, dtick=2, rangemode="tozero")
                fig_m.update(layout_showlegend=False)
                st.plotly_chart(fig_m, use_container_width=True)
                st.caption("*ความสูงของจุดบนแกน Y แสดงจำนวนครั้งที่เกิดเหตุในระดับนั้นๆ ในแต่ละเดือน")

            with g2:
                st.write("แนวโน้มรายปี")
                yearly_trend = df_filtered.groupby(["year_str", "level_str"])["incident_count"].sum().reset_index()

                fig_y = px.scatter(
                    yearly_trend, x="year_str", y="incident_count",
                    color="level_str",
                    category_orders={"ระดับความรุนแรง": LEVEL_ORDER},
                    color_discrete_map=LEVEL_COLORS,
                    size_max=20
                )

                fig_y.update_layout(xaxis_title="ปี (Year)", yaxis_title="จำนวนครั้ง")
                # **แก้ไขแกน Y ให้เพิ่มทีละ 5**
                fig_y.update_yaxes(tickmode="linear", tick0=0, dtick=5, rangemode="tozero")
                fig_y.update_xaxes(type='category')
                fig_y.update(layout_showlegend=False)
                st.plotly_chart(fig_y, use_container_width=True)
                st.caption("*ความสูงของจุดบนแกน Y แสดงจำนวนครั้งที่เกิดเหตุในระดับนั้นๆ ในแต่ละปี")

            # **Legend รวมอธิบายความหมายของสีแบบสี่เหลี่ยม**
            st.divider()
            st.markdown("ความหมายของสีตามระดับความรุนแรง")

            st.markdown(
                f"""
                <div style="display: flex; gap: 20px; justify-content: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: {LEVEL_COLORS["1"]}; border-radius: 0px;"></div>
                        <span>ระดับ 1 : กึ่งเร่งด่วน</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: {LEVEL_COLORS["2"]}; border-radius: 0px;"></div>
                        <span>ระดับ 2 : เร่งด่วน</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <div style="width: 14px; height: 14px; background-color: {LEVEL_COLORS["3"]}; border-radius: 0px;"></div>
                        <span>ระดับ 3 : ฉุกเฉิน</span>
                    </div>
                </div>
                <br>
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



