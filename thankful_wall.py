import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import time

# Set the page title and layout
st.set_page_config(page_title="Thanksgiving Thankful Wall", layout="wide")

# Page header
st.title("🦃 Happy Thanksgiving! 感恩节快乐! 🦃")

# Add the smaller message about Python
st.caption("This application was created entirely with Python! 这个应用程序完全使用Python创建!")

# New markdown section with the gratitude message
st.markdown("""
This is a special time of the year when we gather to express gratitude for all that we appreciate in life. We may be thankful for:

在这个一年一度的特别时刻，我们欢聚一堂，感恩生活中值得珍惜的一切。我们感谢的可能是：

- Family and friends 家人和朋友
- Good health 健康
- Education opportunities 教育机会
- Delicious food 美味的食物
- A warm home 温暖的家
- Kind teachers 善良的老师
- Beautiful nature 美丽的大自然
- Technology 科技
- Music and art 音乐和艺术
- A peaceful life 和平的生活

…and so much more! Let's always remember to cherish what we have.

……还有很多很多！愿我们始终心怀感恩，珍惜所拥有的一切。
""")

# Add the smaller message about Python
st.caption("This application was created entirely with Python. 这个应用程序完全使用Python创建。")

# Initialize Firebase
def initialize_firebase():
    try:
        # Check if Firebase app is already initialized
        if not firebase_admin._apps:
            # Use Streamlit secrets for Firebase configuration
            firebase_config = {
                "type": st.secrets["firebase"]["type"],
                "project_id": st.secrets["firebase"]["project_id"],
                "private_key_id": st.secrets["firebase"]["private_key_id"],
                "private_key": st.secrets["firebase"]["private_key"].replace('\\n', '\n'),
                "client_email": st.secrets["firebase"]["client_email"],
                "client_id": st.secrets["firebase"]["client_id"],
                "auth_uri": st.secrets["firebase"]["auth_uri"],
                "token_uri": st.secrets["firebase"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
            }
            
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        return None

# Initialize Firebase
db = initialize_firebase()

def get_all_entries():
    """Get all entries from Firestore"""
    if db is None:
        return {}
    
    try:
        entries_ref = db.collection('thankful_entries')
        docs = entries_ref.stream()
        
        entries = {}
        for doc in docs:
            entries[doc.id] = doc.to_dict()
        
        return entries
    except Exception as e:
        st.error(f"Error getting entries: {e}")
        return {}

def add_single_entry(entry_data):
    """Add a single entry to Firestore"""
    if db is None:
        st.error("Database not connected")
        return False
    
    try:
        entries_ref = db.collection('thankful_entries')
        # Generate a new document ID
        new_doc_ref = entries_ref.document()
        entry_data['entry_id'] = new_doc_ref.id
        new_doc_ref.set(entry_data)
        return True
    except Exception as e:
        st.error(f"Error adding entry: {e}")
        return False

def delete_entry(entry_id):
    """Delete a specific entry from Firestore"""
    if db is None:
        st.error("Database not connected")
        return False
    
    try:
        db.collection('thankful_entries').document(entry_id).delete()
        return True
    except Exception as e:
        st.error(f"Error deleting entry: {e}")
        return False

def delete_all_entries():
    """Delete all entries from Firestore"""
    if db is None:
        st.error("Database not connected")
        return False
    
    try:
        entries_ref = db.collection('thankful_entries')
        docs = entries_ref.stream()
        for doc in docs:
            doc.reference.delete()
        return True
    except Exception as e:
        st.error(f"Error deleting all entries: {e}")
        return False

# Load the current data
entries = get_all_entries()

# --- MAIN AREA: Add Your Gratitude Form ---
st.header("Add Your Gratitude 添加感恩")

# Initialize session state for form submission
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'success_message' not in st.session_state:
    st.session_state.success_message = ""

# Create the form in the main area (not sidebar)
with st.form("main_entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        english_name = st.text_input("English Name 英文名", key="english_name")
    with col2:
        chinese_name = st.text_input("Chinese Name 中文名", key="chinese_name")
    
    role_class = st.text_input("Class or Role (e.g., Class A, Teacher, Parent, etc.) 班级或身份 (例如: A班, 老师, 家长等)", key="role_class")
    thankful_for = st.text_area("What are you thankful for? 你感恩什么?", key="thankful_for")
    
    submitted = st.form_submit_button("Submit 提交", type="primary")

    if submitted:
        if english_name and chinese_name and thankful_for:
            # Show loading state
            with st.spinner("Saving your entry... 正在保存您的条目..."):
                entry_data = {
                    "english_name": english_name,
                    "chinese_name": chinese_name,
                    "role_class": role_class if role_class else "Not specified 未指定",
                    "thankful_for": thankful_for
                }
                
                if add_single_entry(entry_data):
                    # Set simplified success message
                    st.session_state.success_message = """
                    🎉 **Thank you! Your entry has been saved successfully! 谢谢！您的条目已成功保存！**
                    
                    ⏳ **Please wait a moment for the page to update and show your entry below.**
                    ⏳ **请稍等片刻，页面将更新并在下方显示您的条目。**
                    """
                    st.session_state.submitted = True
                    
                    # Force immediate rerun to show success message and refresh data
                    st.rerun()
                else:
                    st.error("❌ Failed to save entry. Please try again. 保存失败，请重试。")
        else:
            st.error("❌ Please fill in name fields and what you're thankful for. 请填写姓名字段和您感恩的内容。")

# Display success message if form was submitted
if st.session_state.submitted and st.session_state.success_message:
    st.success(st.session_state.success_message)
    
    # Show a progress bar to indicate waiting time
    progress_bar = st.progress(0)
    for i in range(100):
        # Update progress bar
        progress_bar.progress(i + 1)
        time.sleep(0.03)  # 3 second total wait time
    
    # Clear the message and refresh
    st.session_state.submitted = False
    st.session_state.success_message = ""
    st.rerun()

# --- Main Area: Display the Thankful Wall ---
st.header("Our Thankful Wall 我们的感恩墙")

# Refresh entries data
entries = get_all_entries()

# Display all entries
if not entries:
    st.info("📝 The wall is empty... Let's add some gratitude! 墙上空空的... 让我们添加一些感恩!")
else:
    # Show statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entries 总条目数", len(entries))
    
    # Count teachers - safely handle missing role_class fields
    teachers = 0
    students = 0
    for entry in entries.values():
        role = entry.get("role_class", "").lower()
        if "teacher" in role:
            teachers += 1
        else:
            students += 1
    
    with col2:
        st.metric("Students 学生", students)
    with col3:
        st.metric("Teachers 老师", teachers)
    
    # Display entries with the newest first
    st.subheader(f"All Entries (Newest First) 所有条目 (最新优先)")
    
    # Show loading message while entries refresh
    if st.session_state.get('submitted', False):
        st.info("🔄 Loading latest entries... Please wait. 正在加载最新条目... 请稍候。")
    
    # Convert to list and reverse for newest first (Firestore orders by creation time)
    entries_list = list(entries.items())
    if entries_list:
        # Sort by document ID (newest first) - Firebase creates chronological IDs
        entries_list.sort(key=lambda x: x[0], reverse=True)
    
    for entry_id, info in entries_list:
        with st.container():
            # Create a nice card-like display
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.write(f"**English Name:** {info['english_name']}")
            with col2:
                st.write(f"**Chinese Name:** {info['chinese_name']}")
            with col3:
                # Safely handle missing role_class field
                role_class = info.get('role_class', 'Not specified 未指定')
                st.write(f"**Class/Role:** {role_class}")
            
            st.write(f"**Thankful For:** {info['thankful_for']}")
            
            # Show entry ID and timestamp-like info
            st.caption(f"Entry ID: {entry_id[:8]}... • 条目ID: {entry_id[:8]}...")
            st.divider()

# --- Admin Section in the Sidebar ---
st.sidebar.header("Admin Section 管理员部分")
admin_password = st.sidebar.text_input("Password 密码", type="password", key="admin_pass")

if admin_password == "admin":  # Simple password check
    st.sidebar.success("🔓 Access Granted 访问批准")
    
    # Individual entry deletion
    st.sidebar.subheader("Delete Specific Entry 删除特定条目")
    if entries:
        # Create a dropdown of all entries for deletion
        entry_options = {}
        for entry_id, info in entries.items():
            # Safely handle missing role_class field
            role_class = info.get('role_class', 'Not specified')
            # Show shortened ID for better display
            short_id = entry_id[:8] + "..."
            entry_options[f"ID {short_id}: {info['english_name']} - {role_class}"] = entry_id
        
        selected_entry = st.sidebar.selectbox(
            "Select entry to delete 选择要删除的条目",
            [""] + list(entry_options.keys()),
            key="delete_select"
        )
        
        if selected_entry and st.sidebar.button("Delete Selected Entry 删除选定条目", key="delete_btn"):
            entry_id_to_delete = entry_options[selected_entry]
            # Store the entry info before deleting for confirmation message
            deleted_entry = entries[entry_id_to_delete]
            
            with st.sidebar:
                with st.spinner("Deleting entry... 正在删除条目..."):
                    if delete_entry(entry_id_to_delete):
                        # Show deletion confirmation
                        st.sidebar.error(f"🗑️ Deleted: {deleted_entry['english_name']} ({deleted_entry['chinese_name']}) 已删除!")
                        time.sleep(2)
                        st.rerun()
    else:
        st.sidebar.info("No entries to delete 没有可删除的条目")
    
    # Delete all entries with confirmation
    st.sidebar.subheader("Delete All Entries 删除所有条目")
    
    if st.sidebar.button("Show Delete All Options 显示删除所有选项", key="delete_all_btn"):
        st.sidebar.warning("⚠️ This will delete ALL entries! 这将删除所有条目!")
        
        # Double confirmation for delete all
        confirm_text = st.sidebar.text_input(
            "Type 'DELETE ALL' to confirm 输入 'DELETE ALL' 确认",
            key="delete_confirm"
        )
        
        if confirm_text == "DELETE ALL":
            if st.sidebar.button("🚨 CONFIRM DELETE ALL 确认删除所有", type="primary", key="confirm_delete_all"):
                with st.sidebar:
                    with st.spinner("Deleting all entries... 正在删除所有条目..."):
                        if delete_all_entries():
                            st.sidebar.error("❌ All entries have been deleted. 所有条目已被删除。")
                            time.sleep(2)
                            st.rerun()
        elif confirm_text and confirm_text != "DELETE ALL":
            st.sidebar.error("Incorrect confirmation text 确认文本不正确")
    
else:
    if admin_password:
        st.sidebar.error("❌ Incorrect Password 密码错误")

# --- Footer ---
st.markdown("---")
st.markdown("### What we've learned in this project 我们在这个项目中学到了:")
st.markdown("""
- **print() statements** - Displaying output
- **input()** - Getting user input  
- **if-elif-else statements** - Decision making
- **Lists and dictionaries** - Data storage
- **Streamlit** - Creating web applications
- **JSON file handling** - Data persistence
- **Firebase Firestore** - Cloud database integration
""")

# Add a refresh button for good measure
if st.button("🔄 Refresh Page 刷新页面", key="refresh_btn"):
    with st.spinner("Refreshing... 正在刷新..."):
        time.sleep(1)
        st.rerun()

# Information about data persistence
st.sidebar.markdown("---")
st.sidebar.info("""
**About Data Storage 关于数据存储:**
All entries are stored securely in Google Firebase Firestore. 
Your data will persist even when the app is updated.
所有条目都安全地存储在 Google Firebase Firestore 中。
即使应用更新，您的数据也会保留。
""")
