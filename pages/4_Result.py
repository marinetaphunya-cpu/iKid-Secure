import streamlit as st

st.set_page_config(layout="wide", page_title="Result | iKid Secure")

# ดึงข้อมูลจากหน้า Evaluation
score = st.session_state.get("evaluation_score", 0)
details = st.session_state.get("evaluation_details", {})

st.title("📊 ผลการประเมิน OAS")

# 1. โชว์ผลการประเมิน
st.subheader(f"ระดับความรุนแรง: ระดับ {score}")
if score == 1:
    st.warning("ระดับ 1: กึ่งเร่งด่วน (Semi-urgency) - ต้องจัดการทันที")
elif score == 2:
    st.error("ระดับ 2: เร่งด่วน (Urgency) - ต้องจัดการทันที")
elif score == 3:
    st.error("🚨 ระดับ 3: ฉุกเฉิน (Emergency) - ต้องจัดการทันทีด้วยความระมัดระวังสูงสุด")
else:
    st.info("ไม่มีความเสี่ยง")

st.divider()

# 2. แนวทางปฏิบัติ (ชื่อเต็มตำแหน่ง)
# คำนิยามตำแหน่ง
pos = {
    "N1": "พยาบาลที่สัมภาษณ์ผู้ป่วย",
    "N2": "พยาบาลที่ออกใบผู้ป่วย",
    "N3": "พยาบาลที่ปฏิบัติงาน Day care",
    "Pn1": "ผู้ช่วยพยาบาล/พนักงานช่วยพยาบาล (OPD)",
    "Pn2/Pn3": "ผู้ช่วยพยาบาล/พนักงานช่วยพยาบาล (Day care)",
    "Med nurse": "พยาบาลให้ยา"
}

# ข้อมูลแนวทาง (แบ่งตาม Code)
guidelines = {
    1: {"name": "CODE 91", "color": "yellow"},
    2: {"name": "CODE 92", "color": "orange"},
    3: {"name": "CODE 93", "color": "red"}
}

if score in guidelines:
    st.subheader(f"🏥 แนวปฏิบัติ: {guidelines[score]['name']}")
    
    col_out, col_in = st.columns(2)
    
    with col_out:
        st.write("#### 📍 นอกห้องตรวจ")
        if score == 1:
            st.write("1. ผู้พบเห็นแจ้ง N2 สื่อสารกับทีม")
            st.write("2. N2 โทรแจ้งรปภ. (Tel. 5500, 8700) แจ้ง Code 91")
            st.write("3. N1 สื่อสารแพทย์ พิจารณาให้พบแพทย์ก่อน")
            st.write("4. N2 / Pn1 Zoning ผู้ป่วย")
            st.write("5. รปภ. อยู่กับแพทย์ในห้องตรวจ")
            st.write("6. N1 ดูแลผู้ป่วย Zone เขียว")
        elif score == 2:
            st.write("1. ผู้พบเห็นแจ้ง N2 สื่อสารกับทีม\n2. N2 โทรแจ้งรปภ. (Tel. 5500, 8700) แจ้ง Code 92\n3. N1 สื่อสารแพทย์ พิจารณาให้พบแพทย์ก่อน\n4. N2 / Pn1 Zoning ผู้ป่วย\n5. N3, Pn2 หรือ Pn3 เตรียมเตียงและผูกยึด\n6. N3 / Med nurse เตรียมยา, N1 ดูแลผู้ป่วย Zone เขียว")
        elif score == 3:
            st.write("1. ผู้พบเห็นแจ้ง N2 สื่อสารกับทีม\n2. N2 โทรแจ้งรปภ. (Tel. 5500, 8700) แจ้ง Code 93\n3. N1 สื่อสารแพทย์ พิจารณาให้พบแพทย์ก่อน\n4. N2 / Pn1 Zoning ผู้ป่วย\n5. N3, Pn2 หรือ Pn3 เตรียมเตียงและประสานรปภ.ช่วยผูกยึด\n6. N3 / Med nurse เตรียมและให้ยาตามแผนการรักษา\n7. Pn2 หรือ Pn3 วัด V/S ทุก 15 นาที\n8. N1 ดูแลผู้ป่วย Zone เขียว")

    with col_in:
        st.write("#### 🚪 ในห้องตรวจ")
        st.write("1. แพทย์กดออดสื่อสาร N2")
        st.write(f"2. N2 แจ้ง {guidelines[score]['name']}")
        st.write("3. N2 / Pn1 Zoning ผู้ป่วย")
        st.write("4. N2 บอก N1 โทรแจ้งรปภ. (Tel. 5500, 8700)")
        st.write("5. รปภ. อยู่กับแพทย์ในห้องตรวจ")
        if score > 1:
            st.write("6. N3, Pn2 หรือ Pn3 เตรียมเตียงและเครื่องผูกยึด")
            st.write("7. N3 / Med nurse เตรียมยา")
        else:
            st.write("6. N1 ดูแลผู้ป่วย Zone เขียว")

    st.info(f"**ตำแหน่งที่เกี่ยวข้อง:**\n" + "\n".join([f"- {k}: {v}" for k, v in pos.items()]))

# 3. ปุ่มนำทาง
st.divider()
if st.button("⬅️ กลับหน้าหลัก"):
    st.switch_page("pages/1_Dashboard.py")

