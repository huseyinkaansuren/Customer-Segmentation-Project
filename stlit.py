import streamlit as st
import pandas as pd
import datetime as dt
import main

st.set_page_config(layout="wide")
st.markdown("""<h1 style = 'text-align:center;'>Customer Segmentation</h1>""",unsafe_allow_html=True)

def preprocessing(dataframe, id,frequency, recency, date_day):
    st.session_state.disabled = False
    dataframe.dropna(inplace=True)

    dataframe[frequency] = st.session_state.data[frequency].astype(int)
    dataframe["frequency"] = st.session_state.data[frequency].sum(axis=1)
    dataframe = dataframe[dataframe["frequency"] > 0]


    if date_day == "Date":
        today = dt.datetime.today().date()
        dataframe["recency_days"] = pd.to_datetime(dataframe[recency], dayfirst=True).dt.date
        rfm = dataframe.groupby(id).agg({"recency_days":lambda date: (today - date.max()).days,
                                         "frequency": lambda num: num})
    else:
        dataframe["recency_days"] = dataframe[recency].astype(int)
        rfm = dataframe.groupby(id, as_index=False).agg({"recency_days": lambda date: date,
                                         "frequency": lambda num: num})

    rfm["recency_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5,4,3,2,1]).astype(int)
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels = [1,2,3,4,5]).astype(int)
    rfm["RFM_Score"] = (rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str))

    return rfm


def submit():
    st.write(st.session_state.input)
    st.write((st.session_state.rfm["ID"] == st.session_state.id_input).sum() > 0)
    st.session_state.id_input = st.session_state.input
    if (st.session_state.rfm["ID"] == st.session_state.id_input).sum() > 0:
        tab_seg_right.write(st.session_state.rfm[st.session_state.rfm["ID"] == st.session_state.id_input])
    else:
        tab_seg_right.write("Couldn't Find This Customer")



tab_upload, tab_data, tab_sel_columns , tab_segment_analys, tab_extract_cust = st.tabs(["Upload Data", "Data First Look", "Select Columns", "Customer Segments Analysis", "Extract Customers"])

with tab_upload:
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'], accept_multiple_files=False)
    tab_upload.write("After Uploading File Error In Below Will Disappear")
    if uploaded_file is not None:
        df_ = pd.read_csv(uploaded_file)
        df = df_.copy()

#Tab Data----------------------------------
tab_data.write("In this tab you can look glimpse of data. If data has a problem like collecting all values in a single column you can fix it here. If you still have a problem please wait an update.")
try:
    tab_data.write(df.head())
except:
    pass
split_data_button = tab_data.button("If data has problem with values click this")
if split_data_button:
    df = main.split_data(df)
    st.session_state.data = df
    tab_data.write(st.session_state.data.head())
else:
    st.session_state.data = df


#Tab Select Columns--------------------------------
tab_sel_columns.write("In this tab please select columns that need for segmentation")
columns = df.columns
columns = columns.insert(0, " ")
customer_Id = tab_sel_columns.selectbox("Select Customer ID column:", columns)
total_transaction = tab_sel_columns.multiselect(
    "Select Transaction Count Columns(Number of Web Purchases, Number of Store Purchases and etc.):", columns)

date_or_day_column = tab_sel_columns.selectbox(
    "Select Column That Customer's Last Transaction Date or Column Indicating How Many Days Have Passed Since The Last Transaction",
    columns)
date_or_day = " "
if date_or_day_column is not " ":
    date_or_day = tab_sel_columns.radio("Please Select Type of Last Selection", ["Date", "Day"])

prep_button = tab_sel_columns.button("Do Preprocessing")
if prep_button:
    st.session_state.rfm = preprocessing(st.session_state.data, customer_Id, total_transaction, date_or_day_column, date_or_day)
else:
    pass

#TAB SEGMENT ANALYSIS-----------------------------
tab_segment_analys.write("In this tab you can examine customers by segments.")


# Disable the submit button after it is clicked
def disable():
    st.session_state.disabled = True

# Initialize disabled for form_submit_button to False
if "disabled" not in st.session_state:
    st.session_state.disabled = False

st.session_state.seg_button = tab_segment_analys.button("Do Segmentation", key = "seg_but", on_click=disable, disabled= st.session_state.disabled)

if st.session_state.seg_button:
    st.session_state.rfm = main.segmentation(st.session_state.rfm)


if st.session_state.disabled == True:
    tab_seg_left, tab_seg_right = tab_segment_analys.columns(2)
    tab_seg_left.write(st.session_state.rfm[["segment","recency_days","frequency"]].groupby("segment").agg(["mean", "count"]))

    st.session_state.input = tab_seg_right.text_input("Enter Customer ID you want to check", key = "input", on_change=submit)

try:
    #TAB EXTRACT CUSTOMERS

    cust_segments = tab_extract_cust.multiselect("Select Segments You want to extract:", st.session_state.rfm["segment"].unique())
    extract_button = tab_extract_cust.button("Extract These Segment Customers")

    if extract_button:
        spec_customers = st.session_state.rfm[st.session_state.rfm["segment"].isin(cust_segments)]
        spec_customers_idx = pd.Series(spec_customers.index)
        spec_customers_idx.to_csv("spec_customers_idx.csv")
except:
    pass