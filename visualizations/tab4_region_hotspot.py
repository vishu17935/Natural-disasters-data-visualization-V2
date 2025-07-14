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

# import os
def plot_disasters_on_map(disasters_df, cities_df, country_name, year=None, min_deaths=1, mapbox_style='open-street-map'):
    """
    Plot natural disasters on a country map with markers sized by death toll.
    If `year` is None, plot all disasters across years.
    """

    # Filter disasters
    disaster_filter = (
        (disasters_df['Country_x'].str.contains(country_name, case=False, na=False)) &
        (disasters_df['Total Deaths'].notna()) &
        (disasters_df['Total Deaths'] >= min_deaths)
    )
    if year is not None:
        disaster_filter &= (disasters_df['Start Year'] == year)

    country_disasters = disasters_df[disaster_filter].copy()

    if country_disasters.empty:
        print(f"No disasters found for {country_name} {'in ' + str(year) if year else ''}")
        return None

    # Filter cities
    country_cities = cities_df[cities_df['country_name'].str.contains(country_name, case=False, na=False)].copy()
    if country_cities.empty:
        print(f"No cities found for {country_name}")
        return None

    # Lookup dictionaries
    city_lookup = {}
    state_lookup = {}
    for _, row in country_cities.iterrows():
        if pd.notna(row['name']) and pd.notna(row['latitude']) and pd.notna(row['longitude']):
            city_lookup[row['name'].lower()] = (row['latitude'], row['longitude'], row['name'])
        if pd.notna(row['state_name']):
            state_lookup[row['state_name'].lower()] = (row['latitude'], row['longitude'], row['state_name'])

    # Location parser
    def find_city_coordinates(location_str, threshold=85):
        if pd.isna(location_str):
            return None, None, None
        location_clean = re.sub(r'\([^)]*\)', '', location_str)  # remove parenthesis
        location_clean = re.sub(r'\b(cities|province|district|city|state|municipality|region|near)\b', '', location_clean, flags=re.IGNORECASE)
        parts = re.split(r'[,\|]', location_clean)
        parts = [p.strip().lower() for p in parts if len(p.strip()) >= 3]

        for part in parts:
            if part in city_lookup:
                lat, lon, name = city_lookup[part]
                return lat, lon, name
            if part in state_lookup:
                lat, lon, name = state_lookup[part]
                return lat, lon, name

        # fallback fuzzy match
        best_score, best_coords, best_name = 0, (None, None), None
        for part in parts:
            for name, (lat, lon, n) in {**city_lookup, **state_lookup}.items():
                score = fuzz.ratio(part, name)
                if score > best_score and score >= threshold:
                    best_score = score
                    best_coords = (lat, lon)
                    best_name = n
        return (*best_coords, best_name)

    # Resolve coordinates
    disaster_coords = []
    for _, row in country_disasters.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            lat, lon, match = row['Latitude'], row['Longitude'], "Direct"
        else:
            lat, lon, match = find_city_coordinates(row['Location'])

        if lat is not None and lon is not None:
            disaster_coords.append({
                'disaster_id': row['DisNo.'],
                'disaster_type': row['Disaster Type'],
                'location': row['Location'],
                'matched_city': match,
                'latitude': lat,
                'longitude': lon,
                'deaths': row['Total Deaths'],
                'year': row['Start Year'],
                'total_damage': row['Total Damage (\'000 US$)'] * 1000 if pd.notna(row['Total Damage (\'000 US$)']) else 0,
            })

    if not disaster_coords:
        print("No valid coordinates found.")
        return None

    df_plot = pd.DataFrame(disaster_coords)
    df_plot['marker_size'] = 10 * scale_marker_sizes(df_plot['deaths'])
    def limit_location_parts(loc_str, max_parts=4):
      if pd.isna(loc_str):
          return ''
      parts = [p.strip() for p in str(loc_str).split(',')]
      return ', '.join(parts[:max_parts]) + ('...' if len(parts) > max_parts else '')

    df_plot['short_location'] = df_plot['location'].apply(limit_location_parts)

    # Add customdata for click events - just the disaster_id value, not wrapped in a list
    df_plot['customdata'] = df_plot['disaster_id']
    
    fig = px.scatter_mapbox(
    df_plot,
    lat='latitude',
    lon='longitude',
    color='disaster_type',
    size='marker_size',
    size_max=60,
    hover_data={
        'short_location': True,  # Replaces full location
        'deaths': True,
        'total_damage': True,
        'year': True,
    },
    custom_data=['customdata'],  # Add customdata for click events
    zoom=4,
    mapbox_style=mapbox_style,
    animation_frame=None,
    title=f"Disasters in {country_name} {'in ' + str(year) if year else '(All Years)'} Total Events: {len(df_plot)}, Total Deaths: {df_plot['deaths'].sum()}",
    height=700
  )
    fig.update_layout(
    legend=dict(
        orientation="v",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255,255,255,0.7)",  # Semi-transparent background over map
        bordercolor="black",
        borderwidth=0.5,
    ),
    margin=dict(t=50, b=10, l=10, r=10),  # Keep tight margins
    height=700,
)


    return fig

