import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fuzzywuzzy import fuzz
import re
import numpy as np
noise_words_1 = ['near', 'province', 'district', 'cities', 'city', 'state', 'municipality', 'region']
noise_words = noise_words_1.copy()  # Create a copy to avoid modifying during iteration

for word in noise_words_1:
    noise_words.append(word[0].upper() + word[1:])

def scale_marker_sizes(deaths_series, min_size=10, max_size=100, power=2.5):
    min_deaths = deaths_series.min()
    max_deaths = deaths_series.max()
    
    normalized = (deaths_series - min_deaths) / (max_deaths - min_deaths)
    scaled = min_size + (normalized ** power) * (max_size - min_size)
    return scaled


def plot_disasters_on_map(disasters_df, cities_df, country_name, year, min_deaths=1, mapbox_style='open-street-map'):
    """
    Plot natural disasters on a country map with markers sized by death toll using Mapbox.
    
    Parameters:
    -----------
    disasters_df : pandas.DataFrame
        Natural disasters dataset
    cities_df : pandas.DataFrame
        Cities dataset with coordinates
    country_name : str
        Name of the country to visualize
    year : int
        Year to filter disasters
    min_deaths : int, default=1
        Minimum number of deaths to include in visualization
    mapbox_style : str, default='open-street-map'
        Mapbox style ('open-street-map', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', etc.)
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Interactive map visualization
    """
    
    # Filter disasters for the specified country and year
    country_disasters = disasters_df[
        (disasters_df['Country_x'].str.contains(country_name, case=False, na=False)) &
        (disasters_df['Start Year'] == year) &
        (disasters_df['Total Deaths'].notna()) &
        (disasters_df['Total Deaths'] >= min_deaths)
    ].copy()
    
    if country_disasters.empty:
        print(f"No disasters found for {country_name} in {year} with at least {min_deaths} deaths")
        return None
    
    # Filter cities for the specified country
    country_cities = cities_df[
        cities_df['country_name'].str.contains(country_name, case=False, na=False)
    ].copy()
    
    if country_cities.empty:
        print(f"No cities found for {country_name}")
        return None
    
    print(f"Processing {len(country_disasters)} disasters for {country_name} in {year}...")
    print(f"Available cities in {country_name}: {len(country_cities)}")
    
    # Create lookup dictionaries for faster matching
    city_lookup = {}
    state_lookup = {}
    
    # Build lookup dictionaries with coordinate validation
    for idx, row in country_cities.iterrows():
        if pd.notna(row['name']) and pd.notna(row['latitude']) and pd.notna(row['longitude']):
            city_name = str(row['name']).lower()
            if -90 <= row['latitude'] <= 90 and -180 <= row['longitude'] <= 180:
                city_lookup[city_name] = (row['latitude'], row['longitude'], row['name'])
        
        if pd.notna(row['state_name']) and pd.notna(row['latitude']) and pd.notna(row['longitude']):
            state_name = str(row['state_name']).lower()
            if -90 <= row['latitude'] <= 90 and -180 <= row['longitude'] <= 180:
                state_lookup[state_name] = (row['latitude'], row['longitude'], row['state_name'])
    def clean_location_string(location_str):
      if pd.isna(location_str):
          return []
      
      # Lowercase and remove content in parentheses
      location_str = location_str.lower()
      location_str = re.sub(r'\(.*?\)', '', location_str)

      # Remove noise keywords
  
      for word in noise_words:
          location_str = location_str.replace(word, '')
      print(location_str)
      # Remove punctuation and split
      location_str = re.sub(r'[^\w\s,]', '', location_str)
      tokens = [t.strip() for t in location_str.split(',') if len(t.strip()) >= 3]
      
      return tokens

    # Function to parse location and find best matching city
    def find_city_coordinates(location_str, threshold=85):
      tokens = clean_location_string(location_str)
      
      for token in tokens:
          if token in city_lookup:
              lat, lon, name = city_lookup[token]
              return lat, lon, name
          if token in state_lookup:
              lat, lon, name = state_lookup[token]
              return lat, lon, name
      
      best_match = None
      best_score = 0
      best_coords = (None, None)
      
      for token in tokens:
          if len(token) < 3:
              continue
          for city_name, (lat, lon, name) in city_lookup.items():
              if city_name.startswith(token[0]):
                  score = fuzz.ratio(token, city_name)
                  if score > best_score and score > threshold:
                      best_score = score
                      best_match = name
                      best_coords = (lat, lon)
          for state_name, (lat, lon, name) in state_lookup.items():
              if state_name.startswith(token[0]):
                  score = fuzz.ratio(token, state_name)
                  if score > best_score and score > threshold:
                      best_score = score
                      best_match = name
                      best_coords = (lat, lon)
      
      return best_coords[0], best_coords[1], best_match

    
    # Find coordinates for each disaster
    disaster_coords = []
    for idx, row in country_disasters.iterrows():
        # Try existing coordinates first
        if (pd.notna(row['Latitude']) and pd.notna(row['Longitude']) and 
            -90 <= row['Latitude'] <= 90 and -180 <= row['Longitude'] <= 180):
            lat, lon, matched_city = row['Latitude'], row['Longitude'], "Direct coordinates"
        else:
            lat, lon, matched_city = find_city_coordinates(row['Location'])
        
        if (lat is not None and lon is not None and 
            -90 <= lat <= 90 and -180 <= lon <= 180):
            
            disaster_coords.append({
                'disaster_id': row['DisNo.'],
                'disaster_type': row['Disaster Type'],
                'location': row['Location'],
                'matched_city': matched_city,
                'latitude': lat,
                'longitude': lon,
                'deaths': row['Total Deaths'],
                'total_damage': row['Total Damage (\'000 US$)'] * 1000 if pd.notna(row['Total Damage (\'000 US$)']) else 0,
            })
        else:
            print(f"Invalid coordinates for {row['Location']}: lat={lat}, lon={lon}")
    
    if not disaster_coords:
        print(f"No valid coordinates found for disasters in {country_name} for {year}")
        return None
    
    # Create DataFrame for plotting
    plot_df = pd.DataFrame(disaster_coords)
    
    # Calculate marker sizes (proportional to deaths)
    max_deaths = plot_df['deaths'].max()
    min_deaths_plot = plot_df['deaths'].min()

    # Normalize deaths to marker size (40-120 pixel range for much better visibility)
    if max_deaths > min_deaths_plot:
        # plot_df['marker_size'] = plot_df['deaths'].apply(map_size)
        plot_df['marker_size'] = 10*scale_marker_sizes(plot_df['deaths'])

        # plot_df['marker_size'] = plot_df['deaths'].apply(lambda d: np.log10(d + 1) * 1000 + 60)  # tweak constants for visibility
    else:
        plot_df['marker_size'] = 60
    
    # Create color mapping for disaster types
    disaster_types = plot_df['disaster_type'].unique()
    colors = px.colors.qualitative.Set1[:len(disaster_types)]
    color_discrete_map = dict(zip(disaster_types, colors))
    
    # Calculate map center
    center_lat = plot_df['latitude'].mean()
    center_lon = plot_df['longitude'].mean()
    
    # Calculate zoom level based on coordinate spread
    lat_range = plot_df['latitude'].max() - plot_df['latitude'].min()
    lon_range = plot_df['longitude'].max() - plot_df['longitude'].min()
    max_range = max(lat_range, lon_range)
    
    if max_range > 20:
        zoom = 3
    elif max_range > 10:
        zoom = 4
    elif max_range > 5:
        zoom = 5
    elif max_range > 2:
        zoom = 6
    else:
        zoom = 7
    
    # Create the figure
    fig = go.Figure()
    
    # Add traces for each disaster type
    for disaster_type in disaster_types:
        type_data = plot_df[plot_df['disaster_type'] == disaster_type]
        
        # Create hover text
        hover_text = []
        for _, row in type_data.iterrows():
            damage_text = f"${row['total_damage']:,.0f}" if row['total_damage'] > 0 else "Not available"
            
            # Limit location display to first 4 parts if it's a comma-separated list
            location_parts = str(row['location']).split(',')
            if len(location_parts) > 4:
                limited_location = ', '.join(location_parts[:4]) + '...'
            else:
                limited_location = row['location']
            
            hover_text.append(
                f"<b>{limited_location}</b><br>"
                f"Type: {row['disaster_type']}<br>"
                f"Deaths: {row['deaths']:,}<br>"
                f"Damage: {damage_text}"
            )
        
        fig.add_trace(go.Scattermapbox(
            lat=type_data['latitude'],
            lon=type_data['longitude'],
            mode='markers',
            marker=dict(
                size=type_data['marker_size'],
                color=color_discrete_map[disaster_type],
                sizemode='area',
                opacity=0.8
            ),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            name=disaster_type
        ))
    
    # Update layout with mapbox
    fig.update_layout(
        mapbox=dict(
            style=mapbox_style,
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom
        ),
        title=f'Natural Disasters in {country_name} ({year})<br>'
              f'<sub>Total Events: {len(plot_df)} | Total Deaths: {plot_df["deaths"].sum():,}</sub>',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        height=700,
        margin=dict(r=0, t=60, l=0, b=0)
    )
    
    return fig

