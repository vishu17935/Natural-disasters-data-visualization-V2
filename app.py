# app.py
from dash import Dash
from ui.layout import layout
import callbacks  # Import callbacks to register them

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Natural Disaster Dashboard"
app.layout = layout

if __name__ == "__main__":
    app.run(debug=True,port=8065)
