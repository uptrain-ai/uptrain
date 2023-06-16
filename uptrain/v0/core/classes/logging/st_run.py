import streamlit as st
import pandas as pd
from glob import glob
import os
import sys
import plotly.graph_objects as go
import numpy as np
import json
import plotly.express as px
import random
import pickle
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


st.set_page_config(
    page_title="UpTrain Dashboard",
    layout="wide",
    page_icon='https://github.com/uptrain-ai/uptrain/raw/dashboard/uptrain/core/classes/logging/uptrain_logo_icon.png'
)
st.title("UpTrain Live Dashboard")
st_style = """<style> footer {visibility: hidden;} </style>"""
st.markdown(st_style, unsafe_allow_html=True)

# Getting the streamlit log folder
log_folder = sys.argv[1]

# Get metadata
metadata_file = os.path.join(log_folder, "metadata.json")
with open(metadata_file, encoding='utf-8') as f:
    metadata = json.loads(f.read())
model_args = metadata['model_args']
feature_args = metadata['feature_args']

model_to_compare = None
other_models = {}
num_models_compare = 1
if model_args:
    if len(model_args) > 1:
        # st.sidebar.subheader("Select model type to compare against")
        all_model_types = []
        for model_type in model_args:
            all_model_types.append(model_type['feature_name'])
        model_selected = st.sidebar.selectbox("Model type to compare with", 
            all_model_types, key='select_model_args')
        model_compare_ind = all_model_types.index(model_selected)
        
        st.sidebar.subheader("Select other model types")
        for i, model in enumerate(model_args):
            if i==model_compare_ind:
                continue
            model_name = model['feature_name']
            value = st.sidebar.selectbox(model_name, model['allowed_values'], 
                key=f'model_{model_name}')
            other_models.update({model_name: value})

    elif len(model_args) == 1:
        model_compare_ind = 0   
    model_to_compare = model_args[model_compare_ind]
    num_models_compare = len(model_to_compare['allowed_values'])

features_to_slice = {}
if feature_args:
    st.sidebar.subheader("Select relevant features")
    for i, feature in enumerate(feature_args):
        feature_name = feature['feature_name']
        allowed_feats = feature['allowed_values']
        allowed_feats.insert(0, 'All')
        value = st.sidebar.selectbox(feature_name, allowed_feats, 
            key=f'feature_{feature_name}')
        if value != 'All':
            features_to_slice.update({feature_name: value})

def return_plotly_fig(y_axis, x_axis="Num predictions", x_log=False, y_log=False):
    fig = go.Figure()
    fig.update_xaxes(title_text=x_axis)
    fig.update_yaxes(title_text=y_axis)
    if x_log:
        fig.update_xaxes(type="log")
    if y_log:
        fig.update_yaxes(type="log")
    return fig


def slice_data(
    df, 
    features_to_slice=None, 
    model_to_compare=None, 
    other_models={},
    j=0,
    ):
    cond = None
    if features_to_slice is not None:
        for feat_name, value in features_to_slice.items():
            if value != 'All':
                if 'feature_' + feat_name in df.columns:
                    if cond is None:
                        cond = (df['feature_' + feat_name] == value)
                    else:
                        cond = cond & (df['feature_' + feat_name] == value)
                else:
                    cond = [False] * len(df)
    if model_to_compare is not None:
        model = model_to_compare['allowed_values'][j]
        model_type = model_to_compare['feature_name']
        if model_type in df.columns:
            if cond is None:
                cond = (df[model_type] == model)
            else:
                cond = cond & (df[model_type] == model)
        else:
            cond = [False] * len(df)
    for model_name, value in other_models.items():
        if model_name in df.columns:
            if cond is None:
                cond = (df[model_name] == value)
            else:
                cond = cond & (df[model_name] == value)
        else:
            cond = [False] * len(df)
    if cond is not None:
        df = df[cond]
    return df


def plot_line_charts(files, plot_name):
    # Getting plot metadata from the first file
    if len(files) > 1000:
        files = random.choices(files, k=1000)
    df = pd.read_csv(files[0])

    for key in df.keys():
        if key.startswith("x_"):
            x_axis = key
        if key.startswith("y_"):
            y_axis = key

    col1, col2 = st.columns(2)
    with col1:
        x_log = st.checkbox(
            "log x", help="x-axis in log-scale", key=plot_name + "x"
        )
    with col2:
        y_log = st.checkbox(
            "log y", help="y-axis in log-scale", key=plot_name + "y"
        )
    
    cols = st.columns(2)
    for j in range(num_models_compare):
        fig = return_plotly_fig(y_axis, x_axis, x_log, y_log)
        for i, csv_file in enumerate(files):
            # Reading the csv file
            df = pd.read_csv(csv_file)
            
            df = slice_data(df, features_to_slice, model_to_compare, other_models, j)

            # Getting plot_id
            plot_id = os.path.split(csv_file)[-1].split(".")[0]
            fig = fig.add_trace(
                go.Scatter(
                    x=df[x_axis],
                    y=df[y_axis],
                    name=str(i) + "," + plot_id,
                )
            )

        with cols[j % 2]:
            if model_to_compare is not None:
                model_name = model_to_compare['allowed_values'][j]
                st.subheader(f'Model: {model_name}')
            st.plotly_chart(fig, use_container_width=True)


