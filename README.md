# Music Data Aggregator

## Overview

**Music Data Aggregator** is a business-level data scraping application built with Python and Streamlit. It aggregates music information from multiple sources including Billboard, Wikipedia, and YouTube. The app scrapes the Billboard Hot 100 list, retrieves a brief summary from Wikipedia, and finds official music videos from YouTube. The aggregated data is then displayed interactively in a web interface and can be downloaded as an Excel file.

## Purpose

The purpose of this code is to:
- **Scrape Billboard Hot 100 Data:** Retrieve the latest top songs, including their rank, title, and artist, by scraping Billboard's website.
- **Fetch Wikipedia Summaries:** Get a short extract (first 200 characters) from Wikipedia for each song to provide context and background information.
- **Search YouTube for Music Videos:** Use the YouTube Data API to find official music videos for each song, and generate a clickable URL for easy viewing.
- **Display & Export Data:** Provide an interactive, web-based interface (using Streamlit) where users can view the aggregated data and download it as an Excel file.

## Uses

- **Music Insights & Trend Analysis:** Quickly obtain and review up-to-date information on popular songs, useful for music analysts, marketing teams, and radio stations.
- **Research & Reporting:** Combine data from multiple trusted sources (Billboard, Wikipedia, YouTube) to aid in trend analysis, reporting, or content creation.
- **Business Applications:** Integrate into dashboards or internal tools to provide decision-makers with consolidated and interactive music data.
- **User Interactivity:** The web-based interface makes it accessible without the need for desktop software, and custom inputs allow for a dynamic user experience.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/tannu64/musicapp.git
   cd musicapp
"# musicapp" 
