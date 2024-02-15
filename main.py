import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf

#TODO: calculate metrics (i.e. Price percentage change, moving averages, P/E ratio, etc.)


def sidebar():
    st.sidebar.header('User Input')
    ticker = st.sidebar.text_input('Ticker', 'AAPL')
    # add a date range
    start_date = st.sidebar.text_input('Start Date', '2020-01-01')
    end_date = st.sidebar.text_input('End Date', '2021-01-01')
    return ticker, start_date, end_date

def graph(data):
    # create dropdown for user to select what data (Close, Volume, Open, High) to plot and plot it
    st.subheader('Plot')
    plot = st.selectbox('Select Data to Graph', ('Close', 'Open', 'Volume', 'Low', 'High'))
    st.line_chart(data[plot])

def main():
    # Title
    st.title('Stock Dashboard')
    ticker, start_date, end_date = sidebar()
    # Auto-fetch data, if there is no data, display an error message
    count = st_autorefresh(interval=5 * 60 * 1000, key="data_refresh")
    if count == 0 or count %5 == 0:
        try:
            data = yf.download(ticker, start=start_date, end=end_date)
        except ValueError:
            st.error('Error: Ticker not found')
            return
    # make dropdown option to hide the data
    hide_data = st.checkbox('Hide Data')
    if not hide_data:
        # create a multi-select to choose what data to display, default to all
        st.subheader('Data')
        data_display = st.multiselect('Select Data to Display', ('Open', 'High', 'Low', 'Close', 'Volume'), default=('Open', 'High', 'Low', 'Close', 'Volume'))
        st.write(data[data_display])
        

    graph(data)

main()