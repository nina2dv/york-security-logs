import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import streamlit as st
from scipy.stats import chi2_contingency
import seaborn as sns

@st.experimental_memo
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def app():
    # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

    # ---- READ EXCEL ----
    df_2019 = pd.read_csv("Security Incident Logs 2019.csv")
    df_2020 = pd.read_csv("Security Incident Logs 2020.csv")
    df_2021 = pd.read_csv("Security Incident Logs 2021.csv")

    df = pd.concat([df_2019, df_2020, df_2021])
    df.dropna(inplace=True)
    df['Reported Date'] = pd.to_datetime(df['Reported Date'], format='%m/%d/%Y')
    df['year'] = df['Reported Date'].dt.year
    df['month'] = df['Reported Date'].dt.month
    df['day'] = df['Reported Date'].dt.day
    df['hour'] = pd.to_datetime(df['Reported Time']).dt.hour
    df['hour'] = df['hour'].astype('int')
    df["day_of_week"] = df['Reported Date'].dt.dayofweek

    # st.dataframe(df)


    # ---- SIDEBAR ----
    st.sidebar.header("Please Filter Here:")
    year = st.sidebar.multiselect(
        "Select the year:",
        options=df["year"].unique(),
        default=df["year"].unique()
    )

    month = st.sidebar.multiselect(
        "Select the month:",
        options=df["month"].unique(),
        default=df["month"].unique(),
    )
    day_of_week = st.sidebar.multiselect(
        "Select the day of the week:",
        options=df["day_of_week"].unique(),
        default=df["day_of_week"].unique(),
    )
    hour = st.sidebar.multiselect(
        "Select the hour:",
        options=df["hour"].unique(),
        default=df["hour"].unique(),
    )
    category = st.sidebar.multiselect(
        "Select the category:",
        options=df["Category"].unique(),
        default=df["Category"].unique(),
    )

    location = st.sidebar.multiselect(
        "Select the location:",
        options=df["Location"].unique(),
        default=df["Location"].unique()
    )

    df_selection = df.query(
        "day_of_week == @day_of_week & year == @year & month ==@month & Category == @category & Location == @location & hour == @hour"
    )
    # st.dataframe(df_selection)
    # ---- MAINPAGE ----
    # st.title(":bar_chart: York University Security Incident Logs")

    st.markdown("##")

    # User input filter
    user_select = st.text_input('Search Bar', 'Enter to search the dataframe')
    df_selection = df_selection[df_selection.apply(lambda row: row.astype(str).str.contains(user_select, case=False, na=False).any(), axis=1)]


    # Stats
    total_logs = df_selection.shape[0]
    average_rating = df_selection[df_selection['Location'].str.contains("PARKING")].shape[0]
    average_sale_by_transaction = df_selection[df_selection['Location'].str.contains("GLENDON")].shape[0]
    res_logs = df_selection[df_selection['Location'].str.contains("RESIDENCE")].shape[0]

    # average_logs = round(df_selection["Rating"].mean(), 1)
    # star_rating = ":star:" * int(round(average_rating, 0))
    # average_sale_by_transaction = round(df_selection["Total"].mean(), 2)

    leftmost_column, left_column, middle_column, right_column = st.columns(4)
    with leftmost_column:
        st.subheader("Total Logs:")
        st.subheader(f"{total_logs:,}")
    with left_column:
        st.subheader("Residence Logs:")
        st.subheader(f"{res_logs:,}")
    with middle_column:
        st.subheader("Parking Logs:")
        st.subheader(f"{average_rating}")
    with right_column:
        st.subheader("Glendon Logs:")
        st.subheader(f"{average_sale_by_transaction}")

    # Displayed dataframe
    st.dataframe(df_selection)
    


    csv = convert_df(df_selection)

    st.download_button(
       "Click Here to Download Filtered Dataframe",
       csv,
       "file.csv",
       "text/csv",
       key='download-csv'
    )
    st.markdown("""---""")

    # SALES BY PRODUCT LINE [BAR CHART]

    try:
        type_loc_cross = pd.crosstab(df_selection["Category"], df_selection["Location"], rownames=["Category"], colnames=["Location"])
        # st.dataframe(type_loc_cross)
        Offense_Location_prop = round(type_loc_cross.div(type_loc_cross.sum(axis=1), axis=0) * 100, 2)
        # st.dataframe(Offense_Location_prop)

        fig, ax = plt.subplots(1, 1, figsize=(30, 18))
        sns.heatmap(Offense_Location_prop, ax=ax)
        st.write(fig)
    except:
        st.write('Graph not available!* :sunglasses:')
    left_col, right_col = st.columns(2)
    with left_col:
        try:
            st.markdown("#### Crosstab Category vs. Day of the week")
            type_dow_cross = pd.crosstab(df['Category'], df['day_of_week'])
            st.dataframe(type_dow_cross)
        except:
            st.write('Graph not available!* :sunglasses:')
    with right_col:
        try:
            type_loc_cross = pd.crosstab(df_selection["Category"], df_selection["Location"], rownames=["Category"],
                                         colnames=["Location"])
            g, p, dof, expctd = chi2_contingency(type_loc_cross)
            st.subheader("p-value of Chi-square test for Category vs. Location:")
            st.subheader(f"{p}")
            st.markdown("""---""")
            g, p, dof, expctd = chi2_contingency(type_dow_cross)
            st.subheader(f"p-value of Chi-square test for Category vs. Day of week:")
            st.subheader(f"{p}")
        except:
            st.write('Chi-square test not available!* :sunglasses:')


    try:
        cat_count = (
            df_selection.groupby(['Category', 'month']).size().reset_index(name='counts')
        )
        line_chart = alt.Chart(cat_count).mark_area().encode(
            y=alt.Y('counts', title='count', stack="normalize"),
            x=alt.X('month', title='Month'),
            color="Category"
        ).properties(
            height=350, width=700,
            title="Monthly reports per category"
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(line_chart, use_container_width=True)
    except:
        st.write('Graph not available!* :sunglasses:')

    try:
        cat_count = (
            df_selection.groupby(['Category', 'Reported Date']).size().reset_index(name='counts')
        )
        line_chart = alt.Chart(cat_count).mark_line().encode(
            y=alt.Y('counts', title='count'),
            x=alt.X('Reported Date', title='Day'),
            color="Category"
        ).properties(
            height=350, width=700,
            title="Daily reports per category"
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(line_chart, use_container_width=True)
    except:
        st.write('Graph not available!* :sunglasses:')
    leftG_column, rightG_column = st.columns(2)
    with leftG_column:
        try:
            cat_count = (
                df_selection.groupby(['Category', 'day_of_week']).size().reset_index(name='counts')
            )
            line_chart = alt.Chart(cat_count).mark_line().encode(
                y=alt.Y('counts', title='count'),
                x=alt.X('day_of_week', title='Day of the week'),
                color="Category"
            ).properties(
                height=350, width=700,
                title="Day of the week reports per category"
            ).configure_title(
                fontSize=16
            )

            st.altair_chart(line_chart, use_container_width=True)
        except:
            st.write('Graph not available!* :sunglasses:')
    with rightG_column:
        try:
            dailyGraph = df_selection.groupby(['day_of_week']).size().reset_index(name='incident_counts')
            line_chart = alt.Chart(dailyGraph).mark_trail().encode(
                y=alt.Y('incident_counts', title='count'),
                x=alt.X('day_of_week', title='Day of the week'),
            ).properties(
                height=350, width=700,
                title="Total day of the week reports"
            ).configure_title(
                fontSize=16
            )
            st.altair_chart(line_chart, use_container_width=True)
        except:
            st.write('Graph not available!* :sunglasses:')

    try:
        cat_count = (
            df_selection.groupby(['Location', 'month']).size().reset_index(name='counts')
        )
        line_chart = alt.Chart(cat_count).mark_area().encode(
            y=alt.Y('counts', title='count', stack="normalize"),
            x=alt.X('month', title='Month'),
            color="Location"
        ).properties(
            height=350, width=700,
            title="Monthly reports per location"
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(line_chart, use_container_width=True)
    except:
        st.write('Graph not available!* :sunglasses:')

    left_chart, right_chart = st.columns(2)
    with left_chart:
        try:
            log_counts = df_selection.groupby(['Category']).size().reset_index(name='incident_counts')
            bar_chart1 = alt.Chart(log_counts).mark_bar().encode(
                y=alt.Y('Category', title='Category'),
                x=alt.X('incident_counts', title='count'),
            ).properties(
                height=850,
                width=500,
                title="Total reports per category"
            ).configure_title(
                fontSize=16
            )

            st.altair_chart(bar_chart1, use_container_width=True)

        except:
            st.subheader('Graph not available!* :sunglasses:')
    with right_chart:
        try:
            sub_log_count = df_selection.groupby(['Subcategory']).size().reset_index(name='incident_counts')
            bar_chart2 = alt.Chart(sub_log_count).mark_bar().encode(
                y=alt.Y('Subcategory', title='Subcategory'),
                x=alt.X('incident_counts', title='count'),
            ).properties(
                height=850,
                width=500,
                title="Total reports per subcategory"
            ).configure_title(
                fontSize=16
            )

            st.altair_chart(bar_chart2, use_container_width=True)

        except:
            st.subheader('Graph not available!* :sunglasses:')

    try:
        log_counts = df_selection.groupby(['Location']).size().reset_index(name='incident_counts')
        line_chart = alt.Chart(log_counts).mark_bar().encode(
            y=alt.Y('incident_counts', title='count'),
            x=alt.X('Location', title='Location'),
        ).properties(
            height=350, width=700,
            title="Total reports per location"
        ).configure_title(
            fontSize=16
        )
        st.altair_chart(line_chart, use_container_width=True)
    except:
        st.write('Graph not available!* :sunglasses:')
    leftG_column, rightG_column = st.columns(2)
    with leftG_column:
        try:
            monthlyGraph = df_selection.groupby(['month']).size().reset_index(name='incident_counts')
            line_chart = alt.Chart(monthlyGraph).mark_trail().encode(
                y=alt.Y('incident_counts', title='Count'),
                x=alt.X('month', title='Months'),
            ).properties(
                height=350, width=700,
                title="Total monthly reports"
            ).configure_title(
                fontSize=16
            )
            st.altair_chart(line_chart, use_container_width=True)
        except:
            st.write('Graph not available!* :sunglasses:')
    with rightG_column:
        try:
            hourGraph = df_selection.groupby(['hour']).size().reset_index(name='incident_counts')
            line_chart = alt.Chart(hourGraph).mark_trail().encode(
                y=alt.Y('incident_counts', title='Count'),
                x=alt.X('hour', title='Hour'),
            ).properties(
                height=350, width=700,
                title="Total hourly reports"
            ).configure_title(
                fontSize=16
            )
            st.altair_chart(line_chart, use_container_width=True)
        except:
            st.write('Graph not available!* :sunglasses:')

    try:
        dailyGraph = df_selection.groupby(['Reported Date']).size().reset_index(name='incident_counts')
        line_chart = alt.Chart(dailyGraph).mark_trail().encode(
            y=alt.Y('incident_counts', title='count'),
            x=alt.X('Reported Date', title='Reported Date'),
        ).properties(
            height=350, width=700,
            title="Total daily reports"
        ).configure_title(
            fontSize=16
        )
        st.altair_chart(line_chart, use_container_width=True)
    except:
        st.write('Graph not available!* :sunglasses:')



