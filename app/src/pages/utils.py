import streamlit as st
import pandas as pd
import datetime as dt

from src.constants import month_names, operations_dict, sel_data_defaults

# return filtered df according if col_name contains selected_val
def filter_by_colvalue(df, col_name, st_container=None, mssg=None, options=[], transpose={}, key=None):
    cont = st_container if st_container else st
    values = ["ALL", ]+list(df[col_name].unique()) if len(options)==0 else options
    kwargs = {"key": key} if key else {}
    selected_val = cont.selectbox(mssg if mssg else 'Select '+col_name, values, **kwargs)
    if selected_val!="ALL": #check if it is required to filter df
         #transponse option name to possible value in col of df
        selected_val = transpose[selected_val] if bool(transpose) else selected_val
        return df.loc[df[col_name] == selected_val]
    return df.copy()

# return filtered df according range of dates chosen
def filter_by_dates(df, st_containers, level="day", filter=True, store_dates=False, use_stored=False, key=None):
    state = st.session_state
    init_year = state["init_year"] if "init_year" in state else 2017
    end_year = state["end_year"] if "end_year" in state else 2021
    init_month = "January" if "init_month" not in state else state["init_month"]
    end_month = "December" if "end_month" not in state else state["end_month"]
    is_ym = level == "year_month"
    st_cs = st_containers if isinstance(st_containers, list) else [st_containers, ]*(1+1*(level != "day")+2*is_ym)
    if level == "year" or is_ym:  # two radio buttons selectors to select initial and ending years
        init_year = st_cs[0].radio('Select initial year', list(range(2017, end_year+1)), init_year-2017, key="init_year")
        end_year = st_cs[1].radio('Select ending year', list(range(init_year, 2022)), end_year-init_year, key="end_year")
    if level == "month" or (is_ym and init_year == end_year):
        init_month = st_cs[0+2*is_ym].selectbox('Select initial month', month_names[:month_names.index(
            end_month)+1], month_names.index(init_month), key="init_month")
        end_month = st_cs[1+2*is_ym].selectbox('Select ending month', month_names[month_names.index(init_month):], month_names.index(
            end_month)-month_names.index(init_month), key="end_month")
    elif is_ym:
        init_month = st_cs[2].selectbox('Select initial month', month_names)
        end_month = st_cs[3].selectbox('Select ending month', month_names, len(month_names)-1)
    if level=="day": # time slider to select range of dates
        start = state["init_date"] if use_stored else dt.date(2017, 1, 1)
        end = state["end_date"] if use_stored else dt.date(2021, 8, 31)
        init_date, end_date = st_cs[0].slider('Select range of dates', start, end, (start, end), format="MM/DD/YY", **{"key":key} if key else {})
    else:  # set dates if there is not time slider
        init_month = month_names.index(init_month)+1
        end_month = month_names.index(end_month)+1
        init_date = dt.date(init_year, init_month, 1)
        end_date = dt.date(end_year, end_month+1, 1) - dt.timedelta(days=1) if end_month != 12 else dt.date(end_year, end_month, 31)
        if store_dates:
            state["init_date"], state["end_date"] = init_date, end_date
    if filter:
        df_dates = pd.to_datetime(df[['Year', 'Month', 'Day']])
        return df.loc[(df_dates >= str(init_date)) & (df_dates <= str(end_date))]
    return init_date, end_date

# return df grouped by the specified cols computing the selected operation
def aggregate_df(df, cols_group, cols_operate, operation="Mean", selection_data={}):
    if bool(selection_data):
        s_data = [selection_data[k] if k in selection_data else d for k, d in sel_data_defaults]
        operation = s_data[0].radio(s_data[1], s_data[2], key=s_data[3])
    operation = operations_dict[operation]
    return df.pivot_table(cols_operate, index=cols_group, aggfunc=operation).reset_index()
