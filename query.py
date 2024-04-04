import calendar

def get_month_number(month_name):
    """Return the month number for a three-letter month abbreviation."""
    if month_name:
        try:
            return list(calendar.month_abbr).index(month_name.title())
        except ValueError:
            return None
    return None

def create_query(year_from, month_from, year_to, month_to, media_only, likes_greater_than, likes_less_than, retweets_greater_than, retweets_less_than, link_only):
    # Convert month abbreviations to numbers
    month_from_number = get_month_number(month_from)
    month_to_number = get_month_number(month_to)
    
    # Create the query string based on the available inputs
    query_parts = []
    if year_from:
        query_parts.append(f"year >= {year_from}")
    if year_to:
        query_parts.append(f"year <= {year_to}")
    if month_from_number:
        query_parts.append(f"month >= {month_from_number}")
    if month_to_number:
        query_parts.append(f"month <= {month_to_number}")
    
    if media_only:
        query_parts.append(f"media_present = {1}")

    if link_only:
        query_parts.append(f"link_present = {1}")

    if likes_greater_than:
        query_parts.append(f"likes >= {likes_greater_than}")

    if likes_less_than:
        query_parts.append(f"likes <= {likes_less_than}")

    if retweets_greater_than:
        query_parts.append(f"retweets >= {retweets_greater_than}")

    if retweets_less_than:
        query_parts.append(f"retweets <= {retweets_less_than}")
    
    return " and ".join(query_parts)
