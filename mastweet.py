from mastodon import Mastodon
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1
import requests
import pickle
import os

# Mastodon API setup
mastodon = Mastodon(
    client_id=os.environ.get("MASTODON_CLIENT_ID"),
    client_secret = os.environ.get("MASTODON_CLIENT_SECRET"),
    access_token = os.environ.get("MASTODON_ACCESS_TOKEN"),
    api_base_url= os.environ.get("MASTODON_INSTANCE_URL"),
)

# Twitter API setup
consumer_key = os.environ.get("TWITTER_CONSUMER_KEY")
consumer_secret = os.environ.get("TWITTER_CONSUMER_SECRET")
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

def parse_toot(latest_toot_content, latest_toot_id):
    # Remove HTML tags from toot
    soup = BeautifulSoup(latest_toot_content, 'html.parser')
    latest_toot_text = soup.get_text()

    if latest_toot_text.find(os.environ.get("MASTODON_HASHTAG")) != -1:
        tweet_toot(latest_toot_text, latest_toot_id)


def connect_to_oauth(consumer_key, consumer_secret, acccess_token, access_token_secret):
    url = "https://api.twitter.com/2/tweets"
    auth = OAuth1(consumer_key, consumer_secret, acccess_token, access_token_secret)
    return url, auth

def upload_media(auth, image_url):
    media_upload_url = 'https://upload.twitter.com/1.1/media/upload.json'
img_data = requests.get(image_url).content
    media_upload_resp = requests.post(media_upload_url, files={'media': img_data}, auth=auth)
    media_id = media_upload_resp.json()['media_id_string']
    return media_id

def tweet_toot(latest_toot_text, latest_toot_id, image_url):

    url, auth = connect_to_oauth(
        consumer_key, consumer_secret, access_token, access_token_secret
    )
    media_id = upload_media(auth, image_url)
    payload = { "text": latest_toot_text, "media_ids" : media_id }
    request = requests.post(
        auth=auth, url=url, json=payload, headers={"Content-Type": "application/json"}
    )

    # Check response
    if request.status_code != 201:
        raise Exception(f"Request returned error: {request.status_code}, {request.text}")
    else:
        synced_toots.append(latest_toot_id)
        with open(pickle_name, 'wb') as f:
            pickle.dump(synced_toots, f)
        print("Successfully tweeted!")

def main():
    # Load list of already synced toots, if it exists in cache
    pickle_name = 'synced_toots.pkl'
    try:
        with open(pickle_name, 'rb') as f:
            synced_toots = pickle.load(f)
    except:
        synced_toots = []

    # Get latest Toots
    user = mastodon.account_verify_credentials()
    user_id = user['id']
    toots = mastodon.account_statuses(user_id, limit=1)
    latest_toot_content = toots[0]['content']
    latest_toot_id = toots[0]['id']
    print(toots[0])

    # Only proceed if toot has not been synced before
    # (This is actually redundant, as Twitter does not allow two identical Tweets to be posted)
    if latest_toot_id not in synced_toots:
        parse_toot(latest_toot_content, latest_toot_id)
    else:
        print('Toot already synced')

if __name__ == "__main__":
    main()