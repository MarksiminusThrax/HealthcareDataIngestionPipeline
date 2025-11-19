# Healthcare Data Ingestion Pipeline

A scalable data pipeline for ingesting, processing, and synchronizing healthcare provider data from NPPES to Brilliant Directories.

## 🚀 Features

- **Data Ingestion**: Download and parse NPPES healthcare provider data
- **Intelligent Filtering**: Target Primary Care and Internal Medicine providers
- **Data Cleaning**: Normalize addresses, phone numbers, and provider information
- **API Integration**: Synchronize with Brilliant Directories platform
- **Interactive Prototype**: Streamlit app for demonstration and testing

## 📁 Project Structure

- `prototype/` - Interactive Streamlit demonstration
- `src/` - Production-ready Python modules
- `tests/` - Comprehensive test suite
- `docs/` - Project documentation

## 🛠️ Quick Start

### Running the Prototype
```bash
cd prototype
pip install -r requirements.txt
streamlit run app.py
