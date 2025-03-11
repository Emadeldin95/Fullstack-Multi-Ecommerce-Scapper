import dash
from dash import Input, Output, State, ctx
import dash_bootstrap_components as dbc
import threading
import pandas as pd
import asyncio
from scraper import Scraper
from layout import create_layout  # Importing layout

# Initialize Dash App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Set app layout from external layout.py
app.layout = create_layout()

scraper = None
scraper_thread = None
data_store = []  # Holds scraped data
scraping_status = "Stopped"  # Status tracker

def run_scraper(url, keywords):
    """Runs the scraper in a separate thread."""
    global scraper, scraping_status
    scraping_status = "Active"
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    scraper = Scraper(url, keywords)
    loop.run_until_complete(scraper.start_scraping(update_callback))
    scraping_status = "Stopped"

def update_callback(data):
    """Updates the global data store while scraping is in progress."""
    global data_store
    data_store = data

@app.callback(
    [Output("data-table", "data"), Output("status-indicator", "children"), Output("counter-indicator", "children")],
    Input("interval-component", "n_intervals"),
    Input("start-btn", "n_clicks"),
    Input("stop-btn", "n_clicks"),
    State("url-input", "value"),
    State("keyword-input", "value"),
    prevent_initial_call=True
)
def handle_scraper_and_update_table(n_intervals, start, stop, url, keywords):
    """Manages the scraping process, updates the table, live status indicator, and product counter."""
    global scraper, scraper_thread, scraping_status

    # Check which button was clicked
    triggered_id = ctx.triggered_id

    if triggered_id == "start-btn" and url:
        # Start scraping in a new thread
        scraper_thread = threading.Thread(target=run_scraper, args=(url, keywords))
        scraper_thread.start()
    
    elif triggered_id == "stop-btn" and scraper:
        # Stop scraping
        scraper.stop()
        scraping_status = "Stopped"

    # Update status indicator
    status_text = "Scraping Active 🟢" if scraping_status == "Active" else "Scraper Stopped 🔴"

    # Update scraped product count
    product_count = len(data_store)
    counter_text = f"Total Products Scraped: {product_count}"

    return data_store, status_text, counter_text

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_data(n_clicks):
    """Allows downloading of scraped data."""
    if data_store:
        df = pd.DataFrame(data_store)
        return dash.dcc.send_data_frame(df.to_csv, "scraped_data.csv")

if __name__ == "__main__":
    app.run_server(debug=True)
