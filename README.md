# Brand Discovery

AI-powered retail intelligence for identifying promising CPG brands and assessing their market potential.

## Overview

Brand Discovery helps you:
- **Research brands** automatically from websites or names
- **Analyze market positioning** and competitive landscape
- **Assess retail readiness** and growth potential
- **Identify target consumers** and demographic fit
- **Evaluate distribution opportunities** across 71,000+ US stores

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

3. **Run the web app:**
   ```bash
   streamlit run app.py
   ```

## Features

### Brand Research
- Automatic web research for brand profiles
- Category classification and subcategory analysis
- Pricing strategy and SRP identification
- Distributor and retail presence mapping
- Label claims and positioning analysis

### Market Analysis
- Consumer persona generation
- Demographic targeting assessment
- Store fit scoring across multiple banners
- Growth potential evaluation
- Competitive advantage identification

### Retail Intelligence
- 71,000+ US grocery store database
- Trade area demographic analysis
- Banner-specific shopper personas
- Distribution channel recommendations

## Usage

### Web Interface
Paste a brand website or name to start research, then define target consumers to see retail fit analysis.

### Command Line
```bash
# Analyze a single brand
python run.py try --brand "Brand Name" --category "category"

# Batch analyze multiple brands
python run.py batch --pairs pairs/sample.csv
```

## Data Sources

- Store data: Enriched with demographic and sales information
- Brand research: Real-time web scraping and analysis
- Market intelligence: Consumer trends and retail dynamics

## Requirements

- Python 3.8+
- Anthropic Claude API key
- Streamlit for web interface
- Pandas for data analysis

## License

[Your License Here]