import streamlit as st
import plotly.express as px
import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title='Superstore!!', page_icon=':bar_chart:', layout='wide')

st.title(" :bar_chart: Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

f1 = st.file_uploader(":file_folder: Upload your dataset", type=['csv','txt', 'xls','xlsx'])
if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_excel(filename, engine="xlrd")
else:
    os.chdir(r"E:\Streamlit project")
    df = pd.read_excel("Superstore.xls", engine="xlrd")

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"]) 


StartDate = pd.to_datetime(df["Order Date"]).min()
EndDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", StartDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", EndDate))  

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy() 
#create for region

st.sidebar.header("choose your filter")
region = st.sidebar.multiselect("Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

#create for state
state = st.sidebar.multiselect("Pick your state", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

#create for city
city = st.sidebar.multiselect("Pick your city", df3["City"].unique())
##    df4 = df3.copy()
#else:
 #   df4 = df3[df3["City"].isin(city)]

#filter the data based on Region, State and city
if not region and not state and not city:
    filtered_df = df
elif not state and city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and city:
    filtered_df = df[df["State"].isin(state)]  
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

for col in filtered_df.columns:
    if filtered_df[col].dtype == 'object':
        filtered_df[col] = filtered_df[col].astype(str)


category_df = filtered_df.groupby(by= ["Category"], as_index= False) ["Sales"].sum() 
category_df = category_df.astype(str)
category_df["Sales"] = category_df["Sales"].astype(float)  # convert back for plotting


with col1:
    st.subheader("Category Wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template= "seaborn")
    st.plotly_chart(fig, use_container_width=True, height= 200)

with col2:
    st.subheader("Region Wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole= 0.5)
    fig.update_traces(text= filtered_df["Sales"], textposition= "outside")
    st.plotly_chart(fig, use_container_width=True)
    
cl1, cl2 = st.columns((2))
with cl1:
        with st.expander("Category_ViewData"):
            st.write(category_df.style.background_gradient(cmap= "Blues"))
            csv = category_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                               help="Click to download data as CSV")
            
with cl2:
        with st.expander("Region_ViewData"):
            region = filtered_df.groupby(by= ["Region"], as_index= False) ["Sales"].sum()
            st.write(region.style.background_gradient(cmap= "Oranges"))
            csv = region.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                               help="Click to download data as CSV")  

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M") 
st.subheader('Time Series Analysis')

linechart= pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime('%Y : %m'))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x= "month_year", y= "Sales", labels= {"Sales": "Amount"}, height= 500, width= 1000, template= "gridon")
st.plotly_chart(fig2, use_container_width=True)
linechart = linechart.astype(str)
linechart["Sales"] = linechart["Sales"].astype(float)


with st.expander("TimeSeries_ViewData"):
    st.write(linechart.T.style.background_gradient(cmap= "Blues"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv",
                       help="Click to download data as CSV")

# create a treem based on Region, Category and Sub-Category
st.subheader("Hierachical view of Sales using TreeMap")
fig3 = px.treemap(filtered_df, path= ["Region", "Category", "Sub-Category"], values= "Sales", hover_data= ["Sales"],
                  color= "Sub-Category")
fig3.update_layout(width= 800, height= 650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment Wise Sales")
    fig4 = px.pie(filtered_df, values= "Sales", names= "Segment", template="plotly_dark")
    fig4.update_traces(text= filtered_df["Segment"], textposition= "inside")
    st.plotly_chart(fig4, use_container_width=True)

with chart2:
    st.subheader("Category Wise Sales")
    fig5 = px.pie(filtered_df, values= "Sales", names= "Category", template="gridon")
    fig5.update_traces(text= filtered_df["Category"], textposition= "inside")
    st.plotly_chart(fig5, use_container_width=True)


import plotly.figure_factory as ff
import numpy as np
st.subheader(":point_right: Month Wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Profit", "Quantity"]]
    fig6 = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig6, use_container_width=True)

    st.markdown("*Month Wise Sub-Category Sales Summary*")
    filtered_df["Month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year= pd.pivot_table(data= filtered_df, values= "Sales", index= ["Sub-Category"], columns= "Month")
    sub_category_Year = sub_category_Year.fillna(0)
    st.write(sub_category_Year.style.background_gradient(cmap= "Blues"))

#create a scatter plot
#data1= px.scatter(filtered_df, x= "Sales", y= "Profit", size= "Quantity")
#data1['layout'].update(title="Relationship between Sales and Profit Using Scatter plot",
 #                      titlefont=dict(size=20),xaxis= dict(title="Sales", titlefont=dict(size=19)),
  #                        yaxis= dict(title="Profit", titlefont=dict(size=19))) 
#st.plotly_chart(data1, use_container_width=True)                            