def plot_disasters_on_map_simple(disasters_df, country_name, year, min_deaths=1, mapbox_style='open-street-map'):
    """
    Plot natural disasters on a country map with markers sized by death toll using Mapbox.
    This version works with disaster data that already has Latitude and Longitude columns.
    
    Parameters:
    -----------
    disasters_df : pandas.DataFrame
        Natural disasters dataset with Latitude and Longitude columns
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
        (disasters_df['Total Deaths'] >= min_deaths) &
        (disasters_df['Latitude'].notna()) &
        (disasters_df['Longitude'].notna())
    ].copy()
    
    if country_disasters.empty:
        print(f"No disasters found for {country_name} in {year} with at least {min_deaths} deaths and valid coordinates")
        return None
    
    print(f"Processing {len(country_disasters)} disasters for {country_name} in {year}...")
    
    # Create DataFrame for plotting with coordinates
    plot_df = country_disasters[['DisNo.', 'Disaster Type', 'Location', 'Latitude', 'Longitude', 
                                'Total Deaths', 'Total Damage (\'000 US$)']].copy()
    
    # Rename columns for consistency
    plot_df = plot_df.rename(columns={
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Total Deaths': 'deaths',
        'Total Damage (\'000 US$)': 'total_damage'
    })
    
    # Convert damage to USD (multiply by 1000)
    plot_df['total_damage'] = plot_df['total_damage'] * 1000
    
    # Calculate marker sizes (proportional to deaths)
    max_deaths = plot_df['deaths'].max()
    min_deaths_plot = plot_df['deaths'].min()

    # Normalize deaths to marker size
    if max_deaths > min_deaths_plot:
        plot_df['marker_size'] = 10 * scale_marker_sizes(plot_df['deaths'])
    else:
        plot_df['marker_size'] = 60
    
    # Create color mapping for disaster types
    disaster_types = plot_df['Disaster Type'].unique()
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
        type_data = plot_df[plot_df['Disaster Type'] == disaster_type]
        
        # Create hover text
        hover_text = []
        for _, row in type_data.iterrows():
            damage_text = f"${row['total_damage']:,.0f}" if row['total_damage'] > 0 else "Not available"
            
            # Limit location display to first 4 parts if it's a comma-separated list
            location_parts = str(row['Location']).split(',')
            if len(location_parts) > 4:
                limited_location = ', '.join(location_parts[:4]) + '...'
            else:
                limited_location = row['Location']
            
            hover_text.append(
                f"<b>{limited_location}</b><br>"
                f"Type: {row['Disaster Type']}<br>"
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
        title=f'<br>'
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

# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# from fuzzywuzzy import fuzz
# import re
# import numpy as np
# noise_words_1 = ['near', 'province', 'district', 'cities', 'city', 'state', 'municipality', 'region']
# noise_words = noise_words_1.copy()  # Create a copy to avoid modifying during iteration
# import os

# root_path = os.path.dirname(os.path.abspath(__file__))
# # print(root_path)

# for word in noise_words_1:
#     noise_words.append(word[0].upper() + word[1:])

# def scale_marker_sizes(deaths_series, min_size=10, max_size=100, power=2.5):
#     min_deaths = deaths_series.min()
#     max_deaths = deaths_series.max()
    
#     normalized = (deaths_series - min_deaths) / (max_deaths - min_deaths)
#     scaled = min_size + (normalized ** power) * (max_size - min_size)
#     return scaled


# def plot_disasters_on_map(disasters_df, cities_df, country_name, year=None, min_deaths=1, mapbox_style='open-street-map'):
#     """
#     Plot natural disasters on a country map with markers sized by death toll.
#     If `year` is None, plot all disasters across years.
#     """

