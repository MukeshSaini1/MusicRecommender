import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch the poster and song URLs
def fetch_poster_and_urls(music_title):
    try:
        response = requests.get(f"https://saavn.dev/api/search/songs?query={music_title}")
        response.raise_for_status()
        data = response.json()

        if 'data' in data and isinstance(data['data']['results'], list) and len(data['data']['results']) > 0:
            result = data['data']['results'][0]
            poster_url = result['image'][2]['url']
            download_urls = result['downloadUrl']

            # Extract URLs and sort by quality (highest quality first)
            urls = {quality['quality']: quality['url'] for quality in download_urls}
            sorted_qualities = sorted(urls.keys(), key=lambda x: int(x.replace('kbps', '')), reverse=True)
            default_quality = sorted_qualities[0] if sorted_qualities else None
            default_url = urls.get(default_quality)

            return poster_url, default_url
        else:
            raise ValueError("Unexpected data format or no results found.")

    except requests.exceptions.RequestException as e:
        st.error(f"API request error: {e}")
        return "https://i.postimg.cc/0QNxYz4V/social.png", None
    except (IndexError, KeyError, ValueError) as e:
        st.error(f"Error fetching poster or URL: {e}")
        return "https://i.postimg.cc/0QNxYz4V/social.png", None

# Function to recommend similar songs
def recommend(musics):
    music_index = music[music['title'] == musics].index[0]
    distances = similarity[music_index]
    music_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_music = []
    recommended_music_poster = []
    recommended_music_urls = []
    for i in music_list:
        music_title = music.iloc[i[0]].title
        poster, url = fetch_poster_and_urls(music_title)
        recommended_music.append(music_title)
        recommended_music_poster.append(poster)
        recommended_music_urls.append(url)
    return recommended_music, recommended_music_poster, recommended_music_urls

# Load data
music_dict = pickle.load(open('songdata.pkl', 'rb'))
music = pd.DataFrame(music_dict)
similarity = pickle.load(open('similarities.pkl', 'rb'))

# App title and header
st.title('Music Recommendation System')
st.write("Discover new music based on your favorite tracks. Select a song to get recommendations!")

# Display the selectbox for user to choose a music they like
selected_music_name = st.selectbox('Select a music you like', music['title'].values, index=0)

# Display recommendations when button is clicked
if st.button('Get Recommendations'):
    names, posters, urls_list = recommend(selected_music_name)

    st.write("### Recommended Songs")

    # Create a single container for recommendations
    with st.container():
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.image(posters[i], caption=names[i], use_column_width='auto')
                if urls_list[i]:
                    st.audio(urls_list[i], format='audio/mp4')
                    #st.markdown(f"[Download High Quality]({urls_list[i]})", unsafe_allow_html=True)

    # Adjust font size using markdown
    st.markdown("""
    <style>
    .stText {
        font-size: 18px;
    }
    .stImage {
        margin: 0 auto;
    }
    .stButton {
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
