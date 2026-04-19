import streamlit as st
import anthropic

SYSTEM_PROMPT = """Kamu adalah Personal Consultant profesional sekelas $500 per jam.

Kamu dibayar mahal karena ketajaman analisis, kejujuran brutal, dan hasil nyata — bukan karena basa-basi.

GAYA & SIKAP:
- Bicara langsung, lugas, rasional, dan tanpa mempermanis kata
- Berani menantang asumsi bodoh, bias, dan titik buta klien
- Jika ide klien lemah, katakan lemah dan jelaskan kenapa dengan spesifik
- Tidak mencari aman, tidak menyenangkan ego
- Fokus pada solusi, dampak, dan efisiensi waktu

CARA KERJA:
- Ajukan pertanyaan strategis jika diperlukan, bukan pertanyaan receh
- Pecah masalah kompleks menjadi langkah konkret dan bisa dieksekusi
- Prioritaskan hasil nyata di atas teori panjang
- Asumsikan waktu klien mahal — jawaban harus padat, tajam, bernilai tinggi

STANDAR JAWABAN:
- Tidak mengulang penjelasan umum yang sudah jelas
- Tidak memberi jawaban setengah matang
- Selalu jelaskan KENAPA dan APA DAMPAKNYA
- Jika ada trade-off, sebutkan secara eksplisit

BAHASA:
- Gunakan Bahasa Indonesia baku, tegas, profesional
- Humor singkat dan tajam boleh jika relevan
- Tidak bertele-tele, tidak pakai basa-basi pembuka

KONTRAK TAK TERTULIS:
Perlakukan setiap pertanyaan seolah dari klien korporat yang membayar mahal dan menuntut hasil nyata."""

st.set_page_config(
    page_title="Personal Consultant AI",
    page_icon="💼",
    layout="centered",
)

st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 1rem;
    }
    .rate-badge {
        background: #1a1a2e;
        color: #ffd700;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .stChatMessage {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💼 Personal Consultant AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Analisis tajam. Jawaban jujur. Hasil nyata. '
    '<span class="rate-badge">$500/jam</span></div>',
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "client" not in st.session_state:
    st.session_state.client = anthropic.Anthropic()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.messages:
    with st.chat_message("assistant"):
        opening = (
            "Apa yang ingin Anda selesaikan hari ini? "
            "Langsung ke intinya — saya tidak dibayar untuk small talk."
        )
        st.markdown(opening)

prompt = st.chat_input("Sampaikan masalah atau pertanyaan Anda...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_messages = []
    for i, msg in enumerate(st.session_state.messages):
        content = msg["content"]
        # Add cache_control to the last user turn for prompt caching
        if msg["role"] == "user" and i == len(st.session_state.messages) - 1:
            api_messages.append({
                "role": "user",
                "content": [{"type": "text", "text": content}],
            })
        else:
            api_messages.append({"role": msg["role"], "content": content})

    with st.chat_message("assistant"):
        with st.spinner("Menganalisis..."):
            response = st.session_state.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                messages=api_messages,
            )
            reply = response.content[0].text
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

with st.sidebar:
    st.markdown("### Sesi Konsultasi")
    msg_count = len(st.session_state.messages)
    st.metric("Pesan", msg_count)

    if msg_count > 0:
        if st.button("Mulai Sesi Baru", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    st.markdown(
        "<small>Powered by Claude Sonnet 4.6<br>"
        "Persona: High-Stakes Consultant</small>",
        unsafe_allow_html=True,
    )
