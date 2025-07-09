# 🏗️ Architecture Comparison Dashboard - Deployment Guide

This guide shows you how to share your Streamlit architecture comparison dashboard with others.

## 📊 What This App Does

- Compares baseline vs enhanced cloud architectures
- Shows binary indicators (1/0) for services, components, attributes, and configurations
- Displays specific differences and reasoning from AI analysis
- Interactive dashboard with filtering and detailed views

## 🚀 Sharing Options

### 1. 🌟 Streamlit Community Cloud (Recommended - Free & Public)

**Best for:** Sharing with anyone on the internet

**Steps:**

1. **Prepare your repository:**

   ```bash
   # Make sure you have all files
   git add .
   git commit -m "Add architecture comparison dashboard"
   git push origin main
   ```

2. **Deploy:**

   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Repository: `your-username/your-repo`
   - Branch: `main`
   - Main file path: `taura/sand_box/streamlit_tabular_comparison.py`
   - Click "Deploy"

3. **Share the URL:** Your app will be available at:
   `https://your-username-your-repo-streamlit-tabular-comparison-main.streamlit.app`

### 2. 🏠 Local Network Sharing

**Best for:** Sharing within your office/home network

**Quick Start:**

```bash
# Run the prepared script
./run_streamlit_local.sh
```

**Manual command:**

```bash
# Generate data first (if needed)
python compare_architectures_tabular.py

# Run Streamlit
streamlit run streamlit_tabular_comparison.py --server.address 0.0.0.0 --server.port 8501
```

**Access:**

- **Your computer:** http://localhost:8501
- **Others on network:** http://YOUR_IP_ADDRESS:8501
- Find your IP: `hostname -I` (Linux) or `ipconfig` (Windows)

### 3. 🌐 Tunnel Services (Quick Public Access)

**Best for:** Temporary sharing without GitHub setup

**Using ngrok:**

1. **Install ngrok:** [Download here](https://ngrok.com/download)
2. **Run your app locally:**
   ```bash
   streamlit run streamlit_tabular_comparison.py
   ```
3. **In another terminal:**
   ```bash
   ngrok http 8501
   ```
4. **Share the ngrok URL** (e.g., `https://abc123.ngrok.io`)

### 4. ☁️ Cloud Deployment

**Best for:** Professional, custom domain sharing

**Heroku Example:**

1. **Create `Procfile`:**

   ```
   web: streamlit run streamlit_tabular_comparison.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **Deploy:**
   ```bash
   # Install Heroku CLI, then:
   heroku create your-app-name
   git push heroku main
   ```

## 📋 Prerequisites

### Required Files:

- `compare_architectures_tabular.py` - Data generation script
- `streamlit_tabular_comparison.py` - Dashboard app
- `requirements.txt` - Dependencies
- `comparison_output/` directory with JSON data files

### Required Data Files:

```
comparison_output/
├── baseline_db_architectures_set_search_space_output.json
├── enhanced_db_architectures_set_search_space_output.json
├── baseline_db_architectures_set_search_space_reasoning_output.json
└── enhanced_db_architectures_set_search_space_reasoning_output.json
```

## 🔧 Setup Instructions

### 1. Install Dependencies:

```bash
pip install -r requirements.txt
```

### 2. Generate Comparison Data:

```bash
python compare_architectures_tabular.py
```

### 3. Run Dashboard:

```bash
streamlit run streamlit_tabular_comparison.py
```

## 🛠️ Troubleshooting

**Data not found error:**

- Run `python compare_architectures_tabular.py` first
- Check that all JSON files exist in `comparison_output/`

**Port already in use:**

```bash
streamlit run streamlit_tabular_comparison.py --server.port 8502
```

**Network access issues:**

- Check firewall settings
- Ensure port 8501 is open
- Try different port with `--server.port XXXX`

## 📱 Features Available to Users

1. **📊 Overview Tab:**

   - Summary metrics and charts
   - Quick insights about differences

2. **📋 Detailed Table Tab:**

   - Filterable comparison table
   - Color-coded binary indicators
   - Search functionality

3. **🔬 Architecture Deep Dive Tab:**
   - Individual architecture analysis
   - Detailed difference breakdowns
   - Reasoning explanations

## 🔒 Security Notes

- **Public deployment:** Don't include sensitive data
- **Local sharing:** Only shares with network users
- **Tunnel services:** Use for temporary sharing only
- **Authentication:** Streamlit Community Cloud doesn't have built-in auth

## 📞 Support

If users encounter issues:

1. Check the data files are present
2. Verify all dependencies are installed
3. Try refreshing the browser
4. Check console for error messages