def plot_histograms(files, plot_name): 
    cols = st.columns(2)
    for j in range(num_models_compare):
        fig = go.Figure()
        for i, csv_file in enumerate(files):
            # Reading the csv file
            df = pd.read_csv(csv_file)
            df = slice_data(df, features_to_slice, model_to_compare, other_models, j)

            # Getting plot_id
            plot_id = os.path.split(csv_file)[-1].split(".")[0]
            df_y = df['y_points']
            # if len(df_y) > 1000:
                # df_y = np.random.choice(df_y, 1000)
            fig = fig.add_trace(go.Histogram(x=df_y, name=plot_id))

        with cols[j % 2]:
            if model_to_compare is not None:
                model_name = model_to_compare['allowed_values'][j]
                st.subheader(f'Model: {model_name}')
            st.plotly_chart(fig, use_container_width=True)


def plot_histogram(file):
    with open(file, encoding='utf-8') as f:
        data = json.loads(f.read())
    if isinstance(data, dict):
        fig = go.Figure()
        for key in data.keys():
            fig = fig.add_trace(go.Histogram(x=data[key], name=key))
    else:
        fig = go.Figure(data=[go.Histogram(x=data)])
    st.plotly_chart(fig)


def plot_umap(file, j=0):
    with open(file, encoding='utf-8') as f:
        data = json.loads(f.read())
    arr = np.array(data["umap"])
    labels_dict = data["labels"]
    color_type = st.selectbox("Select coloring type", labels_dict.keys(), key=file)
    x = arr[:, 0]
    y = arr[:, 1]
    dictn = {'x': x, 'y': y, 'color': np.array(labels_dict[color_type])}
    hover_data = []
    if "hover_texts" in data:
        dictn.update({'hover': data['hover_texts']})
        if len(data['hover_texts']):
            hover_data = list(data['hover_texts'][0].keys())

    if arr.shape[1] == 3:
        dictn.update({'z': arr[:, 2]})

    for key in data.keys():
        if key not in ['umap', 'labels', 'hover_texts']:
            dictn.update({key: data[key]})
    df = pd.DataFrame(dictn)
    df = slice_data(df, features_to_slice, model_to_compare, other_models, j)

    if "hover" in list(df.columns):
        hover_df = pd.DataFrame(list(df['hover']))
        for key in hover_data:
            if key not in hover_df.columns:
                df[key] = [''] * len(hover_df)
            else:
                df[key] = pd.Series(hover_df[key]).fillna('').tolist()
    else:
        hover_df = pd.DataFrame()
    
    if arr.shape[1] == 2:
        fig = px.scatter(df, x='x', y='y', color='color', hover_data=hover_data)
    elif arr.shape[1] == 3:
        z = list(df['z'])
        fig = px.scatter_3d(df, x='x', y='y', z='z', color='color', hover_data=hover_data)
    else:
        raise ("Umap dimension not 2D or 3D.")
    st.plotly_chart(fig, use_container_width=True)
    # st.write(
    #     f"Number of clusters: {len(set(clusters))}"
    # )


def get_view_arr_from_files(files):
    view_arr = []
    for file in files:
        view_arr.append(int(os.path.split(file)[-1].split('_')[0]))
    view_arr.sort()
    return np.unique(view_arr)


@st.cache
def plot_umaps(files, plot_name, sub_dir):
    view_arr = get_view_arr_from_files(files)
    if len(view_arr > 0):
        selected_count = st.selectbox(f"Cluster View Point", view_arr, key=plot_name+'count')
    cols = st.columns(2)
    for j in range(num_models_compare):
        if model_to_compare is not None:
            model_compare_name = model_to_compare['allowed_values'][j]
            model_others_name = list(other_models.values())[0]
            file_name = str(selected_count) + '_' + model_compare_name + '_' + model_others_name + '.json'
            file_name = sub_dir + '/' + file_name
            with cols[j%2]:
                st.subheader(f'Model: {model_compare_name}, Signal: {model_others_name}, Count: {selected_count}')
                if os.path.exists(file_name):
                    plot_umap(file_name, j) 
                else:
                    st.write("Not sufficient data.")
        else:
            for file in files:
                count = os.path.split(file)[-1].split(".")[0]
                if int(count) < 0:
                    plot_umap(file, j) 
                else:
                    if st.checkbox(f"For count {count}", key=plot_name+str(count)):
                        plot_umap(file, j)  

