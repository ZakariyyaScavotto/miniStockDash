"""Created by Zak Scavotto for Stevens CS Club"""
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd

def sidebar():
    """Creates the sidebar for the app, returns the user input for the ticker and date range."""
    st.sidebar.header('User Input')
    ticker = st.sidebar.text_input('Single-Stock Ticker', 'AAPL')
    # add a date range
    start_date = st.sidebar.text_input('Start Date', '2020-01-01')
    end_date = st.sidebar.text_input('End Date', '2021-01-01')
    # Add a button to update the data
    update_button = st.sidebar.button('Update Data')
    if update_button:
        st.experimental_rerun()
    return ticker, start_date, end_date

def graph(data):
    """Creates the graph for the app."""
    # create dropdown for user to select what data (Close, Volume, Open, High) to plot and plot it
    st.subheader('Plot')
    plot = st.selectbox('Select Data to Graph', ('Adj Close', 'Open', 'Volume', 'Low', 'High','Returns', '7 Day Moving Average', '1 Month Moving Average'))
    st.line_chart(data[plot])

def returns(data):
    """Calculates the Returns."""
    data['Returns'] = data['Adj Close'].pct_change()
    return data

def sevenDayMovingAverage(data):
    """Calculates the 7 day moving average."""
    data['7 Day Moving Average'] = data['Adj Close'].rolling(window=7).mean()
    return data

def monthMovingAverage(data):
    """Calculates the 1 month moving average."""
    data['1 Month Moving Average'] = data['Adj Close'].rolling(window=30).mean()
    return data

def downloadData(ticker, start_date, end_date):
    """Downloads the data from Yahoo Finance."""
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        return data
    except ValueError:
        st.error('Error: Ticker not found')
        return

def compareCompanies(start_date, end_date):
    """Compares multiple companies."""
    # Add input for multiple companies
    companies = st.text_input('Enter Tickers of Companies to Compare (separated by a comma)', 'AAPL, MSFT, GOOGL')
    companies = companies.strip().split(',')
    # Remove any empty strings
    companies = [company.strip() for company in companies if company]
    # Download data for each company
    data = {}
    for company in companies:
        data[company] = downloadData(company, start_date, end_date)
    # Add a dropdown to select what data to compare
    st.subheader('Compare Data')
    compare_data = st.selectbox('Select Data to Compare', ('Adj Close', 'Open', 'Volume', 'Low', 'High'))
    # Plot the data for all companies on the same graph by combining the data into a single dataframe
    combinedDf = pd.concat([data[company][compare_data] for company in companies], axis=1, keys=companies)
    st.line_chart(combinedDf)

def initializeGraphs(data, start_date, end_date):
    # Add checkbox to select single company or compare multiple companies
    st.subheader('Compare Companies')
    st.caption('Select to compare multiple companies\' stock prices')
    compare = st.checkbox('Compare Company Stock Prices')
    if compare:
        compareCompanies(start_date, end_date)
    else:
        graph(data)

def main():
    # Set page config to wide
    st.set_page_config(layout="wide")
    # Title
    st.title('Stock Dashboard')
    companyTicker, start_date, end_date = sidebar()
    # Auto-fetch data, if there is no data, display an error message
    # not sure if this actually works but it should refresh the data every 5 minutes
    count = st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")
    if count == 0 or count %5 == 0:
        data = downloadData(companyTicker, start_date, end_date)
    # make dropdown option to hide the data
    hide_data = st.checkbox('Hide Data')
    hide_balance_sheet = st.checkbox('Hide Balance Sheet')
    # add the metrics to the single-stock data if selected
    data = returns(data)
    data = sevenDayMovingAverage(data)
    data = monthMovingAverage(data)
    # display the data if the user does not want to hide it
    if not hide_data:
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            # create a multi-select to choose what data to display, default to all
            st.subheader('Data')
            data_display = st.multiselect('Select Data to Display', ('Open', 'High', 'Low', 'Adj Close', 'Volume','Returns', '7 Day Moving Average', '1 Month Moving Average'), default=('Adj Close', 'Returns'))
            st.write(data[data_display])
        with col2:
            initializeGraphs(data, start_date, end_date)
    else:
        initializeGraphs(data, start_date, end_date)
    # Display company balance sheet
    if not hide_balance_sheet:
        st.subheader(companyTicker+' Balance Sheet')
        st.write(yf.Ticker(companyTicker).balance_sheet)


main()