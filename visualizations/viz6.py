import pandas as pd
import plotly.express as px

def get_pie_viz(data: pd.DataFrame) -> px.pie:
    """
    Creates a static pie chart for GDP contributions by sector.

    Parameters:
    - data (pd.DataFrame): A DataFrame with columns 'sector' (string) and 'value' (numeric).

    Returns:
    - A Plotly pie figure.
    """
    try:
        # Validate required columns
        required_columns = ['sector', 'value']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("DataFrame must have 'sector' and 'value' columns.")

        # Validate 'value' column is numerical
        if not pd.api.types.is_numeric_dtype(data['value']):
            raise ValueError("'value' column must be numerical.")

        # Create the pie chart
        fig = px.pie(
            data,
            names='sector',
            values='value',
            title="India's GDP by Sector (Pie Chart)",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, l=25, r=25, b=25),
            title_font_size=20
        )

        return fig

    except Exception as e:
        print(f"Error creating pie chart: {str(e)}")
        return px.pie()  # Return an empty figure if there's an error

# Example usage for testing
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'sector': ['Agriculture', 'Industry', 'Services'],
        'value': [110, 260, 330]
    })
    fig = get_pie_viz(sample_data)
    fig.show()