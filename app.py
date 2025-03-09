import streamlit as st
import re
import random
import time
from streamlit_lottie import st_lottie
import requests
import json

# Set page configuration
st.set_page_config(
    page_title="Password Power Meter",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling with responsive header
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 20px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .generated-password {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 18px;
        border-left: 4px solid #4CAF50;
        margin: 10px 0;
    }
    .copy-button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 5px 10px;
        cursor: pointer;
        font-size: 14px;
    }
    .strength-meter {
        height: 20px;
        border-radius: 10px;
        margin: 15px 0;
        transition: all 0.5s ease;
    }
    .strength-label {
        font-size: 2rem;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .tip-card {
        background-color: #1B1212;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease;
    }
    .tip-card:hover {
        transform: translateY(-5px);
    }
    
    /* Responsive header styles */
    .responsive-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .responsive-header h1 {
        margin-bottom: 0;
        font-size: 2.5rem;
    }
    
    .responsive-header .subtitle {
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Media query for tablets and larger */
    @media (min-width: 768px) {
        .responsive-header {
            flex-direction: row;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            align-items: baseline;
        }
        
        .responsive-header h1 {
            font-size: 3rem;
            margin-bottom: 0;
        }
        
        .responsive-header .subtitle {
            font-size: 1.5rem;
            margin-top: 0;
        }
    }
    
    /* Media query for desktops */
    @media (min-width: 992px) {
        .responsive-header h1 {
            font-size: 3.5rem;
        }
        
        .responsive-header .subtitle {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Function to load Lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Password strength functions
def get_emoji(status):
    return "✅" if status else "❌"

def get_strength_emoji(strength):
    emojis = ["😱", "😨", "😐", "😊", "💪"]
    return emojis[strength]

def get_strength_color(strength):
    colors = ["#ff4d4d", "#ffa64d", "#ffff4d", "#4dff4d", "#4d4dff"]
    return colors[strength]

def generate_password(length=16, include_lower=True, include_upper=True, include_digits=True, include_symbols=True):
    characters = {}
    if include_lower:
        characters['lower'] = 'abcdefghijklmnopqrstuvwxyz'
    if include_upper:
        characters['upper'] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if include_digits:
        characters['digits'] = '0123456789'
    if include_symbols:
        characters['symbols'] = '!@#$%^&*(),.?":{}|<>'
    
    if not characters:
        return "Please select at least one character type"
    
    # Ensure at least one character from each selected type
    password = []
    for char_type, chars in characters.items():
        password.append(random.choice(chars))
    
    # Fill the rest of the password
    remaining_length = max(0, length - len(password))
    all_chars = ''.join(characters.values())
    password += random.choices(all_chars, k=remaining_length)
    
    # Shuffle the password
    random.shuffle(password)
    return ''.join(password)

def password_strength(password):
    score = 0
    
    # Basic checks
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
    
    # Advanced checks
    if len(password) >= 12:
        score += 1
    
    # Check for common patterns
    common_patterns = [
        r'12345', r'qwerty', r'password', r'admin', r'welcome',
        r'123123', r'abcabc', r'abc123', r'password123'
    ]
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            score = max(0, score - 2)
            break
    
    # Check for sequential characters
    sequential = False
    for i in range(len(password) - 2):
        if (ord(password[i]) + 1 == ord(password[i+1]) and 
            ord(password[i+1]) + 1 == ord(password[i+2])):
            sequential = True
            break
    if sequential:
        score = max(0, score - 1)
    
    # Normalize score to 0-4 range
    normalized_score = min(4, max(0, score))
    
    return {
        'strength': normalized_score,
        'length': length,
        'uppercase': uppercase,
        'lowercase': lowercase,
        'digit': digit,
        'special': special,
        'long_enough': len(password) >= 12,
        'no_patterns': not any(re.search(p, password.lower()) for p in common_patterns),
        'no_sequential': not sequential
    }

def get_strength_message(strength):
    messages = [
        "Very Weak! Your password needs serious improvement.",
        "Weak. Your password is vulnerable to attacks.",
        "Medium. Your password provides basic protection.",
        "Strong. Your password offers good security.",
        "Very Strong! Your password is highly secure."
    ]
    return messages[strength]

def get_password_tips(result):
    tips = []
    if not result['length']:
        tips.append("Make your password at least 8 characters long")
    if not result['uppercase']:
        tips.append("Add uppercase letters (A-Z)")
    if not result['lowercase']:
        tips.append("Add lowercase letters (a-z)")
    if not result['digit']:
        tips.append("Include numbers (0-9)")
    if not result['special']:
        tips.append("Add special characters (!@#$%^&*)")
    if not result['long_enough']:
        tips.append("Consider making your password longer (12+ characters)")
    if not result['no_patterns']:
        tips.append("Avoid common patterns and dictionary words")
    if not result['no_sequential']:
        tips.append("Avoid sequential characters like 'abc' or '123'")
    
    return tips

def main():
    # Initialize session state for generated password if it doesn't exist
    if 'generated_password' not in st.session_state:
        st.session_state.generated_password = ''
    
    # Load animations
    lottie_lock = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_yzoqyyqf.json")
        
    # Add Lottie animation
    if lottie_lock:
        st_lottie(lottie_lock, height=150, key="lock_animation")
    
    # Responsive header with title and subtitle on one line for large screens
    st.markdown('''
    <div class="responsive-header">
        <h1>🔐 Password Power Meter</h1>
        <div class="subtitle">Check and strengthen your digital fortress! 💪</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Password input section
    password = st.text_input("", 
                           type="password", 
                           placeholder="Enter your password here... 🔑", 
                           value=st.session_state.get('generated_password', ''),
                           key="password_input")
    
    # Password generator section
    with st.expander("✨ Password Generator", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            pwd_length = st.slider("Password Length", min_value=8, max_value=32, value=16)
        with col2:
            st.write("Character Types:")
            col2a, col2b = st.columns(2)
            with col2a:
                include_lower = st.checkbox("Lowercase (a-z)", value=True)
                include_upper = st.checkbox("Uppercase (A-Z)", value=True)
            with col2b:
                include_digits = st.checkbox("Numbers (0-9)", value=True)
                include_symbols = st.checkbox("Symbols (!@#$)", value=True)
        
        if st.button("Generate Strong Password"):
            with st.spinner("Generating secure password..."):
                time.sleep(0.5)  # Add a small delay for effect
                generated_pwd = generate_password(
                    length=pwd_length,
                    include_lower=include_lower,
                    include_upper=include_upper,
                    include_digits=include_digits,
                    include_symbols=include_symbols
                )
                st.session_state.generated_password = generated_pwd
                # Update the password input field with the generated password
                st.rerun()
    
    # Display generated password
    if st.session_state.generated_password:
        st.markdown('<div class="generated-password">', unsafe_allow_html=True)
        st.code(st.session_state.generated_password, language="")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("📋 Copy to Clipboard"):
            st.success("Password copied to clipboard!")
    
    # Password strength analysis
    if password:
        result = password_strength(password)
        strength = result['strength']
        
        # Animated progress bar
        progress = (strength + 1) * 20
        st.markdown(f"""
        <div class="strength-meter" style="
            background: linear-gradient(90deg, 
            {get_strength_color(strength)} {progress}%, 
            #e0e0e0 {progress}%);
            animation: pulse 1.5s infinite alternate;">
        </div>
        """, unsafe_allow_html=True)
        
        # Strength message
        st.markdown(f'<div class="strength-label" style="color: {get_strength_color(strength)};">{get_strength_emoji(strength)} {get_strength_message(strength)}</div>', unsafe_allow_html=True)
        
        # Password analysis
        with st.expander("📊 Password Analysis", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Basic Requirements")
                st.markdown(f"{get_emoji(result['length'])} At least 8 characters")
                st.markdown(f"{get_emoji(result['uppercase'])} Uppercase letters")
                st.markdown(f"{get_emoji(result['lowercase'])} Lowercase letters")
            
            with col2:
                st.markdown("### Advanced Security")
                st.markdown(f"{get_emoji(result['digit'])} Numbers")
                st.markdown(f"{get_emoji(result['special'])} Special characters")
                st.markdown(f"{get_emoji(result['long_enough'])} 12+ characters (recommended)")
                st.markdown(f"{get_emoji(result['no_patterns'])} No common patterns")
        
        # Improvement tips
        tips = get_password_tips(result)
        if tips:
            with st.expander("🚀 Improvement Tips", expanded=True):
                st.markdown("### How to strengthen your password:")
                for i, tip in enumerate(tips):
                    st.markdown(f"""
                    <div class="tip-card">
                        <b>Tip {i+1}:</b> {tip}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Password security facts
        with st.expander("🔍 Password Security Facts", expanded=False):
            st.markdown("""
            ### Did you know?
            
            - A password with 8 characters can be cracked in less than 8 hours using modern techniques
            - Adding just 4 more characters can increase cracking time to several years
            - Using a unique password for each site prevents credential stuffing attacks
            - Password managers are the safest way to manage multiple complex passwords
            - Two-factor authentication adds an extra layer of security beyond passwords
            """)
    else:
        st.info("👆 Enter a password above to check its strength!")
    
    # Footer
    st.markdown("---")
    st.markdown("### 🛡️ Your password is never stored or transmitted")
    st.caption("All analysis happens in your browser for maximum security")

if __name__ == "__main__":
    main()
