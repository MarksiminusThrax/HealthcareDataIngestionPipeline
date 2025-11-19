
import streamlit as st
import pandas as pd
import numpy as np
import time
import io

# Configure the page
st.set_page_config(page_title="Healthcare Data Pipeline", page_icon="🏥", layout="wide")

# Title and description
st.title("🏥 Healthcare Provider Data Pipeline")
st.markdown("Interactive prototype for NPPES data ingestion, filtering, cleaning, and synchronization with Brilliant Directories")

# Initialize session state
if 'raw_data' not in st.session_state:
    st.session_state.raw_data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'cleaned_data' not in st.session_state:
    st.session_state.cleaned_data = None
if 'sync_results' not in st.session_state:
    st.session_state.sync_results = None

# Generate sample NPPES data
def generate_sample_data():
    """Generate realistic sample NPPES data for demonstration"""
    npis = [f"{np.random.randint(1000000000, 1999999999)}" for _ in range(50)]
    
    specialties = ['207R00000X', '207Q00000X', '208D00000X', '106S00000X', '122300000X', 
                   '163W00000X', '183500000X', '207V00000X', '208600000X']
    
    data = {
        'NPI': npis,
        'Provider_Name': [f"Dr. {name} {lastname}" for name, lastname in 
                         zip(np.random.choice(['John', 'Jane', 'Robert', 'Maria', 'David', 'Sarah'], 50),
                             np.random.choice(['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Garcia'], 50))],
        'Taxonomy_Code': np.random.choice(specialties, 50),
        'Address_Line_1': [f"{np.random.randint(100, 9999)} {name} St" for name in 
                          np.random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'], 50)],
        'City': np.random.choice(['Boston', 'Cambridge', 'Somerville', 'Brookline', 'Quincy'], 50),
        'State': ['MA'] * 50,
        'ZIP_Code': [f"0{np.random.randint(1000, 9999)}" for _ in range(50)],
        'Phone': [f"617-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}" for _ in range(50)],
        'Status': ['A'] * 45 + ['I'] * 5  # 45 Active, 5 Inactive
    }
    
    # Make some data messy for demonstration
    df = pd.DataFrame(data)
    
    # Add some messy phone numbers
    messy_indices = np.random.choice(50, 10, replace=False)
    df.loc[messy_indices, 'Phone'] = df.loc[messy_indices, 'Phone'].str.replace('-', '.')
    
    # Add some messy addresses
    messy_addr_indices = np.random.choice(50, 8, replace=False)
    df.loc[messy_addr_indices, 'Address_Line_1'] = df.loc[messy_addr_indices, 'Address_Line_1'].str.lower()
    
    return df

# Main workflow
st.header("📋 Data Pipeline Workflow")

# Step 1: Data Ingestion
st.subheader("1. Data Ingestion")
col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Generate Sample NPPES Data", use_container_width=True):
        sample_data = generate_sample_data()
        st.session_state.raw_data = sample_data
        st.session_state.filtered_data = None
        st.session_state.cleaned_data = None
        st.session_state.sync_results = None
        st.success(f"Generated {len(sample_data)} sample provider records!")

with col2:
    uploaded_file = st.file_uploader("Or upload your CSV", type=['csv'])
    if uploaded_file is not None:
        st.session_state.raw_data = pd.read_csv(uploaded_file)
        st.success(f"Uploaded {len(st.session_state.raw_data)} records!")

# Display raw data if available
if st.session_state.raw_data is not None:
    with st.expander("📊 View Raw NPPES Data", expanded=False):
        st.dataframe(st.session_state.raw_data, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Records", len(st.session_state.raw_data))
        with col2:
            st.metric("Active Providers", len(st.session_state.raw_data[st.session_state.raw_data['Status'] == 'A']))
        with col3:
            st.metric("Unique Specialties", st.session_state.raw_data['Taxonomy_Code'].nunique())

# Step 2: Data Filtering
if st.session_state.raw_data is not None:
    st.subheader("2. Data Filtering")
    
    st.markdown("**Target Specialties:**")
    st.code("207R00000X (Internal Medicine), 207Q00000X (Family Medicine), 208D00000X (General Practice)")
    
    if st.button("🎯 Filter Primary Care Providers", use_container_width=True):
        primary_care_taxonomies = ['207R00000X', '207Q00000X', '208D00000X']
        
        filtered_data = st.session_state.raw_data[
            (st.session_state.raw_data['Taxonomy_Code'].isin(primary_care_taxonomies)) &
            (st.session_state.raw_data['Status'] == 'A')
        ].copy()
        
        st.session_state.filtered_data = filtered_data
        st.success(f"Filtered {len(filtered_data)} primary care providers from {len(st.session_state.raw_data)} total records!")

# Display filtered data if available
if st.session_state.filtered_data is not None:
    with st.expander("🎯 View Filtered Primary Care Providers", expanded=False):
        st.dataframe(st.session_state.filtered_data, use_container_width=True)
        
        # Show taxonomy distribution
        taxonomy_counts = st.session_state.filtered_data['Taxonomy_Code'].value_counts()
        st.bar_chart(taxonomy_counts)

# Step 3: Data Cleaning
if st.session_state.filtered_data is not None:
    st.subheader("3. Data Cleaning & Normalization")
    
    if st.button("🧹 Clean & Normalize Data", use_container_width=True):
        with st.spinner("Cleaning and normalizing data..."):
            cleaned_data = st.session_state.filtered_data.copy()
            
            # Normalize phone numbers
            cleaned_data['Phone_Clean'] = cleaned_data['Phone'].str.replace(r'[^\d]', '', regex=True)
            cleaned_data['Phone_Clean'] = cleaned_data['Phone_Clean'].apply(
                lambda x: f"{x[:3]}-{x[3:6]}-{x[6:]}" if len(x) == 10 else x
            )
            
            # Standardize addresses
            cleaned_data['Address_Clean'] = cleaned_data['Address_Line_1'].str.title()
            
            # Add full address field
            cleaned_data['Full_Address'] = (
                cleaned_data['Address_Clean'] + ', ' + 
                cleaned_data['City'] + ', ' + 
                cleaned_data['State'] + ' ' + 
                cleaned_data['ZIP_Code']
            )
            
            st.session_state.cleaned_data = cleaned_data
            st.success("Data cleaning completed!")

# Display cleaning results
if st.session_state.cleaned_data is not None:
    with st.expander("🧹 View Data Cleaning Results", expanded=True):
        st.markdown("**Before vs After Cleaning:**")
        
        # Show sample of cleaned data
        sample_cleaned = st.session_state.cleaned_data[['Provider_Name', 'Phone', 'Phone_Clean', 'Address_Line_1', 'Address_Clean']].head(5)
        st.dataframe(sample_cleaned, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Records Cleaned", len(st.session_state.cleaned_data))
        with col2:
            st.metric("Phone Numbers Normalized", 
                     len(st.session_state.cleaned_data[st.session_state.cleaned_data['Phone'] != 
                                                      st.session_state.cleaned_data['Phone_Clean']]))

# Step 4: API Synchronization
if st.session_state.cleaned_data is not None:
    st.subheader("4. Brilliant Directories Sync")
    
    if st.button("🔄 Simulate API Synchronization", use_container_width=True):
        st.session_state.sync_results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_container = st.empty()
        
        log_messages = []
        cleaned_data = st.session_state.cleaned_data
        
        for i, (index, row) in enumerate(cleaned_data.iterrows()):
            progress = (i + 1) / len(cleaned_data)
            progress_bar.progress(progress)
            
            # Simulate API call logic
            if i % 3 == 0:  # Simulate creating new listings
                message = f"CREATE: {row['Provider_Name']} (NPI: {row['NPI']})"
                log_messages.append(f"✅ {message}")
            else:  # Simulate updating existing listings
                message = f"UPDATE: {row['Provider_Name']} (NPI: {row['NPI']})"
                log_messages.append(f"🔄 {message}")
            
            # Update log display (show last 10 messages)
            status_text.text(f"Processing {i+1}/{len(cleaned_data)}: {row['Provider_Name']}")
            log_container.code("\n".join(log_messages[-10:]))
            
            # Simulate API processing time
            time.sleep(0.1)
            
            st.session_state.sync_results.append({
                'npi': row['NPI'],
                'name': row['Provider_Name'],
                'action': 'CREATE' if i % 3 == 0 else 'UPDATE',
                'success': True
            })
        
        progress_bar.empty()
        status_text.empty()
        st.balloons()
        st.success(f"✅ Synchronization Complete! Processed {len(cleaned_data)} provider records.")

# Display final results
if st.session_state.sync_results is not None:
    st.subheader("📈 Sync Summary")
    
    results_df = pd.DataFrame(st.session_state.sync_results)
    action_counts = results_df['action'].value_counts()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Processed", len(results_df))
    with col2:
        st.metric("New Listings", action_counts.get('CREATE', 0))
    with col3:
        st.metric("Updated Listings", action_counts.get('UPDATE', 0))
    
    # Export options
    st.subheader("📤 Export Results")
    
    if st.session_state.cleaned_data is not None:
        # Convert cleaned data to CSV for download
        csv = st.session_state.cleaned_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Cleaned Data (CSV)",
            data=csv,
            file_name="cleaned_primary_care_providers.csv",
            mime="text/csv",
            use_container_width=True
        )

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ Pipeline Info")
    
    st.markdown("""
    **Workflow Steps:**
    
    1. **Ingestion** - Load NPPES data from source
    2. **Filtering** - Isolate Primary Care providers
    3. **Cleaning** - Normalize phone numbers, addresses
    4. **Synchronization** - Sync with Brilliant Directories API
    
    **Target Taxonomies:**
    - 207R00000X: Internal Medicine
    - 207Q00000X: Family Medicine  
    - 208D00000X: General Practice
    """)
    
    if st.session_state.raw_data is not None:
        st.metric("Raw Records", len(st.session_state.raw_data))
    if st.session_state.filtered_data is not None:
        st.metric("Filtered Records", len(st.session_state.filtered_data))
    if st.session_state.cleaned_data is not None:
        st.metric("Cleaned Records", len(st.session_state.cleaned_data))

st.markdown("---")
st.markdown("*Prototype for Healthcare Data Ingestion Pipeline - Generated sample data for demonstration*")