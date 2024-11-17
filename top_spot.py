import math
import requests
import streamlit as st
from streamlit_oauth import OAuth2Component
from streamlit_oauth import StreamlitOauthError

def spotify_top_items(access_token):
    type = st.radio("Type", ["artists", "tracks"], horizontal=True)
    time_range = st.radio("Time range", ["short_term", "medium_term", "long_term"], horizontal=True, captions=["Last 4 weeks","Last 6 months","Last year"],)
    num_items = st.radio("Number of items", [10, 20, 50, 100, 200, 500, 1000], horizontal=True)

    url = f"https://api.spotify.com/v1/me/top/{type}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    num_iter = math.ceil(num_items / 50)
    table = []
    offset = 0
    for i in range(num_iter):
        if num_items > 50:
            curr_items = 50
        else:
            curr_items = num_items

        params = {"time_range": time_range, "limit": curr_items, "offset": offset}
        r = requests.get(url=url, params=params, headers=headers)
        if r.status_code == 200:
            for item in r.json()["items"]:
                if type == "artists":
                    table.append({"Artist": item["name"], "Genres": ", ".join(item["genres"]), "Popularity": item["popularity"]})
                else:
                    table.append({"Track": item["name"], "Album": item["album"]["name"], "Artist": item["artists"][0]["name"]})
        else:
            st.write("Error")
            st.write(r.json())
            break

        offset+=50

    st.table(table)


def main():
    
    st.title("TopSpot")
    st.header("Your Spotify top artists and tracks")
    
    # Set environment variables
    AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    REFRESH_TOKEN_URL = "https://accounts.spotify.com/api/token"
    REVOKE_TOKEN_URL = None
    CLIENT_ID = st.secrets["CLIENT_ID"]
    CLIENT_SECRET = st.secrets['CLIENT_SECRET']
    REDIRECT_URI = 'http://localhost:8501/component/streamlit_oauth.authorize_button/index.html'
    SCOPE = "user-top-read"
    
    # Create OAuth2Component instance
    oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)

    # Check if token exists in session state
    if 'token' not in st.session_state:
        # If not, show authorize button
        try:
            result = oauth2.authorize_button("Login with your Spotify account", REDIRECT_URI, SCOPE, pkce="S256", use_container_width=True)
            if result and 'token' in result:
                # If authorization successful, save token in session state
                st.session_state.token = result.get('token')
                st.rerun()
        except StreamlitOauthError as ex:
            if 'access_denied' in str(ex.args):
                pass
            else:
                raise
    else:
        # If token exists in session state, show the token
        token = st.session_state['token']
        spotify_top_items(token["access_token"])


if __name__ == "__main__":
    main()
