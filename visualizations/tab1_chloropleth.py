from random import sample
import pandas as pd
import plotly.express as px
import numpy as np
    

def get_choropleth_viz(
    data: pd.DataFrame,
    value_col: str,
    location_col: str = 'ISO_Code',
    hover_name_col: str = 'Country name',
    animation_frame_col: str = 'Year',
    title: str = "World Choropleth Map (Animated)",
    log_scale: bool = False,
    color_scale: str = 'Turbo'
) -> px.choropleth:
    """
    Creates an animated choropleth map visualization for world data.

    Parameters:
    - data (pd.DataFrame): DataFrame with necessary columns.
    - value_col (str): Column name for coloring the map.
    - location_col (str): Column with ISO country codes.
    - hover_name_col (str): Column for country names in hover tooltip.
    - animation_frame_col (str): Column for animation frames (e.g., 'Year').
    - title (str): Plot title.
    - log_scale (bool): Whether to use log10 scale for color (default: False).
    - color_scale (str): Color scale to use (default: 'Turbo').

    Returns:
    - A Plotly choropleth figure.
    """
    try:
        # Validate columns
        required_cols = [location_col, value_col, hover_name_col, animation_frame_col]
        if not all(col in data.columns for col in required_cols):
            raise ValueError(f"DataFrame must include columns: {', '.join(required_cols)}")

        df_plot = data.copy()

        # Apply log scale if requested
        if log_scale:
            log_col = f"log_{value_col}"
            df_plot[log_col] = np.log10(df_plot[value_col] + 1e-6)
            color_column = log_col
        else:
            color_column = value_col

        # Create the figure
        fig = px.choropleth(
            df_plot,
            locations=location_col,
            color=color_column,
            hover_name=hover_name_col,
            animation_frame=animation_frame_col,
            color_continuous_scale=color_scale,
            title=title,
            range_color=(df_plot[color_column].min(), df_plot[color_column].max())
        )

        # Layout customization
        fig.update_layout(
            geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
            coloraxis_colorbar=dict(title=value_col),
            width=1200,
            height=700,
            title_font_size=22,
            font=dict(family='Tektur, Segoe UI, sans-serif', size=15, color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        fig.update_traces(marker_line_width=0.5, marker_line_color='white')

        return fig

    except Exception as e:
        print(f"Error creating choropleth map: {e}")
        return px.choropleth()  # Empty figure fallback


# Example usage for testing
if __name__ == "__main__":
    import plotly.io as pio

    # Load the dataset
    file_path = "/Users/vishalsingh/python/sample/data/processed/merged_output_with_iso.csv"
    df = pd.read_csv(file_path)

    # Create the figure
    fig = get_choropleth_viz(
        df,
        value_col='Total economic damages from disasters as a share of GDP',
        log_scale=True,
        color_scale='Plasma'
    )

    # Display the figure in browser
    fig.show()

    # Optional: Save to HTML for debugging or sharing
    output_path = "/Users/vishalsingh/python/sample/visualizations/choropleth_output.html"
    pio.write_html(fig, file=output_path, auto_open=False)
    print(f"Choropleth map saved to {output_path}")



    