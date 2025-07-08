import pandas as pd
import plotly.graph_objects as go

def get_sankey_viz(data: pd.DataFrame) -> go.Figure:
    """
    Creates a Sankey diagram using the provided preprocessed data.

    Parameters:
    - data (pd.DataFrame): A DataFrame with columns 'source', 'target', and 'value'.

    Returns:
    - A Plotly Sankey figure.
    """
    try:
        # Validate required columns
        required_columns = ['source', 'target', 'value']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("DataFrame must have 'source', 'target', and 'value' columns.")
        
        # Validate value column is numerical
        if not pd.api.types.is_numeric_dtype(data['value']):
            raise ValueError("The 'value' column must be numerical.")

        # Create a list of unique nodes
        nodes = list(set(data['source']).union(set(data['target'])))
        node_indices = {node: idx for idx, node in enumerate(nodes)}

        # Prepare links for Sankey diagram
        link_source = [node_indices[src] for src in data['source']]
        link_target = [node_indices[tgt] for tgt in data['target']]
        link_value = data['value'].tolist()

        # Create the Sankey diagram
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color="lightblue"
            ),
            link=dict(
                source=link_source,
                target=link_target,
                value=link_value,
                color="rgba(0, 184, 255, 0.5)"
            )
        )])

        # Update layout
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            title_text="India's GDP Flow (Sankey Diagram)",
            font_size=12,
            margin=dict(t=50, l=25, r=25, b=25)
        )

        return fig

    except Exception as e:
        # Handle errors gracefully
        print(f"Error creating Sankey diagram: {str(e)}")
        return go.Figure()  # Return an empty figure if there's an error

# Example usage for testing
if __name__ == "__main__":
    # Sample data
    sample_data = pd.DataFrame({
        'source': ['Agriculture', 'Agriculture', 'Crops', 'Crops', 'Industry', 'Industry', 
                   'Manufacturing', 'Manufacturing', 'Services', 'Services', 'Services'],
        'target': ['Crops', 'Livestock', 'Food Crops', 'Cash Crops', 'Manufacturing', 'Construction', 
                   'Electronics', 'Textiles', 'IT Services', 'Tourism', 'Finance'],
        'value': [80, 20, 50, 30, 180, 60, 100, 80, 150, 70, 90]
    })
    fig = get_sankey_viz(sample_data)
    fig.show()