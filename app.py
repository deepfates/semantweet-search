from shiny import App, render, ui
import lancedb
import json
import calendar
import pandas as pd
from query import create_query
from tweet_utils import parse_tweets
from shinyswatch import theme

theme.morph()

def get_handle(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        json_str = content.replace('window.YTD.account.part0 = ', '').strip()
        data = json.loads(json_str)
        username = data[0]['account']['username']
        return username

# Specify the path to your 'account.js' file 

file_path = 'twitter-archive/data/account.js'
default_username = get_handle(file_path)
print(f"Username: {default_username}")


app_ui = ui.page_fluid(
    ui.panel_title("Twitter Archive Search"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_text("search", "Search Query", placeholder="Enter search query"),
            ui.input_text("username", "From username", value=default_username),
            ui.input_numeric("year_from", "From Year", value=2006, min=2006, max=2024),
            ui.input_select("month_from", "From Month", choices=list(calendar.month_abbr)[1:]),
                        ui.input_numeric("year_to", "To Year", value=2024, min=2006, max=2024),
            ui.input_select("month_to", "To Month", choices=list(calendar.month_abbr)[1:]),
            ui.input_numeric("likes_greater_than", "Likes Greater Than", value=0),
            ui.input_numeric("likes_less_than", "Likes Less Than", value=0),
            ui.input_numeric("retweets_greater_than", "Retweets Greater Than", value=0),
            ui.input_numeric("retweets_less_than", "Retweets Less Than", value=0),
            ui.input_checkbox("media_only", "Media Only", value=False),
            ui.input_checkbox("link_only", "Link Only", value=False),
        ),
        ui.panel_main(
            ui.output_data_frame("results")
        ),
    ),
)

def server(input, output, session):
    # Connect to LanceDB and open the table
    db = lancedb.connect("data/bge_embeddings")
    table = db.open_table("bge_table")

    @output
    @render.data_frame
    def results():
        search_query = input.search()
        username = input.username()
        year_from = input.year_from()
        month_from = input.month_from()
        year_to = input.year_to()
        month_to = input.month_to()
        likes_greater_than = input.likes_greater_than()
        likes_less_than = input.likes_less_than()
        retweets_greater_than = input.retweets_greater_than()
        retweets_less_than = input.retweets_less_than()
        media_only = input.media_only()
        link_only = input.link_only()

        query = create_query(year_from, month_from, year_to, month_to, media_only, likes_greater_than, likes_less_than, retweets_greater_than, retweets_less_than, link_only)
        
        print("query: ", query)

        if len(search_query) > 0:
            docs = table.search(search_query, query_type="hybrid").where(query, prefilter=True).limit(50).to_pandas()
        else:
            print("empty search query")
            docs = table.search().where(query).limit(100).to_pandas()
      
        metadata_list = docs['metadata'].tolist()

        tweets = parse_tweets(metadata_list, link_only, username)

        def calculate_sort_score(likes, retweets):
            likes = likes or 0
            retweets = retweets or 0
            return likes + retweets

        # if no search query, just want to see by likes
        if len(search_query) == 0 and (likes_greater_than or likes_less_than or retweets_greater_than or retweets_less_than):
            tweets.sort(key=lambda x: calculate_sort_score(x['likes'], x['retweets']), reverse=True)

        print(len(tweets))
        return pd.DataFrame(tweets)

app = App(app_ui, server)