# Example usage:
# fig = plot_disasters_on_map(disasters_df, cities_df, "United States", 2005, mapbox_style='open-street-map')
# fig.show()

# Alternative map styles you can try:
# 'open-street-map' (default, free)
# 'carto-positron' (clean, light)
# 'carto-darkmatter' (dark theme)
# 'stamen-terrain' (topographic)
# 'stamen-toner' (high contrast)

def get_disaster_summary(disasters_df, cities_df, country_name, year):
    """
    Get summary statistics for disasters in a country for a given year.
    """
    country_disasters = disasters_df[
        (disasters_df['Country_x'].str.contains(country_name, case=False, na=False)) &
        (disasters_df['Start Year'] == year)
    ].copy()
    
    if country_disasters.empty:
        return f"No disasters found for {country_name} in {year}"
    
    summary = {
        'Total Events': len(country_disasters),
        'Total Deaths': country_disasters['Total Deaths'].sum(),
        'Total Affected': country_disasters['Total Affected'].sum(),
        'Disaster Types': country_disasters['Disaster Type'].value_counts().to_dict(),
        'Most Deadly Event': country_disasters.loc[country_disasters['Total Deaths'].idxmax(), 'Event Name'] if country_disasters['Total Deaths'].max() > 0 else 'None',
        'Total Economic Damage (USD)': country_disasters['Total Damage (\'000 US$)'].sum() * 1000 if country_disasters['Total Damage (\'000 US$)'].notna().any() else 'Not available'
    }
    
    return summary




# Example usage:
# city = pd.read_csv("cities.csv")
# fig = plot_disasters_on_map_with_slider(data, city, "India", min_deaths=1, mapbox_style='open-street-map', power=2.5)

# fig = create_interactive_disasters_map(data, city)
# fig.show()
# fig = plot_disasters_on_map(data, city, "India", 2010, min_deaths=1, mapbox_style='carto-darkmatter')
# # fig = plot_disasters_on_map(data, city, "India", 2004, "carto-darkmatter")
# # Alternative map styles you can try:
# # 'open-street-map' (default, free)
# # 'carto-positron' (clean, light)
# # 'carto-darkmatter' (dark theme)
# # 'stamen-terrain' (topographic)
# # 'stamen-toner' (high contrast)
# fig.show()