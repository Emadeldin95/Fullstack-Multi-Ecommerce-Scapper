from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container([
        html.H1("E-Commerce Scraper Dashboard", className="text-center my-4"),

        # Live status and count indicators
        dbc.Row([
            dbc.Col(html.Div(id="status-indicator", children="Scraper Stopped 🔴", 
                             style={"fontSize": "20px", "marginBottom": "10px"}), width=6),
            dbc.Col(html.Div(id="counter-indicator", children="Total Products Scraped: 0", 
                             style={"fontSize": "20px", "marginBottom": "10px"}), width=6),
        ]),

        # Input fields for URL and keyword
        dbc.Row([
            dbc.Col(dbc.Input(id="url-input", type="text", placeholder="Enter Shop URL", className="mb-2"), width=6),
            dbc.Col(dbc.Input(id="keyword-input", type="text", placeholder="Optional: Enter Keywords", className="mb-2"), width=6),
        ]),

        # Control buttons
        dbc.Row([
            dbc.Col(dbc.Button("Start Scraping", id="start-btn", color="primary", className="me-2"), width="auto"),
            dbc.Col(dbc.Button("Stop Scraping", id="stop-btn", color="danger", className="me-2"), width="auto"),
            dbc.Col(dbc.Button("Download Data", id="download-btn", color="success", className="me-2"), width="auto"),
        ], className="mb-3"),

        html.Hr(),

        # Auto-refresh every second for status updates
        dcc.Interval(id="interval-component", interval=1000, n_intervals=0),

        # Data Table with Pagination
        dash_table.DataTable(
            id="data-table",
            columns=[{"name": col, "id": col} for col in ["Name", "Price", "Link"]],
            data=[],
            page_size=10,  # Display 10 items per page
            page_action="native",
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
        ),

        dcc.Download(id="download-dataframe-csv")
    ])
