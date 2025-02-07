import os
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import urllib.parse
import pandas as pd
import streamlit as st

# ------------------------------
# Logging Setup
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='music_data.log',
    filemode='w'
)
logger = logging.getLogger()

# ------------------------------
# Load Environment Variables
# ------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# ------------------------------
# Define Functions
# ------------------------------

def scrape_billboard_hot_100():
    """
    Scrapes the Billboard Hot 100 page and returns a list of songs.
    Each song is represented as a dictionary with keys: 'rank', 'title', and 'artist'.
    """
    url = 'https://www.billboard.com/charts/hot-100/'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching Billboard page: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    songs = []
    
    # Select song rows (CSS selectors may change if Billboard updates their layout)
    for item in soup.select('.o-chart-results-list-row'):
        try:
            rank = item.select_one('.c-label').get_text(strip=True)
            title = item.select_one('.c-title').get_text(strip=True)
            artist = item.select_one('.c-label.a-no-trucate').get_text(strip=True)
            songs.append({'rank': rank, 'title': title, 'artist': artist})
        except AttributeError:
            continue  # Skip rows that don't match the expected structure
    
    return songs

def get_wikipedia_info(song_title, artist_name):
    """
    Fetches a short extract from Wikipedia about the song.
    Returns a truncated extract (first 200 characters + ellipsis) if found, or None.
    """
    search_query = f"{song_title} {artist_name} song"
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching Wikipedia search results: {e}")
        return None
    
    if 'query' in data and data['query'].get('search'):
        page_id = data['query']['search'][0]['pageid']
        content_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&pageids={page_id}&format=json"
        try:
            content_response = requests.get(content_url)
            content_response.raise_for_status()
            content_data = content_response.json()
            extract = content_data['query']['pages'][str(page_id)]['extract']
            return extract[:200] + '...'  # Truncate for brevity
        except requests.RequestException as e:
            logger.error(f"Error fetching Wikipedia page content: {e}")
            return None
    return None

def search_youtube_direct(query):
    """
    Uses a direct HTTP GET request to the YouTube Data API v3 to search for a video.
    Returns a dictionary with 'title', 'videoId', and 'thumbnailUrl' if found, else None.
    """
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": GOOGLE_API_KEY,
        "q": query,
        "part": "snippet",
        "type": "video",
        "maxResults": 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Error during YouTube search: {e}")
        return None

    if data.get('items'):
        video = data['items'][0]
        return {
            'title': video['snippet']['title'],
            'videoId': video['id']['videoId'],
            'thumbnailUrl': video['snippet']['thumbnails']['default']['url']
        }
    return None

def process_songs(num_songs):
    """
    Scrapes the Billboard Hot 100 and processes the top `num_songs` songs by fetching
    additional information from Wikipedia and YouTube.
    Returns a list of processed song dictionaries.
    """
    songs = scrape_billboard_hot_100()
    if not songs:
        st.error("No songs found!")
        return []
    
    processed_songs = []
    # Process the first num_songs songs
    for song in songs[:num_songs]:
        errors = []
        # Get Wikipedia info
        wiki_info = get_wikipedia_info(song['title'], song['artist'])
        if wiki_info:
            song['wikipedia_info'] = wiki_info
        else:
            song['wikipedia_info'] = "No info found."
            errors.append("Wikipedia info not found.")
        
        # Search YouTube for an official music video
        yt_query = f"{song['title']} {song['artist']} official music video"
        youtube_info = search_youtube_direct(yt_query)
        if youtube_info:
            song['youtube_video_id'] = youtube_info['videoId']
            # Create a full URL so users can click and watch the video
            song['youtube_video_url'] = f"https://www.youtube.com/watch?v={youtube_info['videoId']}"
            song['youtube_thumbnail'] = youtube_info['thumbnailUrl']
        else:
            song['youtube_video_id'] = "Not found"
            song['youtube_video_url'] = "Not found"
            song['youtube_thumbnail'] = "Not found"
            errors.append("YouTube video not found.")
        
        song['errors'] = "; ".join(errors)
        processed_songs.append(song)
    
    return processed_songs

# ------------------------------
# Streamlit App Interface
# ------------------------------

def main():
    st.title("Music Data Aggregator")
    st.write("This app scrapes the Billboard Hot 100, retrieves Wikipedia summaries, and searches YouTube for official music videos.")
    
    # Custom input: number of songs to process (from 1 to 50, default is 10)
    num_songs = st.slider("Number of Songs to Process", min_value=1, max_value=50, value=10)
    
    if st.button("Process Songs"):
        with st.spinner("Processing songs..."):
            processed_songs = process_songs(num_songs)
        
        if processed_songs:
            # Convert the data into a DataFrame and display it
            df = pd.DataFrame(processed_songs)
            st.write("### Processed Song Data", df)
            
            # Save the DataFrame to an Excel file and provide a download button
            output_file = "music_data.xlsx"
            try:
                df.to_excel(output_file, index=False)
                st.success(f"Data saved to {output_file}")
                with open(output_file, "rb") as file:
                    st.download_button("Download Excel File", data=file, file_name=output_file,
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Error saving Excel file: {e}")
                logger.error(f"Error saving data to Excel: {e}")

if __name__ == '__main__':
    main()

