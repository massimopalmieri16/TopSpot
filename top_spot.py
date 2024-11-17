import math
import requests
import streamlit as st
from streamlit_oauth import OAuth2Component
from streamlit_oauth import StreamlitOauthError

# Get spotify app id and secret from streamlit secrets
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets['CLIENT_SECRET']
REDIRECT_URI = st.secrets['REDIRECT_URI']

# Constants
PROFILE_URL = "https://api.spotify.com/v1/me"
TOP_ITEMS_URL = "https://api.spotify.com/v1/me/top"
AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-top-read"

def user_profile(access_token):
    r = requests.get(url=PROFILE_URL, headers={"Authorization": f"Bearer {access_token}"})
    if r.status_code == 200:
        json_response = r.json()
        st.success(f"Successfully logged as **{json_response["display_name"]}**", icon="✅")
        st.button("Logout", on_click=logout, use_container_width=True)
    else:
        st.error(r.json())

def logout():
    st.session_state.clear()

def user_top_items(access_token):
    # Inputs
    type = st.radio("Type", ["artists", "tracks"], horizontal=True)
    time_range = st.radio("Time range", ["short_term", "medium_term", "long_term"], horizontal=True, captions=["Last 4 weeks","Last 6 months","Last year"],)
    num_items = st.radio("Number of items", [10, 20, 50, 100, 200, 500, 1000], horizontal=True)

    url = f"{TOP_ITEMS_URL}/{type}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get items from spotify api in chunks of 50
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
                    table.append({"Track": item["name"], "Artist": item["artists"][0]["name"], "Album": item["album"]["name"]})
        else:
            st.write("Error")
            st.write(r.json())
            break

        offset+=50

    # Show data as table
    st.table(table)

def main():
    st.set_page_config(page_title="TopSpot")
    st.title("TopSpot")
    st.subheader("Your Spotify top artists and tracks")
    
    # Create OAuth2Component instance
    oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, TOKEN_URL, None)

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
                # Ignore access denied error, in case user cancel auth process
                pass
            else:
                raise
    else:
        # If token exists in session state, show profile and top items
        token = st.session_state['token']
        user_profile(token["access_token"])
        st.divider()
        user_top_items(token["access_token"])

    # Footer
    st.divider()
    st.info(
    """
    [Check the source code on GitHub](https://github.com/massimopalmieri16/TopSpot)
    """,
    icon="🧑‍💻",
)

if __name__ == "__main__":
    main()
