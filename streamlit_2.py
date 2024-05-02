import streamlit as st
import os
import base64
from datetime import datetime

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
    
    # Hiển thị form chọn index và column
    index_input = st.text_input("Nhập tên Index:")
    column_input = st.text_input("Nhập tên Column:")

    # Hiển thị form tải lên tệp
    uploaded_file = st.file_uploader("Tải lên tệp", type=['csv', 'docx', 'pptx'])
    if uploaded_file is not None:
        if index_input and column_input:
            save_uploaded_file(uploaded_file, index_input, column_input)
        else:
            st.warning("Vui lòng nhập tên Index và Column trước khi tải lên tệp.")

    # Hiển thị danh sách các tệp đã tải lên
    file_categories = st.multiselect("Chọn loại file", ['csv', 'docx', 'pptx'], default=['csv', 'docx', 'pptx'])
    list_uploaded_files(file_categories)

def save_uploaded_file(uploaded_file, index_input, column_input):
    # Tạo một thư mục để lưu trữ tệp tải lên nếu nó không tồn tại
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Lưu tệp tải lên vào thư mục "uploads" với tên tệp giữ nguyên
    with open(os.path.join("uploads", f"{index_input}_{column_input}_{uploaded_file.name}"), "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Đã lưu tệp {index_input}_{column_input}_{uploaded_file.name} thành công!")


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
    clone_link = "https://abc.com/download"
    file_name = os.path.basename(file_path)
    return f"{clone_link}?file={file_name}"

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
                download_link = get_download_link(file_path)
                st.markdown(f"[download_link]({download_link})")
    else:
        st.write("Chưa có tệp nào được tải lên.")

if __name__ == "__main__":
    main()
