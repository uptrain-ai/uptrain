import plotly.express as px
import pandas as pd
import streamlit as st 


class StreamlitLogs():
    # st.set_page_config(
    #     page_title="UpTrain AI Dashboard",
    #     layout="wide",
    # )
    # dashboard title
    st.title("UpTrain AI Live Dashboard")
    def __init__(self, log_every=10):
        self.log_every = log_every
        self.placeholders = {}
        self.prev_values = {}
        self.dfs = {}
        self.counts = {}

    def add_scalar(self, label, value):
        # Update the dataframe
        df = self.dfs.get(label, pd.DataFrame())
        df = pd.concat([df, pd.DataFrame({label: value}, index=[0])], ignore_index=True)
        self.dfs[label] = df

        count = self.counts.get(label, 0)
        if count % self.log_every == 0:
            prev_value = self.prev_values.get(label, 0)
            placeholder = self.placeholders.get(label, st.empty())
            with placeholder.container():
                st.metric(label, value, delta=value-prev_value)
                st.markdown(f"### Line chart for {label}")
                fig = px.line(x=df.index, y=df[label])
                st.write(fig)
                st.markdown(f"### Data view for {label}")
                st.dataframe(df)
            self.prev_values[label] = value
            self.placeholders[label] = placeholder
        self.counts[label] = count + 1
    

    def add_scalars(self, label, dict):
        # Update the dataframe
        df = self.dfs.get(label, pd.DataFrame())
        # Currently supports only adding one entry at a time
        try:
            df = pd.concat([df, pd.DataFrame(dict, columns=dict.keys())], ignore_index=True)
        except:
            df = pd.concat([df, pd.DataFrame(dict, index=[0])], ignore_index=True)   
        
        self.dfs[label] = df
        count = self.counts.get(label, 0)
        if count % self.log_every == 0:
            prev_value_dict = self.prev_values.get(label, {})
            placeholder = self.placeholders.get(label, st.empty())
            with placeholder.container():
                kpis = st.columns(len(dict)) 
                for i,key in enumerate(dict.keys()):
                    try:
                        # Displaying the latest value if a list was passed
                        val = dict[key][-1]
                    except:
                        val = dict[key]
                    prev = prev_value_dict.get(key, 0)
                    kpis[i].metric(key, val, delta=val-prev)
                    prev_value_dict[key] = val
                
                st.markdown(f"### Line chart for {label}")
                fig = px.line(df)
                st.write(fig)
                st.markdown(f"### Data view for {label}")
                st.dataframe(df)
            self.placeholders[label] = placeholder
            self.prev_values[label] = prev_value_dict
        self.counts[label] = count + 1
    
    def add_histogram(self, label, value):
        # Update the dataframe
        df = self.dfs.get(label, pd.DataFrame())
        df = pd.concat([df, pd.DataFrame({label: value}, index=[0])], ignore_index=True)
        self.dfs[label] = df

        count = self.counts.get(label, 0)
        if count % self.log_every == 0:
            placeholder = self.placeholders.get(label, st.empty())
            with placeholder.container():
                st.markdown(f"### Histogram for {label}")
                fig = px.histogram(df, x=label)
                st.write(fig)
                st.markdown(f"### Data view for {label}")
                st.dataframe(df)
            self.placeholders[label] = placeholder
        self.counts[label] = count + 1

    def feat_slicing(self, fw):
        relevant_feat_list = st.sidebar.multiselect("Select features", fw.feat_name_list, fw.feat_name_list[0])
        scol1, scol2 = st.sidebar.columns(2)
        limit_list = []
        for feat in relevant_feat_list:
            with scol1:
                lower_limit = st.sidebar.slider(f"Lower limit for {feat}", value=0.5)
            with scol2:
                upper_limit = st.sidebar.slider(f"Upper limit for {feat}", value=0.55)
            limit_list.append((lower_limit, upper_limit))
        # button_callback = lambda : fw.feat_slicing(relevant_feat_list, limit_list)
        
        # TODO: Function is run from top every time the button is clicked
        button = st.sidebar.button("Check", help="Check anomalies for this function",)
            # on_click=button_callback)
        if button:
            fw.feat_slicing(relevant_feat_list, limit_list)

