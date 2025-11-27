import streamlit as st
import json
import os

# Set the page title and layout
st.set_page_config(page_title="Thanksgiving Thankful Wall", layout="wide")

# Page header
st.title("🦃 Thanksgiving Thankful Wall 感恩节感恩墙")
st.markdown("Share what you're thankful for! 分享你的感恩之心！")

# Initialize the JSON file to store data
DATA_FILE = "thankful_wall.json"


# Load existing entries from the JSON file
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {"entries": {}}


# Save entries to the JSON file
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


# Load the current data
data = load_data()
entries = data.get("entries", {})

# --- Sidebar for Adding New Entries ---
st.sidebar.header("Add Your Gratitude 添加感恩")

with st.sidebar.form("entry_form"):
    english_name = st.text_input("English Name 英文名")
    chinese_name = st.text_input("Chinese Name 中文名")

    # Simple text field for class/role - users can type anything
    role_class = st.text_input(
        "Class or Role (e.g., Class A, Teacher, Parent, etc.) 班级或身份 (例如: A班, 老师, 家长等)")

    thankful_for = st.text_area("What are you're thankful for? 你感恩什么?")
    submitted = st.form_submit_button("Submit 提交")

    if submitted:
        if english_name and chinese_name and thankful_for:
            # Generate a new entry ID
            new_id = str(len(entries) + 1)
            entries[new_id] = {
                "english_name": english_name,
                "chinese_name": chinese_name,
                "role_class": role_class if role_class else "Not specified 未指定",
                "thankful_for": thankful_for
            }
            data["entries"] = entries
            save_data(data)
            st.sidebar.success("Thank you! Your entry has been added. 谢谢！您的条目已添加。")
            st.rerun()  # Refresh to show the new entry
        else:
            st.sidebar.error("Please fill in name fields and what you're thankful for. 请填写姓名字段和您感恩的内容。")

# --- Main Area: Display the Thankful Wall ---
st.header("Our Thankful Wall 我们的感恩墙")

# Display all entries
if not entries:
    st.info("The wall is empty... Let's add some gratitude! 墙上空空的... 让我们添加一些感恩!")
else:
    # Show statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Entries 总条目数", len(entries))

    # Count teachers - safely handle missing role_class fields
    teachers = 0
    for entry in entries.values():
        role = entry.get("role_class", "").lower()
        if "teacher" in role:
            teachers += 1

    with col2:
        st.metric("Teachers 老师", teachers)

    # Display entries
    for entry_id, info in entries.items():
        with st.container():
            # Create a nice card-like display
            st.subheader(f"Entry {entry_id}")

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
            st.divider()

# --- Admin Section in the Sidebar ---
st.sidebar.header("Admin Section 管理员部分")
admin_password = st.sidebar.text_input("Password 密码", type="password")

if admin_password == "admin":  # Simple password check
    st.sidebar.success("Access Granted 访问批准")

    # Individual entry deletion
    st.sidebar.subheader("Delete Specific Entry 删除特定条目")
    if entries:
        # Create a dropdown of all entries for deletion
        entry_options = {}
        for id, info in entries.items():
            # Safely handle missing role_class field
            role_class = info.get('role_class', 'Not specified')
            entry_options[f"ID {id}: {info['english_name']} - {role_class}"] = id

        selected_entry = st.sidebar.selectbox(
            "Select entry to delete 选择要删除的条目",
            [""] + list(entry_options.keys())
        )

        if selected_entry and st.sidebar.button("Delete Selected Entry 删除选定条目"):
            entry_id_to_delete = entry_options[selected_entry]
            # Store the entry info before deleting for confirmation message
            deleted_entry = entries[entry_id_to_delete]
            del entries[entry_id_to_delete]
            data["entries"] = entries
            save_data(data)
            st.sidebar.success(f"Deleted: {deleted_entry['english_name']} ({deleted_entry['chinese_name']}) 已删除!")
            st.rerun()
    else:
        st.sidebar.info("No entries to delete 没有可删除的条目")

    # Delete all entries with confirmation
    st.sidebar.subheader("Delete All Entries 删除所有条目")

    if st.sidebar.button("Show Delete All Options 显示删除所有选项"):
        st.sidebar.warning("⚠️ This will delete ALL entries! 这将删除所有条目!")

        # Double confirmation for delete all
        confirm_text = st.sidebar.text_input(
            "Type 'DELETE ALL' to confirm 输入 'DELETE ALL' 确认",
            key="delete_confirm"
        )

        if confirm_text == "DELETE ALL":
            if st.sidebar.button("🚨 CONFIRM DELETE ALL 确认删除所有", type="primary"):
                data["entries"] = {}
                save_data(data)
                st.sidebar.error("All entries have been deleted. 所有条目已被删除。")
                st.rerun()
        elif confirm_text and confirm_text != "DELETE ALL":
            st.sidebar.error("Incorrect confirmation text 确认文本不正确")

else:
    if admin_password:
        st.sidebar.error("Incorrect Password 密码错误")

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
""")