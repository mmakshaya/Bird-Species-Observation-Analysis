import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import pymysql

# --- Database Connection ---
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="EDA"
    )

# --- Query Execution ---
def execute_query(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# --- Load CSV Data ---
df = pd.read_csv('forest_bird.csv')
df1 = pd.read_csv('grassland_bird.csv')

# --- Page Configuration ---
st.set_page_config(
    page_title="Bird Species Observation Analysis",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🐦📊 Bird Monitoring Toolkit")

# Sidebar Navigation
page = st.sidebar.radio(
    "Select Dataset",
    ["🏠 Home", "🌲Forest Data Analysis", "🌾Grassland Data Analysis","🧾Detailed Report"]
)

# --- Home Page ---
if page == "🏠 Home":
    st.title("Welcome to the Bird Monitoring 🌲 Forest and 🌾  Grassland Toolkit")
    #st.title("🌲 Forest vs 🌾 Grassland Bird Monitoring")
    st.markdown("""This comparative dashboard summarizes priorities across **Forest** and **Grassland** ecosystems.""")
    col1, col2, col3 = st.columns(3)
    with col1:
      st.metric("Total Observations", "Forest: 8,444", "Grassland: 7,951")
    with col2:
      st.metric("Unique Species", "Forest: 102", "Grassland: 92")
    with col3:
      st.metric("Top Observer", "Elizabeth Oswald", "Highest across both")
    col4, col5, col6 = st.columns(3)
    with col4:
      st.metric("Detections(⬆Singing)", "Forest: 5,426", "Grassland: 4,421")
    with col5:
      st.metric("Detections ≤ 50m", "Grassland: 3,464", "Forest: 4,302")
    with col6:
      st.metric("Detections 50–100m", "Forest: 4,142", "Grassland: 5,040")
    col7, col8, col9 = st.columns(3)
    with col7:
      st.metric("Peak Time", "5–8 AM", "Most active in both habitats")
    with col8:
      st.metric("Most Observed Priority Species", "Wood Thrush", "Both habitats")
    with col9:
      st.metric("Rare Watchlist Species", "Kentucky Warbler", "Low in both")
    

# --- Forest Data Analysis Page ---
elif page == "🌲Forest Data Analysis":
    st.write("🌲Forest Data Analysis🐦")
    
    sub_page = st.sidebar.radio(
        "Forest Data Insights",
        ["🌍Species frequency per site","🌲Species Behavior and Detection Patterns","🌦️Environmental Influence","👩‍🔬 Observer Analysis","🗓️Temporal Analysis","🦜🌍Conservation Insights"]
    )

    if sub_page == "🌍Species frequency per site":
        richness_df = df.groupby('Admin_Unit_Code')['Common_Name'].nunique().reset_index()
        richness_df.columns = ['Admin_Unit_Code', 'Species_Richness']

        fig = px.bar(
          richness_df,
          x='Admin_Unit_Code',
          y='Species_Richness',
          #title='Species Richness per Admin Unit',
          labels={'Species_Richness': 'Unique Species Count'},
          color='Species_Richness',
          color_continuous_scale='Viridis'
        )
        st.title("Species Richness by Admin Unit")
        st.plotly_chart(fig)
        

        df_counts = df.groupby('Admin_Unit_Code')['Common_Name'].count().reset_index()
        df_counts.columns = ['Admin_Unit_Code', 'Bird_Count']

        fig = px.bar(
          df_counts,
          x='Admin_Unit_Code',
          y='Bird_Count',
          color='Bird_Count',
          color_continuous_scale='Viridis'
        )
        st.title("Count of Birds by Admin Unit")
        st.plotly_chart(fig)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The two bar charts reveal key patterns in bird abundance and diversity across different administrative units. Prince William Forest Park (PRWI) and C&O Canal Historical Park (CHOH) stand out with the highest total bird counts, suggesting these areas may provide more suitable habitats or attract greater bird activity. CHOH also has the highest number of unique bird species, indicating it is a biodiversity hotspot and potentially a priority area for conservation. In contrast, Wolf Trap National Park (WOTR) consistently shows the lowest bird count and species diversity, possibly reflecting ecological constraints or urban pressures. Interestingly, while PRWI leads in total bird numbers, its species diversity is lower than CHOH’s, suggesting a few species may dominate there. These patterns highlight the importance of tailored management strategies—protecting biodiversity-rich areas like CHOH and NACE, and investigating ecological limitations in lower-performing parks like WOTR.</p>", unsafe_allow_html=True)

    elif sub_page == "🌲Species Behavior and Detection Patterns":
        st.title("Time of detection")

    # Count detections per species per interval
        species_interval_counts = df.groupby(['Common_Name', 'Interval_Length']).size().unstack(fill_value=0)

    # Normalize by total detections per interval
        normalized_counts = species_interval_counts.div(species_interval_counts.sum(axis=0), axis=1)

    # Get all species and split into 5 groups
        all_species = normalized_counts.index.tolist()
        species_groups = [all_species[i::5] for i in range(5)]  # Split into 5 roughly equal groups

        group_labels = [f"Group {i+1}" for i in range(5)]
        group_dict = dict(zip(group_labels, species_groups))

        selected_groups = st.multiselect("Select Species Group:", group_labels, default=group_labels[:1])

        selected_species = [species for group in selected_groups for species in group_dict[group]]

    # Filter data
        filtered_data = normalized_counts.loc[normalized_counts.index.isin(selected_species)]

    # Melt for Plotly
        melted = filtered_data.reset_index().melt(id_vars='Common_Name', var_name='Interval', value_name='Proportion')

    # Plotly bar chart
        fig = px.bar(
          melted,
          x='Common_Name',
          y='Proportion',
          color='Interval',
          barmode='group',
          title="🕒 Proportional Detection of Bird Species by Time Interval",
          labels={'Common_Name': 'Species', 'Proportion': 'Proportional Observations'},
          height=500
        )

        st.plotly_chart(fig, use_container_width=True)
        
    
        df = df[df['Distance'].isin(['<= 50 Meters', '50 - 100 Meters'])]

    # Group by species and distance, then count
        species_counts = df.groupby(['Common_Name', 'Distance']).size().reset_index(name='Count')

        fig = px.scatter(
          species_counts,
          x='Common_Name',
          y='Count',
          color='Distance',
          symbol='Distance',
          title='Species Count by Distance Band',
          labels={'Common_Name': 'Species', 'Count': 'Observation Count'},
          size='Count',
        )

        fig.update_layout(
          xaxis_tickangle=-45,
          xaxis={'categoryorder': 'total ascending'},
          height=500
        )

        st.plotly_chart(fig, use_container_width=True)

# Filter and group by Distance        

        total_counts = df[df['Distance'].isin(['<= 50 Meters', '50 - 100 Meters'])] \
                 .groupby('Distance') \
                 .size() \
                 .reset_index(name='Total Observations')

# Display as a table or metric in Streamlit
        st.subheader("Total Bird Observations by Distance")
        st.dataframe(total_counts)


# Filter and group by ID_Method
        df['ID_Method'] = df['ID_Method'].str.strip()


        total_counts_id = (
          df[df['ID_Method'].isin(['Singing', 'Calling', 'Visualization'])]
          .groupby('ID_Method')
          .size()
          .reset_index(name='Total Observations')
        )

# Display in Streamlit
        st.subheader("Total Bird Observations by ID_Method")
        st.dataframe(total_counts_id) 

# Filter and group by visit

        total_counts_Visit = (
          df[df['Visit'].isin([1 , 2])]
          .groupby('Visit')
          .size()
          .reset_index(name='Total Observations')
        )
       
# Display in Streamlit
        st.subheader("Total Bird Observations by Visit")
        st.dataframe(total_counts_Visit) 


# Ensure 'Presence' is created from count column
        if 'Initial_Three_Min_Cnt' in df.columns:
            df['Presence'] = (df['Initial_Three_Min_Cnt'].fillna(0) > 0).astype(int)
        else:
            st.warning("Column 'Initial_Three_Min_Cnt' is missing, so 'Presence' could not be computed.")
            df['Presence'] = 0  # Fallback to zeros if column is missing

        species_list = df['Common_Name'].unique()
        selected_species = st.selectbox("Select a bird species", sorted(species_list))

# Filter data for selected species
        species_df = df[df['Common_Name'] == selected_species]

        st.subheader(f"Detection Method Analysis for {selected_species}")

# Group by ID Method
        method_summary = species_df.groupby('ID_Method')['Presence'].sum().reset_index(name='Detections')

# Plotly bar chart - Detection by Method
        fig_method = px.bar(
           method_summary,
           x='ID_Method',
           y='Detections',
           title=f'Detection Counts by Method: {selected_species}',
           labels={'ID_Method': 'Detection Method', 'Detections': 'Number of Detections'},
           color='ID_Method'
        )
        st.plotly_chart(fig_method, use_container_width=True)

# Distance Analysis
        st.subheader(f"Distance Effect on Detection for {selected_species}")

# Group by Distance
        distance_summary = species_df.groupby('Distance')['Presence'].sum().reset_index(name='Detections')

# Plotly bar chart - Detection by Distance
        fig_distance = px.bar(
          distance_summary,
          x='Distance',
          y='Detections',
          title=f'Detection Counts by Distance: {selected_species}',
          labels={'Distance': 'Distance from Observer', 'Detections': 'Number of Detections'},
          color='Distance'
        )
        st.plotly_chart(fig_distance, use_container_width=True)

        st.markdown("<p style='color: red;'>The bird observation dataset reveals meaningful patterns across distance, identification method, and time intervals. A total of 4302 detections were recorded within ≤ 50 meters, slightly more than the 4142 detections at 50–100 meters, indicating that birds are more easily detected at closer distances. Among identification methods, Singing (5426 detections) was the most common, followed by Calling (2675), while Visualization was rare (343), likely due to visibility constraints in the field. When examining detection over time, many species such as the Acadian Flycatcher, American Robin, and Northern Cardinal were more frequently detected in the first 2.5 minutes, likely due to heightened vocal activity or reduced disturbance early on. Conversely, species like the Wood Thrush and Scarlet Tanager were more commonly detected in later intervals, suggesting delayed behavioral responses. Some species, including the American Crow and Northern Flicker, maintained consistent detection across all intervals, reflecting steady presence or vocalization patterns. Rare species such as the Killdeer and Canada Goose were infrequently observed, possibly due to low abundance or unsuitable habitat. These insights suggest that while shorter surveys can effectively capture common, vocal species, they may underrepresent others—supporting the value of longer or multi-interval surveys.Visit 1 recorded slightly more bird observations (4,317) than Visit 2 (4,127), indicating similar bird activity levels during both visits. This suggests consistent observation conditions or bird presence across the two visits. </p>", unsafe_allow_html=True)
    
  
    elif sub_page == "🌦️Environmental Influence":
        st.title("Effect of environmental factor on Bird activity")

        st.subheader("Temperature vs Humidity by Species")
        fig_temp_hum = px.scatter(
          df,
          x="Temperature",
          y="Humidity",
          color="Common_Name",
          hover_data=["Scientific_Name", "Distance", "Observer", "Date"],
          title="Temperature vs Humidity Colored by Common Name"
        )
        st.plotly_chart(fig_temp_hum, use_container_width=True)

        wind_counts = df.groupby("Wind_Label").size().reset_index(name="Observation_Count")
        fig_wind_label = px.bar(
          wind_counts,
          x="Wind_Label",
          y="Observation_Count",
          title="Bird Observations by Wind Strength",
          labels={"Observation_Count": "Number of Observations"}
        )
        st.plotly_chart(fig_wind_label, use_container_width=True)
       
        wind_effect_richness = df.groupby("Wind_Label")["Common_Name"].nunique().reset_index(name="Species_Richness")
        fig_wind_effect_richness = px.bar(
          wind_effect_richness,
          x="Wind_Label",
          y="Species_Richness",
          title="Species Richness by Wind Effect",
          labels={"Species_Richness": "Unique Species Observed"}
        )
        st.plotly_chart(fig_wind_effect_richness, use_container_width=True)


        behavior_by_wind = df.groupby(["Wind_Label", "ID_Method"]).size().reset_index(name="Count")
        fig_behavior_wind = px.bar(
          behavior_by_wind,
          x="Wind_Label",
          y="Count",
          color="ID_Method",
          barmode="group",
          title="Bird Behavior (Singing vs Calling) by Wind Strength"
        )
        st.plotly_chart(fig_behavior_wind, use_container_width=True)

# Aggregations
        sky_counts = df.groupby("Sky").size().reset_index(name="Observation_Count")
        species_richness = df.groupby("Sky")["Common_Name"].nunique().reset_index(name="Species_Richness")
        behavior_by_sky = df.groupby(["Sky", "ID_Method"]).size().reset_index(name="Count")

        fig_obs = px.bar(
          sky_counts,
          x="Sky",
          y="Observation_Count",
          title="Bird Observations by Sky Condition",
          labels={"Observation_Count": "Number of Observations"}
        )

        fig_richness = px.bar(
          species_richness,
          x="Sky",
          y="Species_Richness",
          title="Species Richness by Sky Condition",
          labels={"Species_Richness": "Number of Unique Species"}
        )

        behavior_by_sky = df.groupby(["Sky", "ID_Method"]).size().reset_index(name="Count")
        fig_behavior = px.bar(
          behavior_by_sky,
          x="Sky",
          y="Count",
          color="ID_Method",
          barmode="group",
          title="Bird Behavior (Singing/Calling) by Sky Condition"
        )
        with st.expander("Analyze Sky Condition Impact"):
          view = st.selectbox("View type", ["Observation Count", "Species Richness", "Behavior (Singing vs Calling)"])

          if view == "Observation Count":
              st.plotly_chart(fig_obs, use_container_width=True)
          elif view == "Species Richness":
              st.plotly_chart(fig_richness, use_container_width=True)
          elif view == "Behavior (Singing vs Calling)":
              st.plotly_chart(fig_behavior, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The visualizations reveal the influence of weather conditions—sky and wind—on bird species richness, behavior, and detectability. Species richness and total bird observations are highest during clear or partly cloudy skies, indicating optimal visibility and bird activity under these conditions. In contrast, richness and detections decline significantly in foggy and misty conditions, likely due to both reduced bird activity and observer limitations. Similarly, bird observations and species richness peak with light air movement (1–3 mph) and calm winds (<1 mph), but decrease as wind speeds increase. Behavioral insights show birds are most often detected singing or calling during calm or lightly breezy conditions, with singing being the most common behavior regardless of wind. Finally, the temperature vs. humidity scatter plot, colored by species, shows bird activity is concentrated within a moderate temperature (15–25°C) and high humidity (70–90%) range, with some species showing preferences for specific conditions. These insights underscore the importance of considering weather conditions when planning and interpreting bird surveys, as they significantly affect species detectability and richness.</p>", unsafe_allow_html=True)


    elif sub_page == "👩‍🔬 Observer Analysis":
        st.title("👩‍🔬 Observer Contribution and Detection Performance")
    # Total observations per observer
        observer_counts = df.groupby("Observer").size().reset_index(name="Observation_Count")
    # Species richness per observer
        observer_richness = df.groupby("Observer")["Common_Name"].nunique().reset_index(name="Species_Richness")
    # Initial detection rate per observer
        observer_detection_rate = df.groupby("Observer")["Initial_Three_Min_Cnt"].mean().reset_index(name="Detection_Rate")
    #  Observer × Species matrix
        observer_species_matrix = df.groupby(["Observer", "Common_Name"]).size().reset_index(name="Count")
    # Merge for summary table
        observer_summary = observer_counts.merge(observer_richness, on="Observer").merge(observer_detection_rate, on="Observer")

        fig_obs_count = px.bar(
          observer_summary,
          x="Observer",
          y="Observation_Count",
          title="Total Observations by Observer"
        )

        fig_richness = px.bar(
          observer_summary,
          x="Observer",
          y="Species_Richness",
          title="Species Richness by Observer"
        )

        fig_detection = px.bar(
          observer_summary,
          x="Observer",
          y="Detection_Rate",
          title="Initial Detection Rate by Observer",
          labels={"Detection_Rate": "Proportion of Birds Detected in First 3 Minutes"}
        )

        fig_heatmap = px.density_heatmap(
          observer_species_matrix,
          x="Observer",
          y="Common_Name",
          z="Count",
          color_continuous_scale="Viridis",
          title="Observer × Species Detection Heatmap"
        )

        st.subheader("📋 Observer Summary Table")
        st.dataframe(observer_summary.sort_values(by="Observation_Count", ascending=False))

    # Optional: Download summary
        csv = observer_summary.to_csv(index=False)
        st.download_button("Download Observer Summary", csv, file_name="observer_summary.csv", mime="text/csv")

        st.subheader("📊 Observer Metrics")
        view = st.selectbox("Choose a metric to visualize", [
           "Total Observations", 
           "Species Richness", 
           "Initial Detection Rate"
        ])

        if view == "Total Observations":
           st.plotly_chart(fig_obs_count, use_container_width=True)
        elif view == "Species Richness":
           st.plotly_chart(fig_richness, use_container_width=True)
        elif view == "Initial Detection Rate":
           st.plotly_chart(fig_detection, use_container_width=True)

        st.subheader("🧬 Observer × Species Detection Heatmap")
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The analysis reveals notable variation in bird observation performance among observers. Elizabeth Oswald contributed the highest number of observations (3,248), detected the greatest number of unique species (98), and had the highest initial detection rate (60%), suggesting strong identification skills and survey efficiency. Kimberly Serno followed with 2,887 observations, 71 species, and a 55% detection rate, while Brian Swimelar had the lowest across all metrics, with 2,309 observations, 67 species, and a 49% detection rate. The observer × species heatmap highlights detection biases, indicating that Elizabeth consistently recorded a broader range of species. These findings underscore the importance of accounting for observer variability in ecological surveys to ensure data reliability and comparability.</p>", unsafe_allow_html=True)


    elif sub_page == "🗓️Temporal Analysis":
        st.title("Temporal Trends")
# Group data by species and month
        species_month_matrix = df.groupby(["Common_Name", "month_name"]).size().reset_index(name="Count")
# sort species by total count for readability
        top_species = (
          species_month_matrix.groupby("Common_Name")["Count"]
          .sum()
          .sort_values(ascending=False)
          #.head(20)
          .index
        )

        filtered_matrix = species_month_matrix[species_month_matrix["Common_Name"].isin(top_species)]

        fig = px.density_heatmap(
          filtered_matrix,
          x="month_name",
          y="Common_Name",
          z="Count",
          color_continuous_scale="Viridis",
          title="Bird Species Activity by Month",
          labels={"Count": "Observation Count"},
        )

        st.plotly_chart(fig, use_container_width=True)

# Convert Start_Time to datetime and create hour bins
        df["End_Hour"] = pd.to_datetime(df["End_Time"]).dt.hour

# Define time group bins
        bins = [4,8,10]  
        labels = ["5-8 AM","8-10 AM"]
        df["Time_Group"] = pd.cut(df["End_Hour"], bins=bins, labels=labels, right=False)

# Extract month name
        df["Month_Name"] = df["month_name"]

# Group data
        grouped = df.groupby(["Month_Name", "Common_Name", "Time_Group"]).size().reset_index(name="Count")

# Plot grouped bar chart
        fig = px.bar(
          grouped,
          x="Common_Name",
          y="Count",
          color="Time_Group",
          barmode="group",
          facet_col="Month_Name",
          title="Bird Observations by Time Group, Month, and Species",
          labels={"Common_Name": "Bird Species", "Time_Group": "Start Time Group"}
        )

        fig.update_layout(xaxis_tickangle=90)

# Streamlit display
        st.subheader("📅 Bird Detection by Time Group and Month")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The visualizations reveal that bird activity is highest in the month of June, with a notable concentration of observations occurring during the early morning hours between 5–8 AM. Across all three months—May, June, and July—this early time window consistently yields more bird sightings than the later period of 8–10 AM, highlighting it as the optimal time for birdwatching. Several species, such as the Red-eyed Vireo, Ovenbird, and Acadian Flycatcher, show particularly high observation counts, suggesting they are both abundant and active during this season. The heatmap further emphasizes June as the peak month for species activity, with a broader diversity of birds being observed at higher frequencies. These insights can inform better planning for bird monitoring and conservation efforts by focusing efforts in June during early morning hours. </p>", unsafe_allow_html=True)


    elif sub_page == "🦜🌍Conservation Insights":
        st.title("Watchlist Trends")
        st.write("Trends in species that are at risk or require conservation focus")

        # PIF Watchlist vs Not 
        pif_counts = df['PIF_Watchlist_Status'].value_counts()
        status_map = {1: 'On PIF Watchlist', 0: 'Not on PIF Watchlist'}
        labels1 = [status_map.get(index, 'Unknown') for index in pif_counts.index]
        percentages1 = (pif_counts / pif_counts.sum() * 100).round(1)
        legend1 = [f"{label} ({pct}%)" for label, pct in zip(labels1, percentages1)]
        colors1 = px.colors.qualitative.Set2[:len(legend1)]

        fig1 = go.Figure(data=[go.Pie(
            labels=legend1,
            values=pif_counts.values,
            hole=0.4,
            marker=dict(colors=colors1),
            sort=False,
            textinfo='none'
        )])
        fig1.update_layout(
            title_text='PIF Watchlist Species Proportion',
            margin=dict(t=50, b=50),
            height=300
        )

        # Species on PIF Watchlist 
        watchlist_species = df[df['PIF_Watchlist_Status'] == 1]['Common_Name']
        species_counts = watchlist_species.value_counts()
        fig2 = go.Figure(go.Bar(
            x=species_counts.values,
            y=species_counts.index,
            orientation='h',
            marker_color=px.colors.qualitative.Plotly[:len(species_counts)]
        ))
        fig2.update_layout(
            title_text='All PIF Watchlist Species (by Observations)',
            margin=dict(t=50, b=50),
            height=400,
            yaxis=dict(autorange="reversed")
        )

        # Regional Stewardship vs Not
        rs_counts = df['Regional_Stewardship_Status'].value_counts()
        rs_map = {1: 'Under Regional Stewardship', 0: 'Not Under Stewardship'}
        labels3 = [rs_map.get(index, 'Unknown') for index in rs_counts.index]
        percentages3 = (rs_counts / rs_counts.sum() * 100).round(1)
        legend3 = [f"{label} ({pct}%)" for label, pct in zip(labels3, percentages3)]

        fig3 = go.Figure(data=[go.Pie(
            labels=legend3,
            values=rs_counts.values,
            hole=0.4,
            marker=dict(colors=colors1),
            sort=False,
            textinfo='none'
        )])
        fig3.update_layout(
            title_text='Regional Stewardship Species Proportion',
            margin=dict(t=50, b=50),
            height=300
        )

        # All Regional Stewardship Species
        rs_species = df[df['Regional_Stewardship_Status'] == 1]['Common_Name']
        rs_species_counts = rs_species.value_counts()
        fig4 = go.Figure(go.Bar(
            x=rs_species_counts.values,
            y=rs_species_counts.index,
            orientation='h',
            marker_color=px.colors.qualitative.Plotly[:len(rs_species_counts)]
        ))
        fig4.update_layout(
            title_text='All Regional Stewardship Species (by Observations)',
            margin=dict(t=50, b=50),
            height=400,
            yaxis=dict(autorange="reversed")
        )

        st.subheader("PIF Watchlist Charts")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Regional Stewardship Charts")
        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(fig3, use_container_width=True)
        with col4:
            st.plotly_chart(fig4, use_container_width=True)

        # Priority Species Chart 
        priority_species_df = df[
            (df['PIF_Watchlist_Status'] == 1) &
            (df['Regional_Stewardship_Status'] == 1)
        ]

        priority_species_counts = priority_species_df['Common_Name'].value_counts().sort_values()

        fig_priority = go.Figure(data=[
            go.Bar(
                x=priority_species_counts.values,
                y=priority_species_counts.index,
                orientation='h',
                marker=dict(color='teal')
            )
        ])

        fig_priority.update_layout(
            title='Observations of Priority or Rare Species',
            xaxis_title='Number of Observations',
            yaxis_title='Common Name',
            height=300,
            width=300,
            margin=dict(t=50, b=50)
        )

        st.subheader("Priority or Rare Species Observations")
        st.plotly_chart(fig_priority, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The Data collectively reveal that the Wood Thrush is the most frequently observed species across both priority/rare and PIF Watchlist categories, indicating its relative abundance or ease of detection in the region. In contrast, other notable species such as the Worm-eating Warbler, Prairie Warbler, and Kentucky Warbler have significantly fewer observations, highlighting potential concerns regarding their population status or detectability. Additionally, the majority of observed species (71.1%) are not under regional stewardship, suggesting a potential gap between regional conservation responsibilities and the species most commonly encountered. These insights point to a need for more targeted monitoring and conservation strategies for less observed, high-priority species and a possible reevaluation of regional stewardship priorities.</p>", unsafe_allow_html=True)


# Grassland 
elif page == "🌾Grassland Data Analysis":
    st.write("🌾Grassland Data Analysis🐦")
    # Subpage Selector
    sub_page = st.sidebar.radio(
        "Grassland Data Insights",
        ["🌍Species frequency per site","🌲Species Behavior and Detection Patterns","🌦️Environmental Influence","👩‍🔬 Observer Analysis","🗓️Temporal Analysis","🦜🌍Conservation Insights"]
    )

    if sub_page == "🌍Species frequency per site":
        richness_df1 = df1.groupby('Admin_Unit_Code')['Common_Name'].nunique().reset_index()
        richness_df1.columns = ['Admin_Unit_Code', 'Species_Richness']
# Plot using Plotly
        fig = px.bar(
          richness_df1,
          x='Admin_Unit_Code',
          y='Species_Richness',
          labels={'Species_Richness': 'Unique Species Count'},
          color='Species_Richness',
          color_continuous_scale='Viridis'
        )
        st.title("Species Richness by Admin Unit")
        st.plotly_chart(fig)

        df1_counts = df1.groupby('Admin_Unit_Code')['Common_Name'].count().reset_index()
        df1_counts.columns = ['Admin_Unit_Code', 'Bird_Count']

        fig = px.bar(
          df1_counts,
          x='Admin_Unit_Code',
          y='Bird_Count',
          color='Bird_Count',
          color_continuous_scale='Viridis'
        )
        st.title("Count of Birds by Admin Unit")
        st.plotly_chart(fig)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The two charts provide insights into bird abundance and species diversity across four administrative units: ANTI, HAFE, MANA, and MONO. ANTI has the highest total bird count, indicating it may be a key area for overall bird abundance, followed by MONO and MANA, while HAFE has significantly fewer birds recorded. However, when considering species diversity, MONO stands out with the highest number of unique bird species observed, suggesting it supports a broader range of bird biodiversity. ANTI and MANA show similar species richness, despite differences in total bird count, while HAFE again trails behind in both total bird count and species diversity. These findings suggest that MONO may be especially important for conservation efforts focused on species diversity, while ANTI may serve as a hotspot for overall bird population density.</p>", unsafe_allow_html=True)

       

    elif sub_page == "🌲Species Behavior and Detection Patterns":
        st.title("Time of detection")

    # Count detections per species per interval
        species_interval_counts = df1.groupby(['Common_Name', 'Interval_Length']).size().unstack(fill_value=0)

    # Normalize by total detections per interval
        normalized_counts = species_interval_counts.div(species_interval_counts.sum(axis=0), axis=1)

    # Get all species and split into 5 groups
        all_species = normalized_counts.index.tolist()
        species_groups = [all_species[i::5] for i in range(5)]  # Split into 5 roughly equal groups

        group_labels = [f"Group {i+1}" for i in range(5)]
        group_dict = dict(zip(group_labels, species_groups))

        selected_groups = st.multiselect("Select Species Group:", group_labels, default=group_labels[:1])

        selected_species = [species for group in selected_groups for species in group_dict[group]]

    # Filter data
        filtered_data = normalized_counts.loc[normalized_counts.index.isin(selected_species)]

    # Melt for Plotly
        melted = filtered_data.reset_index().melt(id_vars='Common_Name', var_name='Interval', value_name='Proportion')

    # Plotly bar chart
        fig = px.bar(
          melted,
          x='Common_Name',
          y='Proportion',
          color='Interval',
          barmode='group',
          title="🕒 Proportional Detection of Bird Species by Time Interval",
          labels={'Common_Name': 'Species', 'Proportion': 'Proportional Observations'},
          height=500
        )

        st.plotly_chart(fig, use_container_width=True)
        
    
        df1 = df1[df1['Distance'].isin(['<= 50 Meters', '50 - 100 Meters'])]

    # Group by species and distance, then count
        species_counts = df1.groupby(['Common_Name', 'Distance']).size().reset_index(name='Count')

        fig = px.scatter(
          species_counts,
          x='Common_Name',
          y='Count',
          color='Distance',
          symbol='Distance',
          title='Species Count by Distance Band',
          labels={'Common_Name': 'Species', 'Count': 'Observation Count'},
          size='Count',
        )

        fig.update_layout(
          xaxis_tickangle=-45,
          xaxis={'categoryorder': 'total ascending'},
          height=500
        )

        st.plotly_chart(fig, use_container_width=True)

# Filter and group by Distance        

        total_counts = df1[df1['Distance'].isin(['<= 50 Meters', '50 - 100 Meters'])] \
                 .groupby('Distance') \
                 .size() \
                 .reset_index(name='Total Observations')

# Display as a table or metric in Streamlit
        st.subheader("Total Bird Observations by Distance")
        st.dataframe(total_counts)


# Filter and group by ID_Method
        df1['ID_Method'] = df1['ID_Method'].str.strip()


        total_counts_id = (
          df1[df1['ID_Method'].isin(['Singing', 'Calling', 'Visualization'])]
          .groupby('ID_Method')
          .size()
          .reset_index(name='Total Observations')
        )

# Display in Streamlit
        st.subheader("Total Bird Observations by ID_Method")
        st.dataframe(total_counts_id) 

# Filter and group by visit

        total_counts_Visit = (
          df[df['Visit'].isin([1 , 2])]
          .groupby('Visit')
          .size()
          .reset_index(name='Total Observations')
        )
       
# Display in Streamlit
        st.subheader("Total Bird Observations by Visit")
        st.dataframe(total_counts_Visit) 


       # Ensure 'Presence' is created from count column
        if 'Initial_Three_Min_Cnt' in df.columns:
            df1['Presence'] = (df1['Initial_Three_Min_Cnt'].fillna(0) > 0).astype(int)
        else:
            st.warning("Column 'Initial_Three_Min_Cnt' is missing, so 'Presence' could not be computed.")
            df1['Presence'] = 0  # Fallback to zeros if column is missing

        species_list = df['Common_Name'].unique()
        selected_species = st.selectbox("Select a bird species", sorted(species_list))

# Filter data for selected species
        species_df1 = df1[df1['Common_Name'] == selected_species]

        st.subheader(f"Detection Method Analysis for {selected_species}")

# Group by ID Method
        method_summary = species_df1.groupby('ID_Method')['Presence'].sum().reset_index(name='Detections')

# Plotly bar chart - Detection by Method
        fig_method = px.bar(
           method_summary,
           x='ID_Method',
           y='Detections',
           title=f'Detection Counts by Method: {selected_species}',
           labels={'ID_Method': 'Detection Method', 'Detections': 'Number of Detections'},
           color='ID_Method'
        )
        st.plotly_chart(fig_method, use_container_width=True)

# Distance Analysis
        st.subheader(f"Distance Effect on Detection for {selected_species}")

# Group by Distance
        distance_summary = species_df1.groupby('Distance')['Presence'].sum().reset_index(name='Detections')

# Plotly bar chart - Detection by Distance
        fig_distance = px.bar(
          distance_summary,
          x='Distance',
          y='Detections',
          title=f'Detection Counts by Distance: {selected_species}',
          labels={'Distance': 'Distance from Observer', 'Detections': 'Number of Detections'},
          color='Distance'
        )
        st.plotly_chart(fig_distance, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The charts and data together reveal key insights into bird observation dynamics across distance bands, time intervals, and detection types. Most bird observations occurred at distances of 50–100 meters (5,040), exceeding those recorded within 50 meters (3,464), suggesting that many species may be more detectable at slightly farther distances—possibly due to habitat structure or observer movement patterns. Detection behavior is dominated by singing (4,421), followed by visual sightings (2,700) and calling (1,383), indicating that auditory cues, particularly song, play a critical role in bird identification. Species-specific detection patterns across time intervals show that most species are observed within the first 5 minutes, especially during the 0.25–2.5 minute window, with a gradual decline thereafter—highlighting the importance of early-morning survey efficiency. Additionally, the similar bird counts from visit 1 (4,317) and visit 2 (4,127) suggest consistent observation rates, strengthening confidence in survey reliability and temporal coverage. Together, these findings support strategies for optimizing survey protocols by focusing on peak detection windows and leveraging sound-based identification methods.</p>", unsafe_allow_html=True)

        
    
    elif sub_page == "🌦️Environmental Influence":
        st.title("Effect of environmental factor on Bird activity")

        st.subheader("Temperature vs Humidity by Species")
        fig_temp_hum = px.scatter(
          df1,
          x="Temperature",
          y="Humidity",
          color="Common_Name",
          hover_data=["Scientific_Name", "Distance", "Observer", "Date"],
          title="Temperature vs Humidity Colored by Common Name"
        )
        st.plotly_chart(fig_temp_hum, use_container_width=True)

        wind_counts = df1.groupby("Wind_Label").size().reset_index(name="Observation_Count")
        fig_wind_label = px.bar(
          wind_counts,
          x="Wind_Label",
          y="Observation_Count",
          title="Bird Observations by Wind Strength",
          labels={"Observation_Count": "Number of Observations"}
        )
        st.plotly_chart(fig_wind_label, use_container_width=True)
       
        wind_effect_richness = df1.groupby("Wind_Label")["Common_Name"].nunique().reset_index(name="Species_Richness")
        fig_wind_effect_richness = px.bar(
          wind_effect_richness,
          x="Wind_Label",
          y="Species_Richness",
          title="Species Richness by Wind Effect",
          labels={"Species_Richness": "Unique Species Observed"}
        )
        st.plotly_chart(fig_wind_effect_richness, use_container_width=True)


        behavior_by_wind = df1.groupby(["Wind_Label", "ID_Method"]).size().reset_index(name="Count")
        fig_behavior_wind = px.bar(
          behavior_by_wind,
          x="Wind_Label",
          y="Count",
          color="ID_Method",
          barmode="group",
          title="Bird Behavior (Singing vs Calling) by Wind Strength"
        )
        st.plotly_chart(fig_behavior_wind, use_container_width=True)

    # Aggregations
        sky_counts = df1.groupby("Sky").size().reset_index(name="Observation_Count")
        species_richness = df1.groupby("Sky")["Common_Name"].nunique().reset_index(name="Species_Richness")
        behavior_by_sky = df1.groupby(["Sky", "ID_Method"]).size().reset_index(name="Count")

    # Plots
        fig_obs = px.bar(
          sky_counts,
          x="Sky",
          y="Observation_Count",
          title="Bird Observations by Sky Condition",
          labels={"Observation_Count": "Number of Observations"}
        )

        fig_richness = px.bar(
          species_richness,
          x="Sky",
          y="Species_Richness",
          title="Species Richness by Sky Condition",
          labels={"Species_Richness": "Number of Unique Species"}
        )

        behavior_by_sky = df1.groupby(["Sky", "ID_Method"]).size().reset_index(name="Count")
        fig_behavior = px.bar(
          behavior_by_sky,
          x="Sky",
          y="Count",
          color="ID_Method",
          barmode="group",
          title="Bird Behavior (Singing/Calling) by Sky Condition"
        )
        with st.expander("Analyze Sky Condition Impact"):
          view = st.selectbox("View type", ["Observation Count", "Species Richness", "Behavior (Singing vs Calling)"])

          if view == "Observation Count":
              st.plotly_chart(fig_obs, use_container_width=True)
          elif view == "Species Richness":
              st.plotly_chart(fig_richness, use_container_width=True)
          elif view == "Behavior (Singing vs Calling)":
              st.plotly_chart(fig_behavior, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>These graphs collectively provide insights into how various weather conditions—such as sky condition, wind strength, temperature, and humidity—affect bird behavior, observations, and species richness. Bird activity (especially singing) appears highest under partly cloudy and clear skies, suggesting favorable weather may stimulate vocal behavior. Similarly, most bird observations occurred during partly cloudy conditions and with light air movement (1–3 mph), indicating that moderate wind and mild weather increase visibility or presence of birds. Species richness was also greatest under light air movement, implying that slightly breezy conditions may support more diverse bird communities. Finally, the scatter plot of temperature vs. humidity colored by species name illustrates species-specific preferences, with some species clustering around certain environmental conditions. Overall, mild and moderately dynamic weather conditions seem to promote higher bird activity, detectability, and diversity.</p>", unsafe_allow_html=True)


    elif sub_page == "👩‍🔬 Observer Analysis":
        st.title("👩‍🔬 Observer Contribution and Detection Performance")
    # Total observations per observer
        observer_counts = df1.groupby("Observer").size().reset_index(name="Observation_Count")
    # Species richness per observer
        observer_richness = df1.groupby("Observer")["Common_Name"].nunique().reset_index(name="Species_Richness")
    # Initial detection rate per observer
        observer_detection_rate = df1.groupby("Observer")["Initial_Three_Min_Cnt"].mean().reset_index(name="Detection_Rate")
    #  Observer × Species matrix
        observer_species_matrix = df1.groupby(["Observer", "Common_Name"]).size().reset_index(name="Count")
    # Merge for summary table
        observer_summary = observer_counts.merge(observer_richness, on="Observer").merge(observer_detection_rate, on="Observer")

        fig_obs_count = px.bar(
          observer_summary,
          x="Observer",
          y="Observation_Count",
          title="Total Observations by Observer"
        )

        fig_richness = px.bar(
          observer_summary,
          x="Observer",
          y="Species_Richness",
          title="Species Richness by Observer"
        )

        fig_detection = px.bar(
          observer_summary,
          x="Observer",
          y="Detection_Rate",
          title="Initial Detection Rate by Observer",
          labels={"Detection_Rate": "Proportion of Birds Detected in First 3 Minutes"}
        )

        fig_heatmap = px.density_heatmap(
          observer_species_matrix,
          x="Observer",
          y="Common_Name",
          z="Count",
          color_continuous_scale="Viridis",
          title="Observer × Species Detection Heatmap"
        )

        st.subheader("📋 Observer Summary Table")
        st.dataframe(observer_summary.sort_values(by="Observation_Count", ascending=False))


        st.subheader("📊 Observer Metrics")
        view = st.selectbox("Choose a metric to visualize", [
           "Total Observations", 
           "Species Richness", 
           "Initial Detection Rate"
        ])

        if view == "Total Observations":
           st.plotly_chart(fig_obs_count, use_container_width=True)
        elif view == "Species Richness":
           st.plotly_chart(fig_richness, use_container_width=True)
        elif view == "Initial Detection Rate":
           st.plotly_chart(fig_detection, use_container_width=True)

        st.subheader("🧬 Observer × Species Detection Heatmap")
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The data visualizations and metrics reveal clear differences in bird observation performance among the three observers: Brian Swimelar, Elizabeth Oswald, and Kimberly Serno. Elizabeth Oswald stands out with the highest total number of observations (3,086), the highest species richness (97 unique species), and a strong initial detection rate (approximately 54%). Kimberly Serno follows closely with a comparable number of total observations (2,990) and an initial detection rate slightly higher than Elizabeth's (~55%), though her species richness is lower at 74 species. Brian Swimelar, in contrast, has the lowest figures across all metrics: total observations (2,428), species richness (63), and the lowest initial detection rate (~47%). The heatmap further supports these findings, indicating that Elizabeth Oswald detects a broader variety of species more frequently than the others. Overall, Elizabeth appears to be the most effective observer in terms of both quantity and diversity of bird detections, while Brian may benefit from strategies to improve early detections and species identification.</p>", unsafe_allow_html=True)
    
  
    elif sub_page == "🗓️Temporal Analysis":
        st.title("Temporal Trends")
# Group data by species and month
        species_month_matrix = df1.groupby(["Common_Name", "month_name"]).size().reset_index(name="Count")
# sort species by total count for readability
        top_species = (
          species_month_matrix.groupby("Common_Name")["Count"]
          .sum()
          .sort_values(ascending=False)
          #.head(20)
          .index
        )

        filtered_matrix = species_month_matrix[species_month_matrix["Common_Name"].isin(top_species)]

        fig = px.density_heatmap(
          filtered_matrix,
          x="month_name",
          y="Common_Name",
          z="Count",
          color_continuous_scale="Viridis",
          title="Bird Species Activity by Month",
          labels={"Count": "Observation Count"},
        )

        st.plotly_chart(fig, use_container_width=True)

# Convert Start_Time to datetime and create hour bins
        df1["End_Hour"] = pd.to_datetime(df1["End_Time"]).dt.hour

# Define time group bins
        bins = [4,8,10]  
        labels = ["5-8 AM","8-10 AM"]
        df1["Time_Group"] = pd.cut(df1["End_Hour"], bins=bins, labels=labels, right=False)

# Extract month name
        df1["Month_Name"] = df1["month_name"]

# Group data
        grouped = df1.groupby(["Month_Name", "Common_Name", "Time_Group"]).size().reset_index(name="Count")

# Plot grouped bar chart
        fig = px.bar(
          grouped,
          x="Common_Name",
          y="Count",
          color="Time_Group",
          barmode="group",
          facet_col="Month_Name",
          title="Bird Observations by Time Group, Month, and Species",
          labels={"Common_Name": "Bird Species", "Time_Group": "Start Time Group"}
        )

        fig.update_layout(xaxis_tickangle=90)

        st.subheader("📅 Bird Detection by Time Group and Month")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>chart illustrates that bird observations vary considerably between the 5–8 AM and 8–10 AM time groups, with the 5–8 AM period generally yielding higher counts. July shows a particularly high spike in observations for several species, including the Red-bellied Woodpecker and Eastern Meadowlark, suggesting peak activity or detectability in that month. June and May show a more even distribution of detections across species, though still dominated by early-morning observations.The second heatmap further emphasizes monthly variation in species activity. May stands out as the most active month for several species, especially Eastern Meadowlark, Field Sparrow, and Carolina Chickadee, which display intense observation concentrations. July shows increased observations for species like the Red-shouldered Hawk and Scarlet Tanager, while June exhibits relatively lower overall activity. These trends suggest that both time of day and time of year significantly influence bird visibility and detectability, with early mornings and the month of May generally offering the richest observation opportunities. </p>", unsafe_allow_html=True)


    elif sub_page == "🦜🌍Conservation Insights":
        st.title("Watchlist Trends")
        st.write("Trends in species that are at risk or require conservation focus")

        #  PIF Watchlist vs Not 
        pif_counts = df1['PIF_Watchlist_Status'].value_counts()
        status_map = {1: 'On PIF Watchlist', 0: 'Not on PIF Watchlist'}
        labels1 = [status_map.get(index, 'Unknown') for index in pif_counts.index]
        percentages1 = (pif_counts / pif_counts.sum() * 100).round(1)
        legend1 = [f"{label} ({pct}%)" for label, pct in zip(labels1, percentages1)]
        colors1 = px.colors.qualitative.Set2[:len(legend1)]

        fig1 = go.Figure(data=[go.Pie(
            labels=legend1,
            values=pif_counts.values,
            hole=0.4,
            marker=dict(colors=colors1),
            sort=False,
            textinfo='none'
        )])
        fig1.update_layout(
            title_text='PIF Watchlist Species Proportion',
            margin=dict(t=50, b=50),
            height=300
        )

        # Species on PIF Watchlist 
        watchlist_species = df1[df1['PIF_Watchlist_Status'] == 1]['Common_Name']
        species_counts = watchlist_species.value_counts()
        fig2 = go.Figure(go.Bar(
            x=species_counts.values,
            y=species_counts.index,
            orientation='h',
            marker_color=px.colors.qualitative.Plotly[:len(species_counts)]
        ))
        fig2.update_layout(
            title_text='All PIF Watchlist Species (by Observations)',
            margin=dict(t=50, b=50),
            height=400,
            yaxis=dict(autorange="reversed")
        )

        #  Regional Stewardship vs Not
        rs_counts = df1['Regional_Stewardship_Status'].value_counts()
        rs_map = {1: 'Under Regional Stewardship', 0: 'Not Under Stewardship'}
        labels3 = [rs_map.get(index, 'Unknown') for index in rs_counts.index]
        percentages3 = (rs_counts / rs_counts.sum() * 100).round(1)
        legend3 = [f"{label} ({pct}%)" for label, pct in zip(labels3, percentages3)]

        fig3 = go.Figure(data=[go.Pie(
            labels=legend3,
            values=rs_counts.values,
            hole=0.4,
            marker=dict(colors=colors1),
            sort=False,
            textinfo='none'
        )])
        fig3.update_layout(
            title_text='Regional Stewardship Species Proportion',
            margin=dict(t=50, b=50),
            height=300
        )

        # All Regional Stewardship Species 
        rs_species = df1[df1['Regional_Stewardship_Status'] == 1]['Common_Name']
        rs_species_counts = rs_species.value_counts()
        fig4 = go.Figure(go.Bar(
            x=rs_species_counts.values,
            y=rs_species_counts.index,
            orientation='h',
            marker_color=px.colors.qualitative.Plotly[:len(rs_species_counts)]
        ))
        fig4.update_layout(
            title_text='All Regional Stewardship Species (by Observations)',
            margin=dict(t=50, b=50),
            height=400,
            yaxis=dict(autorange="reversed")
        )

      
        st.subheader("PIF Watchlist Charts")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Regional Stewardship Charts")
        col3, col4 = st.columns(2)
        with col3:
            st.plotly_chart(fig3, use_container_width=True)
        with col4:
            st.plotly_chart(fig4, use_container_width=True)

        # Priority Species Chart
        priority_species_df1 = df1[
            (df1['PIF_Watchlist_Status'] == 1) &
            (df1['Regional_Stewardship_Status'] == 1)
        ]

        priority_species_counts = priority_species_df1['Common_Name'].value_counts().sort_values()

        fig_priority = go.Figure(data=[
            go.Bar(
                x=priority_species_counts.values,
                y=priority_species_counts.index,
                orientation='h',
                marker=dict(color='teal')
            )
        ])

        fig_priority.update_layout(
            title='Observations of Priority or Rare Species',
            xaxis_title='Number of Observations',
            yaxis_title='Common Name',
            height=300,
            width=300,
            margin=dict(t=50, b=50)
        )

        st.subheader("Priority or Rare Species Observations")
        st.plotly_chart(fig_priority, use_container_width=True)

        st.subheader("Insights:")
        st.markdown("<p style='color: red;'>The charts highlight the observation patterns of priority, stewardship, and watchlist bird species. Among priority or rare species, the Wood Thrush and Prairie Warbler were the most frequently observed, with nearly 20 detections each, while the Kentucky Warbler was observed only a few times, indicating its rarity or lower detectability. In the context of regional stewardship species, Field Sparrow and Indigo Bunting dominate with over 400 observations each, significantly outnumbering other species, suggesting these birds are both prevalent and possibly key indicators of habitat quality in the region. Meanwhile, the PIF (Partners in Flight) Watchlist species chart reinforces the importance of the Wood Thrush and Prairie Warbler, again ranking them highest in observations among species of conservation concern. These trends suggest a strong presence of certain priority species in the area, offering valuable opportunities for targeted conservation and monitoring, while highlighting species like the Kentucky Warbler that may require special attention due to lower detection rates.</p>", unsafe_allow_html=True)

elif page == "🧾Detailed Report":

    st.title("🦜 Comparative Analysis – Forest vs. Grassland")
    st.markdown("A comprehensive report based on avian survey data across two major habitat types: forests and grasslands.")

# Section 1: Species Frequency and Site Analysis
    st.header("1. Species Frequency and Site Analysis")
    st.subheader("🌲 Forest")
    st.markdown("""
    - **Prince William Forest Park (PRWI)** and **C&O Canal Historical Park (CHOH)** recorded the highest total bird counts.
    - **CHOH** also had the highest species diversity, identifying it as a biodiversity hotspot.
    - **Wolf Trap National Park (WOTR)** had the lowest abundance and diversity, possibly due to urban stress or habitat limitations.
    - **PRWI** was bird-rich but dominated by fewer species, indicating **low species evenness**.
    """)

    st.subheader("🌾 Grassland")
    st.markdown("""
    - **Antietam National Battlefield (ANTI)** had the highest bird abundance.
    - **Monocacy National Battlefield (MONO)** showed the highest species diversity, suggesting **habitat heterogeneity**.
    - **Harpers Ferry National Historical Park (HAFE)** had low abundance and diversity.
    """)
    st.subheader("🔄 Comparison Insight")
    st.markdown("""
    Forest sites generally supported **higher total bird counts and diversity**. However, some grasslands like **MONO** showed strong species diversity, likely due to varied microhabitats.
    """)

# Section 2: Species Behavior and Detection Patterns
    st.header("2. Species Behavior and Detection Patterns")
    st.subheader("🌲 Forest")
    st.markdown("""
    - Most birds were detected **within 50 meters**, suggesting denser acoustic detectability.
    - **Singing** was the dominant behavior (5,426 detections), followed by **calling** (2,675).
    - Some species (e.g., Wood Thrush, Scarlet Tanager) exhibited **delayed vocalization patterns**.
    - **Visit 1** saw slightly more activity than Visit 2.
    """)
    st.subheader("🌾 Grassland")
    st.markdown("""
    - Majority of detections occurred at **50–100 meters**, enabled by open visibility.
    - **Singing** was still dominant (4,421), but **visual detections (2,700)** were much higher than in forests.
    - Most detections occurred in the **first 5 minutes**, underscoring the importance of early surveys.
    - Detection rates were stable between Visit 1 and Visit 2.
    """)
    st.subheader("🔄 Comparison Insight")
    st.markdown("""
    Forests rely more on **close-range acoustic cues**, while grasslands benefit from **long-range visibility**. Both emphasize **early singing** for effective detection.
    """)

# Section 3: Environmental Influence
    st.header("3. Environmental Influence")
    st.subheader("🌲 Forest")
    st.markdown("""
    - Bird activity peaked under **clear/partly cloudy skies** and **light wind (<3 mph)**.
    - **Fog, mist, and wind** suppressed species richness.
    - Peak activity occurred at **15–25°C** and **high humidity (70–90%)**.
    """)
    st.subheader("🌾 Grassland")
    st.markdown("""
    - Partly cloudy skies and light air movement favored high activity.
    - Both **singing and species richness increased** in mild conditions.
    - Environmental responses were **species-specific** in scatter plot analyses.
    """)
    st.subheader("🔄 Comparison Insight")
    st.markdown("""
    Both habitats benefit from **mild weather**. Forest birds are more sensitive to **humidity**, while grassland birds respond more to **sky clarity and air movement**.
    """)

# Section 4: Observer Performance
    st.header("4. Observer Performance")

    st.markdown("""
    - **Elizabeth Oswald** was the top performer in both ecosystems.
       - Forest: 3,248 observations, 98 species
       - Grassland: 3,086 observations, 97 species
    - **Kimberly Serno** showed strong detection in grasslands but fewer species than Oswald.
    - **Brian Swimelar** consistently had the lowest counts and species detections.
    """)
    st.subheader("🔄 Comparison Insight")
    st.markdown("""
    Observer trends were consistent across ecosystems. Observer skill significantly affects results and must be **factored into ecological interpretation**.
    """)
# Section 5: Temporal Trends
    st.header("5. Temporal Trends")
    st.markdown("""
    - **Forest**:
       - Peak Month: **June**
       - Peak Time: **5–8 AM**
       - Key Species: *Red-eyed Vireo*, *Ovenbird*, *Acadian Flycatcher*

    - **Grassland**:
       - Peak Month: **May**
       - Peak Time: **5–8 AM**
      - Key Species: *Eastern Meadowlark*, *Field Sparrow*, *Carolina Chickadee*
    """)

    st.subheader("🔄 Comparison Insight")
    st.markdown("""
    Both ecosystems are most active during **early morning** hours, but **seasonal peaks differ**. These patterns reflect distinct breeding cycles and habitat cues.
    """)

# Section 6: Conservation Insights
    st.header("6. Conservation Insights")

    st.markdown("""
    - **Shared Priority Species**: *Wood Thrush*, *Prairie Warbler*
    - **Forest**: 71.1% of observed species **not under regional stewardship**, indicating a priority mismatch.
    - **Grassland**:
      - *Field Sparrow* and *Indigo Bunting* had strong stewardship presence (400+ detections).
      - *Kentucky Warbler* was under-detected in both ecosystems.

    🔍 **Concern**: *Kentucky Warbler* may need focused monitoring due to consistently low numbers.
    """)

# Conclusion
    st.header("✅ Conclusion")

    st.markdown("""
    The analysis reveals that bird monitoring efforts should be tailored to habitat-specific dynamics—acoustic detections work best in forests due to closer-range bird activity, while visual detections are more effective in open grasslands. Conservation resources should prioritize biodiversity hotspots like CHOH and MONO, while underperforming sites such as WOTR and HAFE warrant habitat restoration or disturbance mitigation. Surveys are most effective in the early morning (5–8 AM), especially during peak months—June for forests and May for grasslands—aligned with breeding activity. Observer training is crucial, as performance varies significantly; leveraging top observers can improve consistency. Environmental factors like sky clarity and wind should guide fieldwork timing to enhance species detection, with forest birds particularly sensitive to humidity. Importantly, grasslands show stronger alignment with stewardship species, suggesting a need to balance efforts across habitats. Under-detected species like the Kentucky Warbler require focused monitoring. These insights support adaptive, data-driven management to improve biodiversity outcomes and ecological stewardship.
    """)
    
 


