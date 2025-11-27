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
    """Get all entries sorted by manual order, then by timestamp (newest first)"""
    if db is None:
        return {}
    
    try:
        entries_ref = db.collection('thankful_entries')
        docs = entries_ref.stream()
        
        entries = {}
        manual_ordered = []
        auto_ordered = []
        
        for doc in docs:
            entry_data = doc.to_dict()
            entry_data['firebase_id'] = doc.id
            
            # Separate entries with manual order from those without
            if entry_data.get('manual_order'):
                manual_ordered.append((doc.id, entry_data))
            else:
                auto_ordered.append((doc.id, entry_data))
        
        # Sort manually ordered entries by their manual_order
        manual_ordered.sort(key=lambda x: x[1].get('manual_order', 999999))
        
        # Sort auto entries by Firebase ID in reverse (newest first)
        # Firebase IDs are chronological, so reverse gives newest first
        auto_ordered.sort(key=lambda x: x[0], reverse=True)
        
        # Combine: manual ordered first, then auto ordered (newest first)
        sorted_entries = {}
        for entry_id, entry_data in manual_ordered + auto_ordered:
            sorted_entries[entry_id] = entry_data
        
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

# --- Rest of your code remains exactly the same ---
# [All the sidebar forms, admin sections, and display code stay identical]
