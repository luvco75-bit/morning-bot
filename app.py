import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from news_crawler import fetch_all_categories
from telegram_sender import send_to_telegram
import pandas as pd

# 인증 설정 로드
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

# 로그인 / 회원가입 탭
if not st.session_state.get("authentication_status"):
    st.title("🤖 자비스 모닝봇")
    login_tab, register_tab = st.tabs(["로그인", "회원가입"])

    with login_tab:
        authenticator.login(
            location="main",
            fields={"Form name": "로그인", "Username": "아이디", "Password": "비밀번호", "Login": "로그인"}
        )

    with register_tab:
        try:
            email, username, name = authenticator.register_user(
                location="main",
                pre_authorized=config.get('pre-authorized', {}).get('emails', []),
                fields={"Form name": "회원가입", "Name": "이름", "Email": "이메일",
                         "Username": "아이디", "Password": "비밀번호",
                         "Repeat password": "비밀번호 확인", "Register": "가입하기"}
            )
            if email:
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
                st.success("회원가입이 완료되었습니다! 로그인 탭에서 로그인해 주세요.")
        except Exception as e:
            st.error(f"{e}")

if st.session_state.get("authentication_status") is False:
    st.error("아이디 또는 비밀번호가 틀렸습니다.")
elif st.session_state.get("authentication_status"):
    authenticator.logout("로그아웃", "sidebar")
    st.sidebar.write(f"👋 안녕하세요, **{st.session_state['name']}**님!")

    st.title("🤖 자비스 모닝봇")
    st.success("반갑습니다, 좌측 관심 키워드 설정을 통해 원하시는 키워드를 입력하시면 관련 뉴스를 받아보실 수 있습니다.")

    st.sidebar.header("🔍 관심 키워드 설정")
    default_kw = "삼성전자, SK하이닉스, HBM, K-pop"

    # 저장된 키워드 불러오기
    saved_key = f"saved_keywords_{st.session_state['username']}"
    if saved_key not in st.session_state:
        st.session_state[saved_key] = default_kw

    user_keywords = st.sidebar.text_area(
        "쉼표(,)로 구분해서 입력해 주세요",
        st.session_state[saved_key],
        height=200
    )
    kw_list = [k.strip() for k in user_keywords.split(",") if k.strip()]

    if st.sidebar.button("키워드 저장"):
        st.session_state[saved_key] = user_keywords
        st.sidebar.success("키워드가 저장되었습니다!")

    if st.button("지금 뉴스 수집하기"):
        with st.spinner('실시간 뉴스를 수집 중입니다...'):
            news_data = fetch_all_categories(kw_list)

            flattened_news = []
            for category, items in news_data.items():
                for item in items:
                    flattened_news.append({"카테고리": category, "제목": item['title'], "링크": item['link']})

            if flattened_news:
                st.session_state['news_results'] = flattened_news
                st.table(pd.DataFrame(flattened_news))
            else:
                st.warning("수집된 뉴스가 없습니다.")

    if 'news_results' in st.session_state:
        if st.button("확인 후 텔레그램으로 전송"):
            status = send_to_telegram(st.session_state['news_results'])
            if status:
                st.success("텔레그램 전송 완료! 📱")
            else:
                st.error("전송 실패! 스트림릿 Secrets 설정을 확인해 주세요.")
