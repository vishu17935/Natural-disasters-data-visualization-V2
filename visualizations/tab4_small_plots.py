import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def plot_disaster_types_by_year(df, country_name, year):
    """
    Generates a bar chart of disaster types for a specific country and year.

    Parameters:
    -----------
    df : pandas.DataFrame
        The disaster dataset
    country_name : str
        Name of the country to filter
    year : int
        Year to filter disasters

    Returns:
    --------
    plotly.graph_objs._figure.Figure
        The bar chart figure object
    """

    # Filter data for the specific country and year
    country_year_data = df[(df['Country_x'] == country_name)].copy()
    if(year):
        country_year_data = df[(df['Start Year'] == year)]
    
    if country_year_data.empty:
        print(f"No disaster data found for {country_name} in {year}.")
        return px.bar(title=f"No disaster data found for {country_name} in {year}")

    # Count the occurrences of each disaster type
    disaster_counts = country_year_data['Disaster Type'].value_counts().reset_index()
    disaster_counts.columns = ['Disaster Type', 'Count']

    # Sort for better visualization (optional, but good practice for horizontal bars)
    disaster_counts = disaster_counts.sort_values('Count', ascending=True)


    # Create the horizontal bar chart
    fig = px.bar(
        disaster_counts,
        x='Count', # Swap x and y for horizontal bars
        y='Disaster Type',
        orientation='h', # Specify horizontal orientation
        title=f'Disaster Type Distribution in {country_name} ({year})',
        labels={'Disaster Type': 'Disaster Type', 'Count': 'Number of Occurrences'},
        template='plotly_white'
    )

    # No need to angle x-axis labels for horizontal bars, update layout for y-axis
    fig.update_layout(yaxis_title='Disaster Type')

    fig.update_layout(
        title=None,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(showticklabels=True, tickfont=dict(size=10)),
        yaxis=dict(showticklabels=True, tickfont=dict(size=10)),
        font=dict(size=10),
        height=300
    )


    return fig



def plot_disaster_types_pie_chart(df, country_name, year):
    """
    Generates a pie chart of disaster types for a specific country and year.

    Parameters:
    -----------
    df : pandas.DataFrame
        The disaster dataset
    country_name : str
        Name of the country to filter
    year : int
        Year to filter disasters

    Returns:
    --------
    plotly.graph_objs._figure.Figure
        The pie chart figure object
    """
    if(year):
        # Filter data for the specific country and year
        country_year_data = df[(df['Country_x'] == country_name) & (df['Start Year'] == year)].copy()
    else:
        country_year_data = df[(df['Country_x'] == country_name)].copy()

    if country_year_data.empty:
        print(f"No disaster data found for {country_name} in {year}.")
        return go.Figure().add_annotation(
            text=f"No disaster data found for {country_name} in {year}",
            xref="paper", yref="paper", showarrow=False, font=dict(size=16)
        )


    # Count the occurrences of each disaster type
    disaster_counts = country_year_data['Disaster Type'].value_counts().reset_index()
    disaster_counts.columns = ['Disaster Type', 'Count']

    # Create the pie chart
    fig = px.pie(
        disaster_counts,
        values='Count',
        names='Disaster Type',
        # title=f'Disaster Type Distribution in {country_name} ({year})',
        template='plotly_white'
    )

    # Update layout for better readability and remove legend
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', showlegend=False)
    fig.update_layout(height=300, width=350, margin=dict(l=0, r=0, t=0, b=0))

    return fig

# Example usage:
# plot_disaster_types_pie_chart(data, 'India', 2010).show()