#     # Filter disasters
#     disaster_filter = (
#         (disasters_df['Country_x'].str.contains(country_name, case=False, na=False)) &
#         (disasters_df['Total Deaths'].notna()) &
#         (disasters_df['Total Deaths'] >= min_deaths)
#     )
#     if year is not None:
#         disaster_filter &= (disasters_df['Start Year'] == year)

#     country_disasters = disasters_df[disaster_filter].copy()

#     if country_disasters.empty:
#         print(f"No disasters found for {country_name} {'in ' + str(year) if year else ''}")
#         return None

#     # Filter cities
#     country_cities = cities_df[cities_df['country_name'].str.contains(country_name, case=False, na=False)].copy()
#     if country_cities.empty:
#         print(f"No cities found for {country_name}")
#         return None

#     # Lookup dictionaries
#     city_lookup = {}
#     state_lookup = {}
#     for _, row in country_cities.iterrows():
#         if pd.notna(row['name']) and pd.notna(row['latitude']) and pd.notna(row['longitude']):
#             city_lookup[row['name'].lower()] = (row['latitude'], row['longitude'], row['name'])
#         if pd.notna(row['state_name']):
#             state_lookup[row['state_name'].lower()] = (row['latitude'], row['longitude'], row['state_name'])

#     # Location parser
#     def find_city_coordinates(location_str, threshold=85):
#         if pd.isna(location_str):
#             return None, None, None
#         location_clean = re.sub(r'\([^)]*\)', '', location_str)  # remove parenthesis
#         location_clean = re.sub(r'\b(cities|province|district|city|state|municipality|region|near)\b', '', location_clean, flags=re.IGNORECASE)
#         parts = re.split(r'[,\|]', location_clean)
#         parts = [p.strip().lower() for p in parts if len(p.strip()) >= 3]

#         for part in parts:
#             if part in city_lookup:
#                 lat, lon, name = city_lookup[part]
#                 return lat, lon, name
#             if part in state_lookup:
#                 lat, lon, name = state_lookup[part]
#                 return lat, lon, name

#         # fallback fuzzy match
#         best_score, best_coords, best_name = 0, (None, None), None
#         for part in parts:
#             for name, (lat, lon, n) in {**city_lookup, **state_lookup}.items():
#                 score = fuzz.ratio(part, name)
#                 if score > best_score and score >= threshold:
#                     best_score = score
#                     best_coords = (lat, lon)
#                     best_name = n
#         return (*best_coords, best_name)

#     # Resolve coordinates
#     disaster_coords = []
#     for _, row in country_disasters.iterrows():
#         if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
#             lat, lon, match = row['Latitude'], row['Longitude'], "Direct"
#         else:
#             lat, lon, match = find_city_coordinates(row['Location'])

#         if lat is not None and lon is not None:
#             disaster_coords.append({
#                 'disaster_id': row['DisNo.'],
#                 'disaster_type': row['Disaster Type'],
#                 'location': row['Location'],
#                 'matched_city': match,
#                 'latitude': lat,
#                 'longitude': lon,
#                 'deaths': row['Total Deaths'],
#                 'year': row['Start Year'],
#                 'total_damage': row['Total Damage (\'000 US$)'] * 1000 if pd.notna(row['Total Damage (\'000 US$)']) else 0,
#             })

#     if not disaster_coords:
#         print("No valid coordinates found.")
#         return None

#     df_plot = pd.DataFrame(disaster_coords)
#     df_plot['marker_size'] = 10 * scale_marker_sizes(df_plot['deaths'])

#     fig = px.scatter_mapbox(
#         df_plot,
#         lat='latitude',
#         lon='longitude',
#         color='disaster_type',
#         size='marker_size',
#         size_max=60,
#         hover_data={
#             'location': True,
#             'deaths': True,
#             'total_damage': True,
#             'year': True,
#         },
#         zoom=4,
#         mapbox_style=mapbox_style,
#         animation_frame='year' if year is None else None,
#         title=f"Disasters in {country_name} {'in ' + str(year) if year else '(All Years)'}",
#         height=700
#     )

