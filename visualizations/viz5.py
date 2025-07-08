import pandas as pd
import plotly.graph_objects as go

def get_stacked_area_viz(data: pd.DataFrame) -> go.Figure:
    """
    Creates a static stacked area chart for GDP contributions over time.

    Parameters:
    - data (pd.DataFrame): A DataFrame with columns 'year', 'Agriculture', 'Industry', 'Services' (numeric).

    Returns:
    - A Plotly figure.
    """
    try:
        # Validate required columns
        required_columns = ['year', 'Agriculture', 'Industry', 'Services']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("DataFrame must have 'year', 'Agriculture', 'Industry', and 'Services' columns.")

        # Validate numerical columns
        for col in ['Agriculture', 'Industry', 'Services']:
            if not pd.api.types.is_numeric_dtype(data[col]):
                raise ValueError(f"'{col}' column must be numerical.")

        # Create the stacked area chart
        fig = go.Figure()

        # Add traces for each sector
        for sector in ['Agriculture', 'Industry', 'Services']:
            fig.add_trace(go.Scatter(
                x=data['year'],
                y=data[sector],
                name=sector,
                mode='lines',
                stackgroup='one',
                fill='tonexty',
                line=dict(width=0.5)
            ))

        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title="GDP Contributions Over Time (Stacked Area)",
            xaxis_title="Year",
            yaxis_title="GDP (Billions USD)",
            showlegend=True,
            margin=dict(t=50, l=25, r=25, b=25)
        )

        return fig

    except Exception as e:
        print(f"Error creating stacked area chart: {str(e)}")
        return go.Figure()  # Return an empty figure if there's an error

# Example usage for testing
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'year': ['2018', '2019', '2020', '2021', '2022', '2023', '2024'],
        'Agriculture': [80, 85, 90, 95, 100, 105, 110],
        'Industry': [200, 210, 220, 230, 240, 250, 260],
        'Services': [250, 270, 280, 290, 310, 320, 330]
    })
    fig = get_stacked_area_viz(sample_data)
    fig.show()