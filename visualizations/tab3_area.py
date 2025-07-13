import pandas as pd
import plotly.graph_objects as go

def get_area_chart3(df: pd.DataFrame):
    """
    Generates an interactive stacked bar chart showing average disaster GDP loss per decade,
    with dropdown to filter by continent.

    Parameters:
        df (pd.DataFrame): Preprocessed dataframe with columns 'Entity', 'Year', 'Continent',
                           and GDP loss columns starting with 'Total economic damages'.
    """
    # === Extract GDP Damage Columns ===
    damage_cols = [col for col in df.columns if col.startswith("Total economic damages")]

    # === Melt to Long Format ===
    df_long = df.melt(
        id_vars=["Entity", "Year", "Continent"],
        value_vars=damage_cols,
        var_name="Disaster Type",
        value_name="Damage Share"
    )

    # === Clean Values ===
    df_long["Disaster Type"] = df_long["Disaster Type"].str.replace(
        "Total economic damages as a share of GDP - ", "", regex=False
    )
    df_long = df_long[df_long["Damage Share"].notna() & (df_long["Damage Share"] > 0)]
    df_long["Damage Share"] = df_long["Damage Share"].apply(lambda x: x / 100 if x > 1 else x)
    df_long["Decade"] = (df_long["Year"] // 10) * 10

    # === Unique Continents and Disaster Types ===
    continents = ["World"] + sorted(df_long["Continent"].dropna().unique())
    all_disasters = sorted(df_long["Disaster Type"].unique())

    # === Plot Setup ===
    fig = go.Figure()

    for i, continent in enumerate(continents):
        # Filter data
        df_filtered = df_long if continent == "World" else df_long[df_long["Continent"] == continent]

        # Aggregate
        df_yearly = df_filtered.groupby(
            ["Year", "Decade", "Entity", "Disaster Type"], as_index=False
        )["Damage Share"].mean()

        df_final = df_yearly.groupby(["Decade", "Disaster Type"], as_index=False)["Damage Share"].mean()
        df_final["Damage Share"] *= 100  # Convert to %

        # Create full grid of all disasters × decades
        all_decades = sorted(df_long["Decade"].unique())
        full_index = pd.MultiIndex.from_product(
            [all_decades, all_disasters],
            names=["Decade", "Disaster Type"]
        )
        df_final = df_final.set_index(["Decade", "Disaster Type"]).reindex(full_index, fill_value=0).reset_index()

        # Add traces for this continent
        for disaster in all_disasters:
            df_dis = df_final[df_final["Disaster Type"] == disaster]
            fig.add_trace(go.Bar(
                x=df_dis["Decade"],
                y=df_dis["Damage Share"],
                name=disaster,
                visible=(i == 0),
                legendgroup=disaster,
                showlegend=(disaster not in [t.name for t in fig.data])  # Show legend only once
            ))

    # === Visibility Logic ===
    num_disasters = len(all_disasters)
    buttons = []
    for i, continent in enumerate(continents):
        vis = [False] * (num_disasters * len(continents))
        start = i * num_disasters
        vis[start:start + num_disasters] = [True] * num_disasters
        buttons.append(dict(
            label=continent,
            method="update",
            args=[
                {"visible": vis},
                {"title": f"Average Disaster GDP Loss (% of GDP) per Decade — {continent}"}
            ]
        ))

    # === Final Layout ===
    fig.update_layout(
         paper_bgcolor='rgba(255, 255, 255, 0.5)',  # outer background
        plot_bgcolor='rgba(255, 255, 255, 0.5)',
        title="Average Disaster GDP Loss (% of GDP) per Decade — World",
        title_x=0.5,  # Centered title
        xaxis_title="Decade",
        yaxis_title="Avg GDP Loss (%)",
        barmode="stack",
        yaxis_tickformat=".2f",
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=0.0,
                xanchor="left",
                y=1.15,
                yanchor="top"
            )
        ]
    )

    return fig


# === Usage Example ===
if __name__ == "__main__":
    file_path = "/Users/vishalsingh/python/sample/data/processed/area_chart3.csv"
    df = pd.read_csv(file_path)
    get_area_chart3(df)
