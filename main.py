import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import statsmodels
import numpy as np


st.set_page_config(
    page_title="Adidas Sales Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded")

#alt.themes.enable("light")

st.markdown("""
<style>

p {
  color: white;
}

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #1D3354;
    text-align: center;
    padding: 15px 0;
    border-radius: 5px;
    color: white;
}

[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}


[data-testid="st-emotion-cache-6qob1r"] {
    background-color: #1D3354;
    color: black;
}

[data-testid="st-emotion-cache-1629p8f"]{
    justify-content: center;
    align-items: center;
}

</style>
""", unsafe_allow_html=True)


data = pd.read_excel("adidas_sales.xlsx",
                     skiprows=4, index_col = False)

data = data.drop("Unnamed: 0", axis = 1)

data["Invoice Data"] = pd.to_datetime(data["Invoice Date"])
data["Year"] = data["Invoice Date"].dt.year
data["Month"] = data["Invoice Date"].dt.month
data["Day"] = data["Invoice Date"].dt.day


#st.title("Adidas Sales Dashboard")
st.markdown("<h1 style='text-align: center;'>Adidas Sales Dashboard</h1>", unsafe_allow_html=True)


with st.sidebar:
    array_city = data["City"].unique()
    array_city = np.append(array_city, "All Cities")
    region_chosen = st.selectbox("Choose Region", (array_city), placeholder = "All Regions")

    array_retailer = data["Retailer"].unique()
    array_retailer = np.append(array_retailer, "All Retailers")
    retailer_chosen = st.selectbox("Choose Retailer", (array_retailer), placeholder = "All Retailers")

    array_product = data["Product"].unique()
    array_product = np.append(array_product, "All Products")
    product_chosen = st.selectbox("Choose Product", (array_product), placeholder = "All Products")




def filter_chart_dataset(retailer_filter, product_filter):
    """Generate Filtered dataset based on the dropdown menus in the dashboard

    Args:
        region_filter ([str]): [Filter for Cities]
        retailer_filter ([str]): [Filter for Retailers]
        product_filter ([str]): [Filter for different products]

    Returns:
        [dataframe]: [returns the filtereddataframe]
    """
    if (retailer_filter == "All Retailers") & (product_filter == "All Products"):

        retailer_sales_sum_by_date = data.groupby(["Invoice Date", "Retailer"])["Total Sales"].sum().reset_index()
        profit_margin_over_time = data.groupby('Invoice Date')['Operating Profit'].mean().reset_index()
        top_selling_products = data.groupby('Product')['Total Sales'].sum().sort_values(ascending=False).reset_index()
        monthly_sales_breakdown = data.groupby(data['Month'])['Total Sales'].sum().reset_index()


    else:

        data_filtered = data[(data["Retailer"] == retailer_filter) & (data["Product"] == product_filter)]

        retailer_sales_sum_by_date = data_filtered.groupby(["Invoice Date", "Retailer"])["Total Sales"].sum().reset_index()
        profit_margin_over_time = data_filtered.groupby('Invoice Date')['Operating Profit'].mean().reset_index()
        top_selling_products = data_filtered.groupby('Product')['Total Sales'].sum().sort_values(ascending=False).reset_index()
        monthly_sales_breakdown = data_filtered.groupby(data_filtered['Month'])['Total Sales'].sum().reset_index()

    return(retailer_sales_sum_by_date, profit_margin_over_time, top_selling_products, monthly_sales_breakdown)



total_sales = data["Total Sales"].sum()
total_units_sold = data["Units Sold"].sum()
best_client = data["Retailer"].value_counts().reset_index().iloc[0]["index"]

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"{total_sales:,} €")
col2.metric("Total Units Sold", f"{total_units_sold:,}")
col3.metric("Biggest Client", best_client)


top_selling_products_non_filtered = data.groupby(['Product', 'Retailer'])['Total Sales'].sum().sort_values(ascending=False).reset_index()
retailer_sales_sum_by_date = data.groupby(["Invoice Date", "Retailer"])["Total Sales"].sum().reset_index()


