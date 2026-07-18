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
    # 3. ดึงข้อมูล
    response = supabase.table("assessments").select("*").execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # --- Clean ข้อมูล ---
        df["created_at"] = pd.to_datetime(df["created_at"], errors='coerce')
        df["aggression_level"] = df["aggression_level"].astype(str).str.extract('(\d+)').astype(float).fillna(0)
        df["incident_count"] = df["incident_count"].astype(str).str.extract('(\d+)').astype(float).fillna(0)

        # --- ข้อมูลสำหรับทำสถิติ (แปลงให้เป็นตัวเลข) ---
        total_incidents = df["incident_count"].sum()
        max_level = int(df["aggression_level"].max())
        avg_level = round(df["aggression_level"].mean(), 1)

        # --- 4. ส่วนแสดง KPI ---
        c1, c2, c3 = st.columns(3)
        c1.metric("จำนวนเคสรวม", int(len(df)))
        c2.metric("ระดับสูงสุด", max_level)
        c3.metric("รวมจำนวนครั้ง", int(total_incidents))
        st.divider()

        # --- 5. แสดงกราฟ (จัดเรียงใหม่) ---
        
        # **บน: กราฟแท่ง (Bar Chart) - ปรับสีตามระดับ OAS**
        st.subheader("📈 จำนวนครั้งตามระดับความรุนแรง (OAS)")
        bar_df = df.groupby("aggression_level")["incident_count"].sum().reset_index()
        # สี Gradient เขียว -> เหลือง -> ส้ม -> แดง
        fig_bar = px.bar(bar_df, x="aggression_level", y="incident_count", 
                         color="aggression_level",
                         color_continuous_scale=["#2196F3", "#FFEB3B", "#FF9800", "#F44336"])
        fig_bar.update_layout(xaxis_title="ระดับความรุนแรง (OAS)", yaxis_title="จำนวนครั้ง", coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        # **Legend แบบสี่เหลี่ยมเล็กๆ สำหรับ Bar Chart**
        st.caption("🟢 ระดับ 0 | 🟡 ระดับ 1 | 🟠 ระดับ 2 | 🔴 ระดับ 3")

        # **ล่าง: แผนภูมิวงกลม (Pie Chart) - ย่อคำอธิบายพฤติกรรม**
        st.divider()
        st.subheader("📊 สัดส่วนพฤติกรรมที่พบมากที่สุด (OSA)")
        
        # ย่อคำอธิบายพฤติกรรมให้กระชับ
        short_behavior_map = {
            "ระดับ 2: ด่าคำหยาบคาย แสดงท่าทางคุกคาม เช่น ถลกเสื้อผ้า ทำท่าต่อย ลม หรือกระชากคอเสื้อ ผู้อื่น พ่น เตะ ผลัก หรือดึงผมผู้อื่นแต่ไม่ได้รับบาดเจ็บ": "ด่าหยาบ แสดงท่าทางคุกคาม",
            "ไม่มีพฤติกรรมก้าวร้าวต่อผู้อื่น": "ไม่มีพฤติกรรมรุนแรง",
            "ขว้างปาสิ่งของ": "ขว้างปาสิ่งของ",
            "พูดจาตะคอกเสียงดัง": "ตะคอกเสียงดัง",
             # เพิ่มกรณีอื่นๆ ที่อาจพบ
            "ทำร้ายตนเองรุนแรง เช่น มีรอยช้ำ มีรอยกรีดลึก เลือดออก หรือมีการบาดเจ็บอวัยวะ ภายใน หรือหมดสติ ฯลฯ": "ทำร้ายตนเองรุนแรง",
            "ขีดข่วนผิวหนัง ตีตนเอง ดึงผม โขกศีรษะตัวเอง เป็นรอยขนาดเล็ก": "ขีดข่วน ตีตนเอง",
             "พูดข่มขู่จะทำร้ายผู้อื่นชัดเจน เช่น ฉันจะฆ่าแก ฯลฯ": "พูดข่มขู่",
            "ทำร้ายผู้อื่นจนได้รับบาดเจ็บ เช่น ช้ำ เคล็ด บวม เกิด บาดแผล กระดูกหัก หรือเกิดการบาดเจ็บ ของอวัยวะภายใน หรือ หมดสติ ฯลฯ": "ทำร้ายผู้อื่น บาดเจ็บ",
            "ทำสิ่งของแตกหัก กระจัดกระจาย เช่น ทุบ กระจก ขว้างแก้ว จาน มีด หรือสิ่งของที่เป็น อันตราย หรือจุดไฟเผา ฯลฯ": "ทำลายทรัพย์สิน",
            "ขว้าง เตะ ทุบวัตถุ หรือสิ่งของ": "ขว้าง เตะ สิ่งของ",
            "ปิดประตูเสียงดัง รื้อ ข้าวของกระจัดกระจาย": "ปิดประตูเสียงดัง รื้อข้าวของ"
        }
        
        pie_df = df.groupby("behavior_note")["incident_count"].sum().reset_index()
        # แทนที่ชื่อยาวด้วยชื่อย่อ
        pie_df["behavior_short"] = pie_df["behavior_note"].map(short_behavior_map).fillna(pie_df["behavior_note"])

        fig_pie = px.pie(pie_df, names="behavior_short", values="incident_count", hole=0.4)
        # ย้าย Legend ไปด้านข้างเพื่อให้เห็นชัด
        fig_pie.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1))
        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.info("ยังไม่มีข้อมูลการประเมินในระบบ ✨")

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")

st.divider()
# ปุ่มกลับ
if st.button("⬅️ กลับหน้า Dashboard", use_container_width=True):
    st.switch_page("pages/1_Dashboard.py")


