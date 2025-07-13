import re
import pandas as pd
import plotly.graph_objects as go

def get_lollipop3(df: pd.DataFrame) -> None:
    """
    Generates a lollipop chart of the top 30 most vulnerable countries per decade.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'Country', 'Decade', 'VulnerabilityScore' columns.
    """
    # === Preprocess ===
    df["Decade"] = df["Decade"].astype(int)

    # === Filter Top 30 Countries per Decade ===
    top_30 = (
        df.sort_values(["Decade", "VulnerabilityScore"], ascending=[True, False])
          .groupby("Decade", group_keys=False)
          .head(30)
    )

    # === Prepare Figure ===
    fig = go.Figure()
    decades = sorted(top_30["Decade"].unique())
    grouped = {
        decade: group.sort_values("VulnerabilityScore")
        for decade, group in top_30.groupby("Decade")
    }

    for i, decade in enumerate(decades):
        group = grouped[decade]
        fig.add_trace(go.Scatter(
            x=group["VulnerabilityScore"],
            y=group["Country"],
            mode='lines+markers',
            marker=dict(size=8, color='red'),
            line=dict(color='gray', width=2),
            name=str(decade),
            visible=(i == 0)  # Show only the first decade by default
        ))

    # === Dropdown Menu ===
    buttons = [
        dict(
            label=str(decade),
            method="update",
            args=[
                {"visible": [j == i for j in range(len(decades))]},
                {"title": f"Top 30 Vulnerable Countries in {decade}"}
            ]
        )
        for i, decade in enumerate(decades)
    ]

    # === Layout Settings ===
    fig.update_layout(
        paper_bgcolor='rgba(255, 255, 255, 0.5)',  # outer background
plot_bgcolor='rgba(255, 255, 255, 0.5)',   # plotting area background
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            x=1.05,
            y=1.15
        )],
        title=f"Top 30 Vulnerable Countries in {decades[0]}",
        xaxis_title="Vulnerability Score",
        yaxis_title="Country",
        height=1000
    )

    return fig


def main():
    file_path = "/Users/vishalsingh/python/sample/data/processed/vulnerability_by_country.csv"
    df = pd.read_csv(file_path)
    get_lollipop3(df)


if __name__ == "__main__":
    main()
