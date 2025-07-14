from wordcloud import WordCloud
from io import BytesIO
import base64
import re
from collections import Counter

def generate_location_wordcloud(df, country_name):
    removal_words = {
        'district', 'districts', 'province', 'provinces', 'state', 'states',
        'city', 'cities', 'area', 'areas', 'region', 'regions', 'division', 'divisions',
        'north', 'south', 'east', 'west', 'central', 'valley', 'coast', 'river', 'basin',
        'border', 'zone', 'of', 'the', 'near', 'unknown'
    }

    country_df = df[df['Country_x'] == country_name]
    cleaned_words = []

    for loc in country_df['Location'].dropna():
        loc = str(loc)
        loc = re.sub(r'[()]', '', loc)     # Remove parentheses but keep content
        loc = loc.replace(',', ' ')
        tokens = loc.split()
        tokens = [t.lower() for t in tokens if t.lower() not in removal_words and len(t) > 1]
        cleaned_words.extend(tokens)

    # Count word frequencies
    word_freq = Counter(cleaned_words)

    # Generate WordCloud
    wc = WordCloud(
        background_color='white',
        width=1080,
        height=360,
        colormap='viridis',
        max_words=200
    ).generate_from_frequencies(word_freq)

    # Save to base64 image
    img_bytes = BytesIO()
    wc.to_image().save(img_bytes, format='PNG')
    img_bytes.seek(0)
    encoded_img = base64.b64encode(img_bytes.getvalue()).decode()

    return f'data:image/png;base64,{encoded_img}'
