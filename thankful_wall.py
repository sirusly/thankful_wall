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

# Mobile instructions
st.info("""
📱 **Mobile Users | 手机用户:** 
Tap the two arrows (>>) in the **top left** to open the menu and add your entry!
点击**左上角**的两个箭头 (>>) 打开菜单添加您的条目！
""")

# New markdown section with the gratitude message
st.markdown("""
This is a special time of the year when we gather to express gratitude for all that we appreciate in life. We may be thankful for:

在这个一年度的特别时刻，我们欢聚一堂，感恩生活中值得珍惜的一切。我们感谢的可能是：

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

def get_all_entries_sorted():
    """Get all entries sorted by manual order, then by timestamp"""
    if db is None:
        return {}
    
    try:
        entries_ref = db.collection('thankful_entries')
        docs = entries_ref.stream()
        
        entries = {}
        for doc in docs:
            entry_data = doc.to_dict()
            entry_data['firebase_id'] = doc.id  # Store the Firebase document ID
            entries[doc.id] = entry_data
        
        # Sort entries: first by manual_order (if exists), then by Firebase ID (chronological)
        sorted_entries = dict(sorted(entries.items(), 
                                   key=lambda x: (x[1].get('manual_order', 999999), x[0])))
        return sorted_entries
    except Exception as e:
        st.error(f"Error getting sorted entries: {e}")
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

def update_entry_order(entry_id, new_data):
    """Update a specific entry with new data"""
    if db is None:
        st.error("Database not connected")
        return False
    
    try:
        db.collection('thankful_entries').document(entry_id).update(new_data)
        return True
    except Exception as e:
        st.error(f"Error updating entry: {e}")
        return False

def update_entry(entry_id, updated_data):
    """Update an existing entry with new data"""
    if db is None:
        st.error("Database not connected")
        return False
    
    try:
        db.collection('thankful_entries').document(entry_id).update(updated_data)
        return True
    except Exception as e:
        st.error(f"Error updating entry: {e}")
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

# Load the current data - USING SORTED ENTRIES
entries = get_all_entries_sorted()

# --- Sidebar for Adding New Entries ---
st.sidebar.header("Add Your Gratitude 添加感恩")

# Initialize session state for form submission
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'success_message' not in st.session_state:
    st.session_state.success_message = ""
if 'editing_entry' not in st.session_state:
    st.session_state.editing_entry = None

# Simple form without clear_on_submit for better control
english_name = st.sidebar.text_input("English Name 英文名", key="english_name")
chinese_name = st.sidebar.text_input("Chinese Name 中文名", key="chinese_name")
role_class = st.sidebar.text_input("Class or Role (e.g., G10-2, Teacher, Administrator, etc.) 班级或身份 (例如: A班, 老师, 家长等)", key="role_class")
thankful_for = st.sidebar.text_area("What are you thankful for? 你感恩什么?", key="thankful_for")

# Submit button
if st.sidebar.button("Submit 提交", type="primary"):
    if english_name and chinese_name and thankful_for:
        # Show loading state
        with st.sidebar:
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
                    st.sidebar.error("❌ Failed to save entry. Please try again. 保存失败，请重试。")
    else:
        st.sidebar.error("❌ Please fill in name fields and what you're thankful for. 请填写姓名字段和您感恩的内容。")

# Display success message if form was submitted
if st.session_state.submitted and st.session_state.success_message:
    st.sidebar.success(st.session_state.success_message)
    
    # Show a progress bar to indicate waiting time
    progress_bar = st.sidebar.progress(0)
    for i in range(100):
        # Update progress bar
        progress_bar.progress(i + 1)
        time.sleep(0.03)  # 3 second total wait time
    
    # Clear the message and refresh
    st.session_state.submitted = False
    st.session_state.success_message = ""
    st.rerun()

# --- Main Area: Display the Thankful Wall ---
st.header("Our Thankful Wall - 👇Scroll down to view 👇我们的感恩墙 - 向下滚动查看 👇")

# Refresh entries data - USING SORTED ENTRIES
entries = get_all_entries_sorted()

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
    
    # Check if manual ordering is being used
    has_manual_order = any(entry.get('manual_order') for entry in entries.values())
    if has_manual_order:
        st.subheader(f"All Entries (Manual Order) 所有条目 (手动排序)")
    else:
        st.subheader(f"All Entries (Newest First) 所有条目 (最新优先)")
    
    # Show loading message while entries refresh
    if st.session_state.get('submitted', False):
        st.info("🔄 Loading latest entries... Please wait. 正在加载最新条目... 请稍候。")
    
    # Display entries in the sorted order (already sorted by get_all_entries_sorted)
    for entry_id, info in entries.items():
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
            
            # Show manual order if it exists
            if info.get('manual_order'):
                st.caption(f"Position: {info['manual_order']} • 位置: {info['manual_order']} • Entry ID: {entry_id[:8]}...")
            else:
                st.caption(f"Entry ID: {entry_id[:8]}... • 条目ID: {entry_id[:8]}...")
            st.divider()

# --- Admin Section in the Sidebar ---
st.sidebar.header("Admin Section 管理员部分")
admin_password = st.sidebar.text_input("Password 密码", type="password", key="admin_pass")

if admin_password == "admin":  # Simple password check
    st.sidebar.success("🔓 Access Granted 访问批准")
    
    # Edit Entry Section
    st.sidebar.subheader("Edit Entry 编辑条目")
    
    if entries:
        # Create a dropdown of all entries for editing
        edit_entry_options = {}
        for entry_id, info in entries.items():
            role_class = info.get('role_class', 'Not specified')
            edit_entry_options[f"ID {entry_id[:8]}: {info['english_name']} - {role_class}"] = entry_id
        
        selected_edit_entry = st.sidebar.selectbox(
            "Select entry to edit 选择要编辑的条目",
            [""] + list(edit_entry_options.keys()),
            key="edit_select"
        )
        
        if selected_edit_entry:
            entry_id_to_edit = edit_entry_options[selected_edit_entry]
            entry_to_edit = entries[entry_id_to_edit]
            
            # Pre-fill form with existing data
            st.sidebar.write("**Edit Entry Details 编辑条目详情:**")
            
            edit_english_name = st.sidebar.text_input(
                "English Name 英文名", 
                value=entry_to_edit['english_name'],
                key="edit_english_name"
            )
            edit_chinese_name = st.sidebar.text_input(
                "Chinese Name 中文名", 
                value=entry_to_edit['chinese_name'],
                key="edit_chinese_name"
            )
            edit_role_class = st.sidebar.text_input(
                "Class or Role 班级或身份", 
                value=entry_to_edit.get('role_class', ''),
                key="edit_role_class"
            )
            edit_thankful_for = st.sidebar.text_area(
                "What are you thankful for? 你感恩什么?", 
                value=entry_to_edit['thankful_for'],
                key="edit_thankful_for"
            )
            
            if st.sidebar.button("Update Entry 更新条目", key="update_btn"):
                if edit_english_name and edit_chinese_name and edit_thankful_for:
                    with st.sidebar:
                        with st.spinner("Updating entry... 正在更新条目..."):
                            updated_data = {
                                "english_name": edit_english_name,
                                "chinese_name": edit_chinese_name,
                                "role_class": edit_role_class if edit_role_class else "Not specified 未指定",
                                "thankful_for": edit_thankful_for
                            }
                            
                            if update_entry(entry_id_to_edit, updated_data):
                                st.sidebar.success("✅ Entry updated successfully! 条目更新成功!")
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.sidebar.error("❌ Failed to update entry. 更新条目失败。")
                else:
                    st.sidebar.error("❌ Please fill in all required fields. 请填写所有必填字段。")
    
    else:
        st.sidebar.info("No entries to edit 没有可编辑的条目")
    
    # Reorder Entries Section - UPDATED WITH OPTION 1
    st.sidebar.subheader("Reorder Entries 重新排序条目")
    
    if entries:
        st.sidebar.write("Set the display order 设置显示顺序:")
        
        # Get current order information
        sorted_entries = get_all_entries_sorted()
        entry_list = list(sorted_entries.items())
        
        # Create a list of entries for the reorder interface
        entry_options = []
        for entry_id, info in entry_list:
            display_text = f"{info['english_name']} ({info['chinese_name']}) - {info.get('thankful_for', '')[:30]}..."
            entry_options.append((entry_id, display_text, info.get('manual_order')))
        
        # Display current order
        st.sidebar.write("**Current Order 当前顺序:**")
        for i, (entry_id, display_text, manual_order) in enumerate(entry_options, 1):
            order_indicator = f" [Position {manual_order}]" if manual_order else ""
            st.sidebar.write(f"{i}. {display_text}{order_indicator}")
        
        # NEW: Improved reorder interface with individual number inputs
        st.sidebar.write("**Set New Order 设置新顺序:**")
        
        # Create a expander to keep it organized
        with st.sidebar.expander("Set Positions 设置位置", expanded=True):
            # Create a dictionary to store new positions
            new_positions = {}
            
            for entry_id, info in entries.items():
                display_text = f"{info['english_name']} ({info['chinese_name']})"
                current_pos = info.get('manual_order', 'Auto')
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{display_text}**")
                    st.caption(f"Current: {current_pos} • 当前: {current_pos}")
                with col2:
                    new_position = st.number_input(
                        "Position 位置",
                        min_value=1,
                        max_value=len(entries),
                        value=current_pos if current_pos != 'Auto' else len(entries),
                        key=f"order_{entry_id}",
                        label_visibility="collapsed"
                    )
                    new_positions[entry_id] = new_position

            if st.button("Apply New Order 应用新顺序", key="apply_order"):
                with st.spinner("Updating order... 正在更新顺序..."):
                    success_count = 0
                    for entry_id, new_position in new_positions.items():
                        if update_entry_order(entry_id, {'manual_order': new_position}):
                            success_count += 1
                    
                    if success_count == len(new_positions):
                        st.success(f"✅ Order updated for {success_count} entries! 已更新{success_count}个条目的顺序!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("❌ Some entries failed to update. 部分条目更新失败。")
        
        # Reset order button
        if st.sidebar.button("Reset to Default Order 重置为默认顺序", key="reset_order"):
            with st.sidebar:
                with st.spinner("Resetting order... 正在重置顺序..."):
                    success_count = 0
                    for entry_id in entries.keys():
                        # Use DELETE_FIELD to remove the manual_order field
                        if update_entry_order(entry_id, {'manual_order': firestore.DELETE_FIELD}):
                            success_count += 1
                    
                    st.sidebar.success(f"✅ Order reset for {success_count} entries! 已重置{success_count}个条目的顺序!")
                    time.sleep(2)
                    st.rerun()
    
    else:
        st.sidebar.info("No entries to reorder 没有可重新排序的条目")
    
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
