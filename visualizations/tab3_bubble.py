import pandas as pd
import plotly.graph_objects as go
from typing import List
from plotly.colors import qualitative
import numpy as np

# Updated color scheme for better contrast
CONTINENT_COLORS = {
    'Asia': qualitative.Set2[0],
    'Europe': qualitative.Set2[1],
    'North America': qualitative.Set2[2],
    'South America': qualitative.Set2[3],
    'Africa': qualitative.Set2[4],
    'Oceania': qualitative.Set2[5],
    'Antarctica': qualitative.Set2[6],
}

# Horizontal offsets per continent
CONTINENT_OFFSETS = {
    'Asia': -1.5,
    'Europe': -2,
    'Africa': 0.0,
    'North America': 2,
    'South America': 0.8,
    'Oceania': 0.15
}

def get_bubble_viz_tab3(data: pd.DataFrame) -> go.Figure:
    try:
        required_cols = {'country', 'continent', 'decade', 'avg_deaths', 'disaster_type'}
        missing = required_cols - set(data.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        print("Sample input:\n", data.head().to_dict(orient='list'))

        disaster_types = sorted(data['disaster_type'].unique())
        dropdown_options = ['all disasters'] + disaster_types
        fig = go.Figure()

        all_y_vals = []

        for d_type in dropdown_options:
            df = data.copy() if d_type == 'all disasters' else data[data['disaster_type'] == d_type]
            if df.empty:
                continue
            # Filter top records only for 'all disasters' to reduce clutter
            
            df = df.nlargest(150, 'avg_deaths')
  # Or use df.nlargest(50, 'avg_deaths')


            # Precompute
            df = df.sort_values('avg_deaths', ascending=False).reset_index(drop=True)
            y_vals = np.linspace(1, 0, len(df)) + np.random.normal(0, 0.02, len(df))
            all_y_vals.extend(y_vals)

            # Horizontal jitter + offset
            x_vals = (
                df['decade']
                + df['continent'].map(CONTINENT_OFFSETS).fillna(0)
                + np.random.normal(0, 0.5, len(df))  # Added jitter here
            )

            # Log-scale bubble sizes
            log_sizes = np.log1p(df['avg_deaths'])
            sizeref = 2. * log_sizes.max() / (40 ** 2)

            color_vals = df['continent'].map(CONTINENT_COLORS).fillna('gray')

            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='markers',
                marker=dict(
                    size=log_sizes,
                    sizemode='area',
                    sizeref=sizeref,
                    sizemin=4,
                    opacity=0.6,  # Reduced opacity
                    color=color_vals,
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                text=df['country'],
                hovertemplate='<b>%{text}</b><br>Decade: %{x}<br>Deaths: %{marker.size:.2f}<extra></extra>',
                hoverlabel=dict(
                bgcolor="white",      # Background of hover label
                font_size=12,
                font_color="black",   # Text color
                bordercolor="gray"
                ),
                name=d_type,
                visible=(d_type == 'all disasters')
            ))

        # Dropdown buttons
        buttons = [
            {
                'label': d_type,
                'method': 'update',
                'args': [
                    {'visible': [j == i for j in range(len(dropdown_options))]},
                    {'title': f"Average Deaths ({d_type.title()})"}
                ]
            }
            for i, d_type in enumerate(dropdown_options)
        ]

        # Layout settings
        fig.update_layout(
            updatemenus=[{
                'active': 0,
                'buttons': buttons,
                'x': 0.01,
                'y': 1.25,
                'xanchor': 'left',
                'yanchor': 'top'
            }],
            title={
                'text': "Average Deaths(All Disasters)",
                'y': 0.92,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=False,
            xaxis=dict(title='Decade', showgrid=False, zeroline=False),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                zeroline=False,
                range=[min(all_y_vals) - 0.05, 1.05]  # Dynamic lower bound
            ),
            paper_bgcolor='rgba(255,255,255,0.5)',
plot_bgcolor='rgba(255,255,255,0)',
            margin=dict(t=100, l=20, r=20, b=20)
        )

        return fig

    except Exception as e:
        print(f"Error in bubble chart: {e}")
        return go.Figure()


def print_dataset_requirements() -> None:
    expected = {
        'country': 'str',
        'continent': 'str',
        'decade': 'int',
        'avg_deaths': 'float',
        'disaster_type': 'str'
    }
    print("Expected DataFrame structure:")
    for col, typ in expected.items():
        print(f" - {col}: {typ}")
    print("Each row = one country, one decade, one disaster type.")

# Run for testing
if __name__ == "__main__":
    print_dataset_requirements()
    df = pd.read_csv("/Users/vishalsingh/python/cleaned_notreal.csv")
    fig = get_bubble_viz_tab3(df)
    fig.show()
