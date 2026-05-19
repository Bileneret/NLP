import streamlit as st
from google.api_core import exceptions
from schemas import FeedbackScorecard
from core import get_chat_session, get_feedback

st.set_page_config(page_title="AI Tech Interviewer", layout="wide")

st.title(":blue[AI Interviewer: Симулятор співбесіди]")

if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "interview_started" not in st.session_state:
    st.session_state.interview_started = False
if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = None

def reset_interview():
    st.session_state.chat_session = None
    st.session_state.interview_started = False
    st.session_state.interview_finished = False
    st.session_state.feedback_data = None

with st.sidebar:
    st.header(":violet[Налаштування]")
    
    role = st.selectbox("Посада:", ["Python Developer", "Data Scientist", "DevOps Engineer"], on_change=reset_interview)
    level = st.select_slider("Рівень:", options=["Junior", "Middle", "Senior"], on_change=reset_interview)
    
    st.markdown("---")
    is_demo_mode = st.checkbox("Enable Debug Logging", value=False, on_change=reset_interview)
    
    if st.button("Почати співбесіду", disabled=st.session_state.interview_started, use_container_width=True):
        try:
            st.session_state.chat_session = get_chat_session(role, level, is_demo=is_demo_mode)
            st.session_state.interview_started = True
            st.session_state.chat_session.send_message("Привіт. Я готовий до співбесіди. Задай перше питання.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

if st.session_state.interview_started and not st.session_state.interview_finished:
    for msg in st.session_state.chat_session.history[1:]:
        role_name = "Інтерв'юер" if msg.role == "model" else "Ви"
        with st.chat_message("assistant" if msg.role == "model" else "user"):
            if msg.role == "model":
                st.markdown(f"**:blue[{role_name}:]** {msg.parts[0].text}")
            else:
                st.markdown(f"**:green[{role_name}:]** {msg.parts[0].text}")

    user_input = st.chat_input("Ваша відповідь...")
    
    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("Завершити інтерв'ю", type="primary"):
            st.session_state.interview_finished = True
            st.rerun()

    if user_input:
        with st.chat_message("user"):
            st.markdown(f"**:green[Ви:]** {user_input}")
        
        with st.chat_message("assistant"):
            with st.spinner("Інтерв'юер аналізує..."):
                try:
                    response = st.session_state.chat_session.send_message(user_input)
                    st.markdown(f"**:blue[Інтерв'юер:]** {response.text}")
                    st.rerun()
                except exceptions.ResourceExhausted:
                    st.error("Помилка: Перевищено ліміти (Resource Exhausted).")
                except exceptions.InvalidArgument as e:
                    st.error(f"Помилка валідації (InvalidArgument): {e}")
                except Exception as e:
                    st.error(f"Помилка з'єднання: {e}")

if st.session_state.interview_finished:
    st.subheader(":violet[Финішний Scorecard кандидата]")
    
    if st.session_state.feedback_data is None:
        with st.spinner("Генерую аналітику (Structured JSON)..."):
            try:
                full_history = "\n".join([f"{m.role}: {m.parts[0].text}" for m in st.session_state.chat_session.history])
                st.session_state.feedback_data = get_feedback(full_history)
            except Exception as e:
                st.error(f"Не вдалося згенерувати фідбек: {e}")
                
    if st.session_state.feedback_data:
        feedback = st.session_state.feedback_data
        col1, col2 = st.columns(2)
        col1.metric("Технічні знання", f"{feedback['technical_score']}/10")
        col2.metric("Комунікація", f"{feedback['communication_score']}/10")
        
        st.markdown("### :green[Сильні сторони:]")
        for pt in feedback['strong_points']: st.markdown(f"- {pt}")
            
        st.markdown("### :orange[Зони для покращення:]")
        for pt in feedback['areas_for_improvement']: st.markdown(f"- {pt}")
            
        st.info(f"**Висновок:** {feedback['final_verdict']}")
        
        if st.button("Почати нову співбесіду", type="primary"):
            reset_interview()
            st.rerun()