def plot_bar(file):
    with open(file, encoding='utf-8') as f:
        data = json.loads(f.read())
    fig = go.Figure()
    for bar_name in data:
        if bar_name == "hover_text":
            continue
        bar_dict = data[bar_name]
        keys, values = zip(*bar_dict.items())
        if "hover_text" in data:
            hover_text = data['hover_text'][bar_name]
        else:
            hover_text = {}
        hover_text = list(hover_text.values())
        fig = fig.add_trace(
            go.Bar(
                x=list(keys),
                y=list(values),
                name=bar_name,
                hovertext=hover_text
            )
        )
    st.plotly_chart(fig)


def plot_for_count(files, plot_func, plot_name):
    for file in files:
        count = os.path.split(file)[-1].split(".")[0]
        if int(count) < 0:
            plot_func(file) 
        else:
            if st.checkbox(f"For count {count}", key=plot_name+str(count)):
                plot_func(file)          


def plot_dashboard(dashboard_name):
    st.header(f"Dashboard {dashboard_name}")
    sub_dirs = [path[0] for path in os.walk(os.path.join(log_folder, dashboard_name))]
    for sub_dir in sub_dirs:
        sub_dir_split = os.path.normpath(sub_dir).split(os.path.sep)
        c1 = sub_dir_split[-1] == "UMAP"
        c2 = sub_dir_split[-2] == "bar_graphs"
        c3 = sub_dir_split[-1] == "alerts"
        c4 = sub_dir_split[-1] == "t_SNE"
        if c1 or c2 or c3 or c4:
            ext = "*.json"
        else:
            ext = "*.csv"

        # Getting the list of relevant files in streamlit logs
        files = [file for path, _, _ in os.walk(sub_dir)
                    for file in glob(os.path.join(path, ext))]
        plot_name = sub_dir_split[-1]

        ######### Showing Alerts ###########

        if sub_dir_split[-1] == "alerts": 
            # First, sort files using human sorting. 
            files.sort(key=natural_keys)
            files.reverse()
            for file in files:
                alert_name = os.path.split(file)[-1].split(".")[0]
                f = open(file)
                alert = json.load(f)
                st.subheader(alert_name)
                st.markdown("##### " + alert)
                st.markdown("""---""")

        ######### Line Plots ###########

        elif sub_dir_split[-2] == "line_plots":
            if st.sidebar.checkbox(f"Line-plot for {plot_name}", key=plot_name+dashboard_name):
                st.markdown(f"### Line chart for {plot_name}")
                plot_line_charts(files, plot_name)
                st.markdown("""---""")    

        # ######### Plotting histograms ###########

        elif sub_dir_split[-2] == "histograms":
            if plot_name == "UMAP":
                if st.sidebar.checkbox(f"UMAP plot"):
                    st.markdown(f"### UMAP plot")
                    if model_args is not None:
                        plot_umaps(files, plot_name, sub_dir)
                    else:
                        for file in files:
                            plot_umap(file)
                    st.markdown("""---""")
            elif plot_name == "t_SNE":  
                if st.sidebar.checkbox(f"t-SNE plot"):
                    st.markdown(f"### t-SNE plot")
                    if model_args is not None:
                        plot_umaps(files, plot_name, sub_dir)
                    else:
                        for file in files:
                            plot_umap(file)
                    st.markdown("""---""")   
            else:
                if st.sidebar.checkbox(f"Histogram for {plot_name}"):
                    st.markdown(f"### Histogram for {plot_name}")
                    # plot_for_count(files, plot_histogram, plot_name) 
                    plot_histograms(files, plot_name)
                    st.markdown("""---""") 

        ######### Plotting Bar Graphs ###########

        elif sub_dir_split[-2] == "bar_graphs":
            if st.sidebar.checkbox(f"Bar graph for {plot_name}"):
                st.markdown(f"### Bar graph for {plot_name}")
                plot_for_count(files, plot_bar, plot_name) 
                st.markdown("""---""")  


        ######### Plotting Images ###########

        # elif sub_dir_split[-1] == "images":
        if True:
            png_files = [
                        file
                        for path, _, _ in os.walk(sub_dir)
                        for file in glob(os.path.join(path, "*.png"))
                    ]
            for i, png_file in enumerate(png_files):
                # Getting image name
                image_name = png_file.split("/")[-1].split(".")[0]
                st.subheader(image_name)
                st.image(png_file)


