import streamlit as st
import home
import recommendation

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Book Recommendations"])

    if page == "Home":
        home.show_home()
    elif page == "Book Recommendations":
        recommendation.show_recommendation()

if __name__ == "__main__":
    main()
