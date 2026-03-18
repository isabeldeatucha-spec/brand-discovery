# Brand Discovery

AI-powered tools for CPG brokers to discover emerging brands and assess broker-readiness.

## Overview

Brand Discovery helps CPG brokers in two key ways:

### 🌟 Brand Discovery
- **Trend Analysis**: Input market trends and discover emerging brands
- **Category Exploration**: Select categories and subcategories to focus research
- **Intelligent Scraping**: AI-powered web research to find promising brands

### 📊 Broker Readiness Assessment
- **Distribution Analysis**: Current POS count, retailers, and channels
- **SKU Intelligence**: Product variety, claims, and pricing strategies
- **Relationship Mapping**: Existing broker and distributor partnerships
- **Growth Signals**: Market momentum and scalability indicators

## Features

### Brand Discovery
- Trend-based brand identification
- Category and subcategory filtering
- Emerging brand scouting
- Growth signal analysis

### Broker Readiness Assessment
- Comprehensive distribution mapping
- SKU portfolio analysis
- Pricing strategy evaluation
- Broker relationship intelligence
- Market readiness scoring

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

## Usage

### Discovery Mode
1. Click "Start Discovery"
2. Enter a market trend (e.g., "protein is trending")
3. Select category and subcategory
4. Review discovered brands
5. Click "Assess Readiness" on promising brands

### Assessment Mode
1. Click "Assess Brand"
2. Enter brand name or website
3. Review comprehensive broker-readiness analysis

## Data Sources

- Real-time web research and scraping
- Brand intelligence from multiple sources
- Distribution and retail presence data
- Market trend analysis

## Requirements

- Python 3.8+
- Anthropic Claude API key
- Streamlit for web interface
- Pandas for data analysis

## Cost Control (Tokens)

This app uses Anthropic via API calls, which consume tokens. To keep costs low:

- Use a lower-cost model by setting `ANTHROPIC_MODEL` (default is `claude-3`)
- Keep prompts short and focused
- Re-run the app without repeatedly re-submitting the same brand
- Set a lower token limit via `ANTHROPIC_MAX_TOKENS` (default: 800)

If you see a "model not found" error, set `ANTHROPIC_MODEL` to one of the models you have access to (e.g. `claude-2`, `claude-3`, `claude-sonnet-4-6`).

Example:
```bash
export ANTHROPIC_MODEL=claude-3
export ANTHROPIC_MAX_TOKENS=600
```
## License

[Your License Here]