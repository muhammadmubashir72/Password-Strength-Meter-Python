import streamlit as st
import re
import random
from streamlit.components.v1 import html

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.get('dark_mode', False)

def get_emoji(status):
    return "✅" if status else "❌"

def get_strength_emoji(strength):
    emojis = ["😱", "😨", "😐", "😊", "💪"]
    return emojis[strength]

def generate_password():
    characters = {
        'lower': 'abcdefghijklmnopqrstuvwxyz',
        'upper': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'digits': '0123456789',
        'symbols': '!@#$%^&*(),.?":{}|<>'
    }
    password = [
        random.choice(characters['lower']),
        random.choice(characters['upper']),
        random.choice(characters['digits']),
        random.choice(characters['symbols'])
    ]
    password += random.choices(
        ''.join(characters.values()), 
        k=12
    )
    random.shuffle(password)
    return ''.join(password)

def password_strength(password):
    score = 0
    feedback = []
    
    length = len(password) >= 8
    score += 1 if length else 0
    uppercase = bool(re.search(r'[A-Z]', password))
    score += 1 if uppercase else 0
    lowercase = bool(re.search(r'[a-z]', password))
    score += 1 if lowercase else 0
    digit = bool(re.search(r'\d', password))
    score += 1 if digit else 0
    special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    score += 1 if special else 0
    
    return {
        'strength': min(score, 4),
        'length': length,
        'uppercase': uppercase,
        'lowercase': lowercase,
        'digit': digit,
        'special': special
    }

st.set_page_config(
    page_title="Password Power Meter",
    page_icon="🔒",
    layout="centered"
)

st.markdown(f"""
<style>
    .stApp {{
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
            url("https://github.com/muhammadmubashir72/Password-Strength-Meter-Python/blob/master/static/background.jpg?raw=true");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
    
    .st-emotion-cache-1y4p8pa {{
        background-color: rgba(255, 255, 255, 0.92) !important;
        border-radius: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(8px);
        margin: 2rem auto;
        max-width: 800px;
    }}
    
    [data-dark] .st-emotion-cache-1y4p8pa {{
        background-color: rgba(0, 0, 0, 0.85) !important;
    }}
    
    .stTextInput input {{
        background-color: #20120f !important;
        color: white !important;
                }}
    
    [data-dark] .stTextInput input {{
        background-color: rgba(0, 0, 0, 0.8) !important;
        color: white !important;
    }}
</style>
""", unsafe_allow_html=True)

def main():
    st.session_state.setdefault('dark_mode', False)
    
    html("""<button onclick="window.parent.document.querySelector('.stApp').toggleAttribute('data-dark');" 
            style="position:fixed;top:10px;right:10px;z-index:9999;background:rgba(255,255,255,0.8);border:none;border-radius:50%;width:40px;height:40px;font-size:20px;cursor:pointer;">
            🌓
        </button>""")
    
    with st.container():
        st.title("🔐 Password Power Meter")
        st.markdown("#### Type your password to check its strength! 💪")
    
    if st.button("✨ Generate Strong Password"):
        generated_pwd = generate_password()
        st.session_state.generated_password = generated_pwd
    
    if 'generated_password' in st.session_state:
        st.code(f"Generated Password: {st.session_state.generated_password}")
    
    password = st.text_input("", 
                           type="password", 
                           placeholder="Enter your password here... 🔑", 
                           value=st.session_state.get('generated_password', ''))
    
    if password:
        result = password_strength(password)
        
        strength = result['strength']
        progress = (strength + 1) * 20
        
        st.markdown(f"""
        <div style="height:15px; border-radius:10px; margin:10px 0;
            background: linear-gradient(90deg, 
            {"#ff0000" if strength < 2 else "#ffd700" if strength < 4 else "#00ff00"} {progress}%, 
            #e0e0e0 {progress}%);">
        </div>
        """, unsafe_allow_html=True)
        
        strength_messages = ["Very Weak! 😱", "Weak 😨", "Medium 😐", "Strong 😊", "Very Strong! 💪"]
        st.markdown(f'<div style="font-size:2.5rem; text-align:center; margin:1rem 0;">{get_strength_emoji(strength)} {strength_messages[strength]}</div>', unsafe_allow_html=True)
        
        with st.expander("📝 Improvement Tips"):
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"{get_emoji(result['length'])} At least 8 characters")
                st.markdown(f"{get_emoji(result['uppercase'])} Uppercase letters")
            with cols[1]:
                st.markdown(f"{get_emoji(result['digit'])} Numbers")
                st.markdown(f"{get_emoji(result['special'])} Special characters")
            
            st.markdown("---\n**Strong passwords should:**\n"
                       "- Be at least 12 characters\n"
                       "- Mix character types\n"
                       "- Avoid personal info\n"
                       "- Use password managers 🔒")
    else:
        st.info("👆 Click above box to enter your password!")

if __name__ == "__main__":
    main()