def get_data_shap(path_all_data, feat_name_list=None):
    file = open(metadata["path_shap_file"], 'rb')
    explainer = pickle.load(file)
    file.close()
    df = pd.read_csv(path_all_data)
    if type(df["id"][0]) == str:
        df["id"] = df["id"].apply(lambda x: eval(x))
    data_ids = [x for x in df["id"]]
    df = df.drop(columns=['id', 'output', 'gt'])
    if feat_name_list:
        df = df[feat_name_list]
    return explainer, df, data_ids

def feat_slice_and_plot(df, df_dashboard, relevant_feat_list, limit_list):
    cond = [True] * len(df)
    for i, feat_name in enumerate(relevant_feat_list):
        cond = (df[feat_name] >= limit_list[i][0]) & (
            df[feat_name] <= limit_list[i][1]
        ) & cond

    if len(df_dashboard) > len(df):
        # Append false to cond to make it of same length as df_dashboard
        cond2 = list(cond) + [False] * (len(df_dashboard) - len(df))
    else:
        cond2 = cond[0:len(df_dashboard)]
    
    df = df[cond]
    df_dashboard = df_dashboard[cond2]
    x_arr = df_dashboard["id"]
    y_arr = np.cumsum(np.array(df_dashboard[dashboard_name]))
    y_arr = y_arr / np.arange(1, len(df_dashboard)+1)
    fig = go.Figure()
    fig = fig.add_trace(go.Scatter(x=x_arr, y=y_arr))

    if relevant_feat_list:
        scol1, scol2 = st.columns(2)
        with scol1:
            st.plotly_chart(fig, use_container_width=True)
        

def feat_slice(metadata):
    feat_name_list = metadata["feat_name_list"]
    path_all_data = metadata["path_all_data"]
    path_dashboard_data = metadata["path_dashboard_data"]
    df = pd.read_csv(path_all_data)
    if os.path.exists(path_dashboard_data):
        df_dashboard = pd.read_csv(path_dashboard_data)
    else:
        return
    st.header(f"Feature slicing for {dashboard_name}")
    relevant_feat_list = st.multiselect(
            "Select features to slice", feat_name_list
        )
        
    scol1, scol2 = st.columns(2)
    limit_list = []
    for i, feat in enumerate(relevant_feat_list):
        max_val = max(df[feat])
        min_val = min(df[feat])
        if i % 2 == 0:
            with scol1:
                vals = st.slider(f"Select range for {feat}", 
                                 min_val, max_val, 
                                 (min_val, max_val))
        else:
            with scol2:
                vals = st.slider(f"Select range for {feat}", 
                                 min_val, max_val, 
                                 (min_val, max_val))
        limit_list.append(vals)
    
    feat_slice_and_plot(df, df_dashboard, relevant_feat_list, limit_list)

    
st.sidebar.title("Select dashboards to view")
dashboard_names = next(os.walk(log_folder))[1]
for dashboard_name in dashboard_names:
    if st.sidebar.checkbox(f"Dashboard: {dashboard_name}"):
        plot_dashboard(dashboard_name)

        # Get Dashboard Metadata for feature slicing
        local_metadata_file = os.path.join(log_folder, dashboard_name, "metadata.json")
        if os.path.exists(local_metadata_file):
            with open(local_metadata_file, encoding='utf-8') as f:
                local_metadata = json.loads(f.read())
            if local_metadata.get("feat_slicing", False):
                feat_slice(local_metadata)
    st.sidebar.markdown("""---""")

if metadata.get("path_shap_file", None):
    if st.sidebar.checkbox(f"SHAP explainability"):
        st.header(f"SHAP Explanability")
        
        path_all_data = metadata["path_all_data"]
        feat_name_list_shap = metadata.get("feat_name_list")
        num_points = metadata.get("shap_num_points")

        import shap
        shap.initjs() # for visualization
        st.set_option('deprecation.showPyplotGlobalUse', False)

        explainer, df, data_ids = get_data_shap(path_all_data, feat_name_list_shap)
        shap_values = explainer(df[:num_points])

        st.subheader("Feature-wise importance")
        cols = st.columns(2)
        with cols[0]:
            st.pyplot(shap.plots.bar(shap_values))

        st.markdown("""---""")

        st.subheader("Explainability for each data-point")
        cols = st.columns(2)
        with cols[0]:
            data_point = st.selectbox("Select data-point for explainability", data_ids)

        index = data_ids.index(data_point)
        shap_val = explainer(df.iloc[[index]])[0]
        pred = sum(shap_val.values) + shap_val.base_values
        st.text(f"The predicted value is {pred:.1f} compared to the mean value of {shap_val.base_values:.1f}.")
            
        cols = st.columns(2)
        with cols[0]:
            shap.plots.waterfall(shap_val)
            st.pyplot()