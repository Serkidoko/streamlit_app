import streamlit as st
import os
import base64
from datetime import datetime
from QA_elasticsearch import QA
from LLM_FULL_elasticsearch import LLM_FULL
from LLM_SMALL_elasticsearch import LLM_SMALL

def main():
    if "logged_in" not in st.session_state:
        login_page()
    else:
        upload_file_page()

def login_page():
    st.title("Trang đăng nhập")
    username = st.text_input("Tài khoản")
    password = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        if username == "admin" and password == "1234":
            st.success("Đăng nhập thành công!")
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Tài khoản hoặc mật khẩu không đúng. Vui lòng thử lại.")

def upload_file_page():
    st.title("Trang tải lên và danh sách tệp")

    index_input = st.text_input("Nhập tên Index:")
    column_input = st.text_input("Nhập tên Column:")

    uploaded_file = st.file_uploader("Tải lên tệp", type=['csv', 'xlsx', 'docx'])
    if uploaded_file is not None:
        if index_input and column_input:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == 'csv' or file_extension == 'xlsx':
                QA.process_file(uploaded_file, index_input, column_input)
            elif file_extension == 'docx':
                LLM_FULL.process_file(uploaded_file, index_input, column_input)
                LLM_SMALL.process_file(uploaded_file, index_input, column_input)
            else:
                st.warning("Loại file không được hỗ trợ.")
        else:
            st.warning("Vui lòng nhập tên Index và Column trước khi tải lên tệp.")

    file_categories = st.multiselect("Chọn loại file", ['csv', 'xlsx', 'docx'], default=['csv', 'xlsx', 'docx'])
    list_uploaded_files(file_categories)

def list_uploaded_files(file_categories):
    st.title("Danh sách tệp đã tải lên")
    if os.path.exists("uploads"):
        files = os.listdir("uploads")
        for file in files:
            file_extension = file.split(".")[-1].lower()
            if file_extension in file_categories:
                file_path = os.path.join("uploads", file)
                upload_time = get_upload_time(file_path)
                st.write(f"{file} - Uploaded at: {upload_time}")
    else:
        st.write("Chưa có tệp nào được tải lên.")

def get_upload_time(file_path):
    upload_time = os.path.getctime(file_path)
    formatted_time = datetime.fromtimestamp(upload_time).strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def get_download_link(file_path):
    with open(file_path, "rb") as f:
        file_contents = f.read()
    b64_file = base64.b64encode(file_contents).decode()
    href = f'data:application/octet-stream;base64,{b64_file}'
    return href

if __name__ == "__main__":
    main()
