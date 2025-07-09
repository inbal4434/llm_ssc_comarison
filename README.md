# 🏗️ Architecture Comparison Dashboard

Interactive Streamlit dashboard for comparing baseline vs enhanced cloud architectures.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate comparison data
python compare_architectures_tabular.py

# Run dashboard
streamlit run streamlit_tabular_comparison.py
```

## 📊 Features

- Binary comparison indicators (1/0) for services, components, attributes, configurations
- Detailed difference analysis with reasoning explanations
- Interactive filtering and search
- Architecture deep-dive views

## 🌐 Live Demo

[View Dashboard](https://your-streamlit-app-url.streamlit.app)

## 📋 Data Format

Compares two JSON architecture datasets with corresponding reasoning files to show:

- What's different between baseline and enhanced architectures
- Why specific choices were made (from AI reasoning)
- Detailed breakdown at each level of the architecture

---

Built with ❤️ using Streamlit