#     return fig

# def plot_disasters_on_map_simple(disasters_df, country_name, year, min_deaths=1, mapbox_style='open-street-map'):
#     """
#     Plot natural disasters on a country map with markers sized by death toll using Mapbox.
#     This version works with disaster data that already has Latitude and Longitude columns.
    
#     Parameters:
#     -----------
#     disasters_df : pandas.DataFrame
#         Natural disasters dataset with Latitude and Longitude columns
#     country_name : str
#         Name of the country to visualize
#     year : int
#         Year to filter disasters
#     min_deaths : int, default=1
#         Minimum number of deaths to include in visualization
#     mapbox_style : str, default='open-street-map'
#         Mapbox style ('open-street-map', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', etc.)
    
#     Returns:
#     --------
#     plotly.graph_objects.Figure
#         Interactive map visualization
#     """
    
#     # Filter disasters for the specified country and year
#     country_disasters = disasters_df[
#         (disasters_df['Country_x'].str.contains(country_name, case=False, na=False)) &
#         (disasters_df['Start Year'] == year) &
#         (disasters_df['Total Deaths'].notna()) &
#         (disasters_df['Total Deaths'] >= min_deaths) &
#         (disasters_df['Latitude'].notna()) &
#         (disasters_df['Longitude'].notna())
#     ].copy()
    
#     if country_disasters.empty:
#         print(f"No disasters found for {country_name} in {year} with at least {min_deaths} deaths and valid coordinates")
#         return None
    
#     print(f"Processing {len(country_disasters)} disasters for {country_name} in {year}...")
    
#     # Create DataFrame for plotting with coordinates
#     plot_df = country_disasters[['DisNo.', 'Disaster Type', 'Location', 'Latitude', 'Longitude', 
#                                 'Total Deaths', 'Total Damage (\'000 US$)']].copy()
    
#     # Rename columns for consistency
#     plot_df = plot_df.rename(columns={
#         'Latitude': 'latitude',
#         'Longitude': 'longitude',
#         'Total Deaths': 'deaths',
#         'Total Damage (\'000 US$)': 'total_damage'
#     })
    
#     # Convert damage to USD (multiply by 1000)
#     plot_df['total_damage'] = plot_df['total_damage'] * 1000
    
#     # Calculate marker sizes (proportional to deaths)
#     max_deaths = plot_df['deaths'].max()
#     min_deaths_plot = plot_df['deaths'].min()

#     # Normalize deaths to marker size
#     if max_deaths > min_deaths_plot:
#         plot_df['marker_size'] = 10 * scale_marker_sizes(plot_df['deaths'])
#     else:
#         plot_df['marker_size'] = 60
    
#     # Create color mapping for disaster types
#     disaster_types = plot_df['Disaster Type'].unique()
#     colors = px.colors.qualitative.Set1[:len(disaster_types)]
#     color_discrete_map = dict(zip(disaster_types, colors))
    
#     # Calculate map center
#     center_lat = plot_df['latitude'].mean()
#     center_lon = plot_df['longitude'].mean()
    
#     # Calculate zoom level based on coordinate spread
#     lat_range = plot_df['latitude'].max() - plot_df['latitude'].min()
#     lon_range = plot_df['longitude'].max() - plot_df['longitude'].min()
#     max_range = max(lat_range, lon_range)
    
#     if max_range > 20:
#         zoom = 3
#     elif max_range > 10:
#         zoom = 4
#     elif max_range > 5:
#         zoom = 5
#     elif max_range > 2:
#         zoom = 6
#     else:
#         zoom = 7
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Add traces for each disaster type
#     for disaster_type in disaster_types:
#         type_data = plot_df[plot_df['Disaster Type'] == disaster_type]
        
#         # Create hover text
#         hover_text = []
#         for _, row in type_data.iterrows():
#             damage_text = f"${row['total_damage']:,.0f}" if row['total_damage'] > 0 else "Not available"
            
#             # Limit location display to first 4 parts if it's a comma-separated list
#             location_parts = str(row['Location']).split(',')
#             if len(location_parts) > 4:
#                 limited_location = ', '.join(location_parts[:4]) + '...'
#             else:
#                 limited_location = row['Location']
            
