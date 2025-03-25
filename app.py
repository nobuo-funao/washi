import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Upload a CSV and Analyze Data")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
  df = pd.read_csv(uploaded_file)
  st.write("DataFrame Preview:")
  st.write(df.head())
  vars  = [c for c in df.columns]
  value = st.selectbox("Variable", vars)
  group = st.selectbox("Group", vars)

  if st.checkbox('Grouped'):
    summary_stats = df.groupby(group)[value].describe()
    st.subheader("Summary Statistics by Group")
    st.write(summary_stats)

    st.subheader("Histogram by Group")
    groups = df[group].unique()
    num_groups = len(groups)

    if num_groups <11:
      fig, axs = plt.subplots(num_groups, 1, figsize=(10, 5 * num_groups))
      if num_groups == 1:
        axs = [axs]
      for ax, grp in zip(axs, groups):
        group_data = df[df[group] == grp][value]
        ax.hist(group_data, bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax.set_title(f'Histogram of Values for Group {grp}')
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
      plt.tight_layout()
      st.pyplot(fig)

  else:
    summary_stats = df[value].describe()
    st.subheader("Summary Statistics by Group")
    st.write(summary_stats)

    st.subheader("Histogram")
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.hist(df[value], bins=20, alpha=0.7, color='blue', edgecolor='black')
    ax.set_title(f'Histogram of Values')
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    plt.tight_layout()
    st.pyplot(fig)