def create_moving_avergage(data, column, n):
    df = data
    df[column] = df[column].rolling(window=n).mean()

    return df


chart_column_1, chart_column_2 = st.columns(2)

CHART_COLOR = "#467599"

with chart_column_1:
    c = (
   alt.Chart(filter_chart_dataset(retailer_chosen, product_chosen)[3])
   .mark_line(interpolate = "monotone", strokeWidth = 3)
   .encode(x="Month", y="Total Sales:Q")
    ).configure_mark(color = CHART_COLOR).properties(title = {"text": f"Monthly Sales Breakdown - {retailer_chosen}",
                                                              "anchor": "middle"})

    st.altair_chart(c, use_container_width=True)

with chart_column_2:

    operating_profit = (
    alt.Chart(filter_chart_dataset(retailer_chosen, product_chosen)[1])
    .mark_line(interpolate = "monotone", opacity = 0.5, strokeWidth = 3)
    .encode(x="Invoice Date", y="Operating Profit:Q", color = alt.value(CHART_COLOR))
    ).properties(title = {"text": f"Operating Profit Breakdown (Moving Average) - {retailer_chosen}",
                                                             "anchor": "middle"})

    operating_profit_moving_average = (
   alt.Chart(create_moving_avergage(filter_chart_dataset(retailer_chosen, product_chosen)[1], "Operating Profit", 10))
   .mark_line(interpolate = "monotone", strokeWidth = 3)
   .encode(x="Invoice Date", y="Operating Profit:Q", color=alt.value('#D64045'))
    )
    combined_chart = operating_profit + operating_profit_moving_average

    layered_plot = alt.layer(operating_profit, operating_profit_moving_average).configure_legend(
                title=None,
                orient='right')

    st.altair_chart(layered_plot, use_container_width=True)


chart_row_2_column1, chart_row_2_column2  = st.columns(2)

with chart_row_2_column1:

    d = (alt.Chart(top_selling_products_non_filtered[top_selling_products_non_filtered["Retailer"] == retailer_chosen]).mark_bar(color = CHART_COLOR).encode(
    x='Total Sales:Q',
    y=alt.Y('Product:N', sort='-x'),
    tooltip = [alt.Tooltip('Product:N', title = "Product:"), alt.Tooltip('Total Sales:Q', format=',d', title='Total Sales:')]
    )).configure_mark(color = CHART_COLOR).properties(title = {"text": f"Top Selling Products - {retailer_chosen}",
                                                                "anchor": "middle"}, height = 400)
    st.altair_chart(d, use_container_width=True)


with chart_row_2_column2:

    monthly_sales_by_region = data.groupby(['Region', "Product"])['Total Sales'].sum().reset_index()

    pie_chart = alt.Chart(monthly_sales_by_region[monthly_sales_by_region["Product"] == product_chosen]).mark_arc(innerRadius = 60).encode(
        theta = "Total Sales",
        color = "Region",
        tooltip=[alt.Tooltip('Region:N', title = "Region:"), alt.Tooltip('Total Sales:Q', format=',d', title='Total Sales:')]
    ).properties(
        title=f"Sales Distribution by {product_chosen}"
    )


    circle_chart = alt.Chart(monthly_sales_by_region[monthly_sales_by_region["Product"] == product_chosen]).mark_circle(size=200, color='white').encode().properties(width=200, height=200)


    donut_chart = pie_chart + circle_chart
    st.altair_chart(pie_chart, use_container_width=True)





c = (
alt.Chart(retailer_sales_sum_by_date)
.mark_line()
.encode(x="Invoice Date", y="Total Sales:Q", tooltip=["Total Sales"])
).configure_mark(color = CHART_COLOR).properties(title = {"text": f"Sales Over Time",
                                                              "anchor": "middle"})

st.altair_chart(c, use_container_width=True)