#             hover_text.append(
#                 f"<b>{limited_location}</b><br>"
#                 f"Type: {row['Disaster Type']}<br>"
#                 f"Deaths: {row['deaths']:,}<br>"
#                 f"Damage: {damage_text}"
#             )
        
#         fig.add_trace(go.Scattermapbox(
#             lat=type_data['latitude'],
#             lon=type_data['longitude'],
#             mode='markers',
#             marker=dict(
#                 size=type_data['marker_size'],
#                 color=color_discrete_map[disaster_type],
#                 sizemode='area',
#                 opacity=0.8
#             ),
#             text=hover_text,
#             hovertemplate='%{text}<extra></extra>',
#             name=disaster_type
#         ))
    
#     # Update layout with mapbox
#     fig.update_layout(
#         mapbox=dict(
#             style=mapbox_style,
#             center=dict(lat=center_lat, lon=center_lon),
#             zoom=zoom
#         ),
#         title=f'<br>'
#               f'<sub>Total Events: {len(plot_df)} | Total Deaths: {plot_df["deaths"].sum():,}</sub>',
#         showlegend=True,
#         legend=dict(
#             orientation="v",
#             yanchor="top",
#             y=0.99,
#             xanchor="left",
#             x=0.01,
#             bgcolor="rgba(255,255,255,0.8)"
#         ),
#         height=700,
#         margin=dict(r=0, t=60, l=0, b=0)
#     )
    
#     return fig

# # Example usage:
# # fig = plot_disasters_on_map(disasters_df, cities_df, "United States", 2005, mapbox_style='open-street-map')
# # fig.show()

# # Alternative map styles you can try:
# # 'open-street-map' (default, free)
# # 'carto-positron' (clean, light)
# # 'carto-darkmatter' (dark theme)
# # 'stamen-terrain' (topographic)
# # 'stamen-toner' (high contrast)

# def get_disaster_summary(disasters_df, cities_df, country_name, year):
#     """
#     Get summary statistics for disasters in a country for a given year.
#     """
#     country_disasters = disasters_df[
#         (disasters_df['Country_x'].str.contains(country_name, case=False, na=False)) &
#         (disasters_df['Start Year'] == year)
#     ].copy()
    
#     if country_disasters.empty:
#         return f"No disasters found for {country_name} in {year}"
    
#     summary = {
#         'Total Events': len(country_disasters),
#         'Total Deaths': country_disasters['Total Deaths'].sum(),
#         'Total Affected': country_disasters['Total Affected'].sum(),
#         'Disaster Types': country_disasters['Disaster Type'].value_counts().to_dict(),
#         'Most Deadly Event': country_disasters.loc[country_disasters['Total Deaths'].idxmax(), 'Event Name'] if country_disasters['Total Deaths'].max() > 0 else 'None',
#         'Total Economic Damage (USD)': country_disasters['Total Damage (\'000 US$)'].sum() * 1000 if country_disasters['Total Damage (\'000 US$)'].notna().any() else 'Not available'
#     }
    
#     return summary




# # Example usage:
# # city = pd.read_csv("cities.csv")
# # fig = plot_disasters_on_map_with_slider(data, city, "India", min_deaths=1, mapbox_style='open-street-map', power=2.5)

# # fig = create_interactive_disasters_map(data, city)
# # fig.show()
# # fig = plot_disasters_on_map(data, city, "India", 2010, min_deaths=1, mapbox_style='carto-darkmatter')
# # # fig = plot_disasters_on_map(data, city, "India", 2004, "carto-darkmatter")
# # # Alternative map styles you can try:
# # # 'open-street-map' (default, free)
# # # 'carto-positron' (clean, light)
# # # 'carto-darkmatter' (dark theme)
# # # 'stamen-terrain' (topographic)
# # # 'stamen-toner' (high contrast)
# # fig.show()
# # if __name__ == "__main__":
# #     data_path = os.path.join(root_path, "data", "Risk_Analysis", "final_risk_merged.csv")
# #     city_path = os.path.join(root_path, "data", "Risk_Analysis", "cities.csv")
# #     data = pd.read_csv(data_path)
# #     city = pd.read_csv(city_path)
# #     fig = plot_disasters_on_map(data, city, "India", 2010, min_deaths=1, mapbox_style='carto-darkmatter')
# #     fig.show()