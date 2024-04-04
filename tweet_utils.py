import re
import json
import datetime

def is_twitter_url(url):
    # filtering out quote tweets
    twitter_domains = [
        'https://twitter.com',
        'http://twitter.com',
        'https://t.co',
        'http://t.co',
        'https://pbs.twimg.com',
        'https://video.twimg.com',
        'https://x.com',
        'http://x.com'
    ]
    return any(url.startswith(domain) for domain in twitter_domains)

def get_non_twitter_url(tweet):
    entities = tweet.get('entities')
    url_list = []
    if entities:
        urls = entities.get('urls')
        if urls:
            for url in urls:
                expanded_url = url.get('expanded_url')
                if expanded_url and not is_twitter_url(expanded_url):
                    url_list.append(expanded_url)
    return url_list

def parse_tweets(metadata_list, link_only, username='username'):
    parsed_tweets = []
    for json_str in metadata_list:
        try:
            tweet = json.loads(json_str)  # Assuming json_str is a JSON string of the tweet
            likes = tweet.get('favorite_count')
            retweets = tweet.get('retweet_count')
            
            # get the tweet id to form url
            tweet_id = tweet.get('id_str', 'No ID available')

            url_list = []
            if(link_only):
                url_list = get_non_twitter_url(tweet)

            print(url_list)
            
            # Parse the timestamp string into a datetime object
            dt_object = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    
            # Extract the year, day, and month
            year = dt_object.strftime('%Y') 
            day = dt_object.strftime('%d')   
            month = dt_object.strftime('%b') 

            # extract text and remove https://t.co url
            full_text = tweet.get('full_text', 'No text available')
            pattern = r'https?://t\.co/[a-zA-Z0-9]+'  
            full_text = re.sub(pattern, '', full_text)
            full_text = full_text + f"\n {month},{day} {year}"
            
            print(full_text)

            username_handle = tweet.get('user', {}).get('screen_name', 'No username available')
            
            # Initialize lists to store media URLs and IDs (if any)
            media_urls = []
            image_ids = []
            
            # Check for media in both 'entities' and 'extended_entities'
            entities = tweet.get('entities', {})
            extended_entities = tweet.get('extended_entities', {})
            
            # Function to extract media
            def extract_media(media_list):
                for media in media_list:
                    if media['type'] == 'photo':  # Ensure it's an image
                        media_url = media.get('media_url_https', '')
                        image_id = media.get('id_str', '')
                        if media_url and image_id:  # If a URL and ID are found, add them to the lists
                            media_urls.append(media_url)
                            image_ids.append(image_id)
            
            # First, check in 'extended_entities'
            if 'media' in extended_entities:
                extract_media(extended_entities['media'])
            
            # Then, also check in 'entities' for any additional images
            elif 'media' in entities:
                extract_media(entities['media'])
            
            # Append the extracted information to the list
            parsed_tweets.append({
                'url':f'twitter.com/{username}/status/{tweet_id}',
                'tweet_id': tweet_id,
                'text': full_text,
                'media_urls': media_urls,
                'image_ids': image_ids,
                'handle': username_handle,
                'url_list': url_list,
                'likes': likes,
                'retweets': retweets
            })
        
        except json.JSONDecodeError:
            print("Error decoding JSON")
        except KeyError as e:
            print(f"Key error in extracting data: {e}")    
    return parsed_tweets
