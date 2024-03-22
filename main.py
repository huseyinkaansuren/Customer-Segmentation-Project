import pandas as pd
import numpy as np

def split_data(dataframe):
    new_cols = dataframe[dataframe.columns[0]].str.split("\t", expand=True)
    new_cols.columns = dataframe.columns
    dataframe = new_cols
    return dataframe


def segmentation(rfm):
    seg_map = {
        r"[1-2][1-2]": "hibernating",
        r"[1-2][3-4]": "at_Risk",
        r"[1-2]5": "cant_loose",
        r"3[1-2]": "about_to_sleep",
        r"33": "need_attention",
        r"[3-4][4-5]": "loyal_customers",
        r"41": "promising",
        r"51": "new_customers",
        r"[4-5][2-3]": "potential_loyalists",
        r"5[4,5]": "champions"
    }

    rfm["segment"] = rfm["RFM_Score"].replace(seg_map, regex=True)
    return rfm
