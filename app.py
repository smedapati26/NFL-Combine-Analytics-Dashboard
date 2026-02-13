import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="NFL Combine Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

px.defaults.template = "plotly_dark"

# --------------------------------------------------
# CUSTOM FONT + GLOBAL STYLING
# --------------------------------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Press+Start+2P&display=swap');

html, body, [class*="css"]  {
    font-family: 'Montserrat', sans-serif;
}

/* Background */
.stApp {
    background-color: #0D0D12;
    color: #EAEAF0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #15151F;
}

/* Gradient Hero Title */
.hero-title {
    text-align: center;
    font-size: 44px;
    font-weight: 800;
    background: linear-gradient(90deg, #6A0DAD, #B026FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

/* Subtitle */
.hero-sub {
    text-align: center;
    color: #BBBBCC;
    margin-bottom: 30px;
}

/* Section Card */
.section-card {
    background: #15151F;
    border-radius: 14px;
    padding: 15px;
    margin: 12px 0;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background-color: #1A1A26;
    padding: 12px;
    border-radius: 14px;
    box-shadow: 0px 4px 20px rgba(176,38,255,0.4);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #6A0DAD, #B026FF);
    color: white;
    font-weight: 600;
    border-radius: 10px;
    border: none;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #8E2DE2, #B026FF);
    transform: scale(1.02);
}

/* DataFrame */
[data-testid="stDataFrame"] {
    border-radius: 12px;
}

/* Sliders */
[data-baseweb="slider"] [role="slider"] {
    background-color: #B026FF !important;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------
st.markdown('<div class="hero-title">NFL Combine Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Advanced Combine Performance & Pipeline Intelligence (2010–2023)</div>', unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("nfl_combine_2010_to_2023.csv")

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Rename columns to consistent format
    df = df.rename(columns={
        "pos": "position",
        "broad jump": "broad_jump",
        "40yd": "forty",
        "3cone": "threecone"
    })

    return df

@st.cache_data
def load_player_info():
    players = pd.read_csv("players.csv")
    players.columns = players.columns.str.strip().str.lower()
    return players

df = load_data()
players_df = load_player_info()

# Clean names for merge
df["player_clean"] = df["player"].str.strip().str.lower()
players_df["player_clean"] = players_df["display_name"].str.strip().str.lower()

# Merge headshot column
df = df.merge(
    players_df[["player_clean", "headshot"]],
    on="player_clean",
    how="left"
)

# --------------------------------------------------
# GLOBAL DISPLAY LABELS (Use Everywhere)
# --------------------------------------------------
DISPLAY_LABELS = {
    "forty": "40 Yard Dash",
    "vertical": "Vertical Jump",
    "bench": "Bench Press",
    "broad_jump": "Broad Jump",
    "threecone": "3 Cone Drill",
    "shuttle": "Shuttle",
    "year": "Year",
    "player": "Player",
    "position": "Position",
    "school": "School"
}

# Ensure numeric columns are numeric
numeric_cols = ["year", "weight", "forty", "vertical",
                "bench", "broad_jump", "threecone", "shuttle"]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_year,
    max_year,
    (2010, 2023)
)

positions = sorted(df["position"].dropna().unique())
selected_position = st.sidebar.selectbox(
    "Select Position",
    ["All"] + positions
)

# Apply filters
filtered_df = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1])
]

if selected_position != "All":
    filtered_df = filtered_df[filtered_df["position"] == selected_position]

event_options = {
    f"{DISPLAY_LABELS['forty']} (Fastest)": ("forty", True),
    f"{DISPLAY_LABELS['vertical']} (Highest)": ("vertical", False),
    f"{DISPLAY_LABELS['bench']} (Most Reps)": ("bench", False),
    f"{DISPLAY_LABELS['broad_jump']} (Highest)": ("broad_jump", False),
    f"{DISPLAY_LABELS['threecone']} (Fastest)": ("threecone", True),
    f"{DISPLAY_LABELS['shuttle']} (Fastest)": ("shuttle", True),
}

selected_event_label = st.selectbox(
    "Select Performance Metric",
    list(event_options.keys())
)

metric, ascending_sort = event_options[selected_event_label]

st.markdown('<div class="section-card">', unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Players", len(filtered_df))
k2.metric("Unique Schools", filtered_df["school"].nunique())
k3.metric("Positions", filtered_df["position"].nunique())
k4.metric("Years Selected", f"{year_range[0]}–{year_range[1]}")

st.markdown('</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.1, 1])

with col_left:
    # --------------------------------------------------
    # 1. TRUE U.S. STATE MAP
    # --------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.header("College Production Map")

    # --- Manual school → state mapping ---
    # Add more schools as needed
    school_state_map = {
        "Alabama": "AL",
        "Auburn": "AL",
        "Notre Dame": "IN",
        "LSU": "LA",
        "Ohio State": "OH",
        "Michigan": "MI",
        "Florida": "FL",
        "Florida State": "FL",
        "Georgia": "GA",
        "Texas": "TX",
        "Texas A&M": "TX",
        "Oklahoma": "OK",
        "USC": "CA",
        "UCLA": "CA",
        "Clemson": "SC",
        "Penn State": "PA",
        "Tennessee": "TN",
        "Oregon": "OR",
        "Washington": "WA",
        "Wisconsin": "WI",
        "Iowa": "IA",
        "North Carolina": "NC",
        "NC State": "NC",
        "South Carolina": "SC",
        "Arkansas": "AR",
        "Mississippi State": "MS",
        "Ole Miss": "MS",
        "Kentucky": "KY",
        "Miami (FL)": "FL",
    }

    # Create state column
    filtered_df["state"] = filtered_df["school"].map(school_state_map)

    # Drop schools not mapped
    state_df = filtered_df.dropna(subset=["state"])

    # Count players per state
    state_counts = (
        state_df.groupby("state")
        .size()
        .reset_index(name="player_count")
    )

    fig_state_map = px.choropleth(
        state_counts,
        locations="state",
        locationmode="USA-states",
        color="player_count",
        scope="usa",
        color_continuous_scale=["#2A003F", "#6A0DAD", "#B026FF"],
        title="NFL Combine Players by College State"
    )

    fig_state_map.update_layout(
        paper_bgcolor="#0D0D12",
        plot_bgcolor="#0D0D12",
        font_color="#EAEAF0"
    )

    st.plotly_chart(fig_state_map, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    # --------------------------------------------------
    # 2. PIPELINE ANALYSIS (Dynamic Metric + Auto Ordering)
    # --------------------------------------------------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.header("Pipeline Strength by Position")

    if selected_position == "All":
        st.markdown("""
        <div style="
            text-align:center;
            color: #666;
            font-size: 13px;
            margin-top: 40px;
        ">
            Pipeline analysis available when a position is selected
        </div>
        """, unsafe_allow_html=True)
    else:
        # Use the currently selected metric from Top Performers
        pipeline_df = filtered_df.dropna(subset=[metric])

        # Keep top 8 schools by player count
        top_schools = (
            pipeline_df.groupby("school")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(8)["school"]
        )

        pipeline_df = pipeline_df[pipeline_df["school"].isin(top_schools)]

        # Determine sorting direction automatically
        # ascending_sort = True means lower is better (e.g., 40 time)
        if ascending_sort:
            median_order = (
                pipeline_df.groupby("school")[metric]
                .median()
                .sort_values(ascending=True)
                .index
                .tolist()
            )
        else:
            median_order = (
                pipeline_df.groupby("school")[metric]
                .median()
                .sort_values(ascending=False)
                .index
                .tolist()
            )

        fig = px.box(
            pipeline_df,
            x="school",
            y=metric,
            points="all",
            category_orders={"school": median_order},
            title=f"{DISPLAY_LABELS[metric]} Distribution by School ({selected_position})",
            labels={
                "school": "School",
                metric: DISPLAY_LABELS[metric]
            },
            color_discrete_sequence=["#B026FF"]
        )

        fig.update_traces(
            marker=dict(
                size=6,
                color="#B026FF",
                opacity=0.7
            ),
            line=dict(width=2)
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            transition_duration=500,
            paper_bgcolor="#0D0D12",
            plot_bgcolor="#15151F",
            font_color="#EAEAF0",
            hoverlabel=dict(
                bgcolor="#1A1A26",
                font_size=14,
                font_family="Arial"
            )
        )
        fig.update_layout(transition_duration=500)
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="black",
                font_size=14,
                font_family="Arial"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 3. TOP PERFORMERS TABLE
# --------------------------------------------------
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.header("Elite Combine Performances")

performance_df = filtered_df.dropna(subset=[metric])

top_n = st.slider("Number of Top Performers", 5, 50, 10)

top_performers = (
    performance_df
    .sort_values(metric, ascending=ascending_sort)
    .head(top_n)
    [["player", "position", "school", "year", metric]]
)

top_performers = top_performers.rename(columns=DISPLAY_LABELS)

st.dataframe(top_performers, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 4. ALL-TIME BEST OPTION
# --------------------------------------------------
st.header("All-Time Best Performances (2010–2023)")

all_time_df = df.dropna(subset=[metric])

if selected_position != "All":
    all_time_df = all_time_df[all_time_df["position"] == selected_position]

all_time_top = (
    all_time_df
    .sort_values(metric, ascending=ascending_sort)
    .head(top_n)
    [["player", "position", "school", "year", metric]]
)

# Rename columns using global label dictionary
all_time_top = all_time_top.rename(columns=DISPLAY_LABELS)

st.dataframe(all_time_top, use_container_width=True, hide_index=True)

# --------------------------------------------------
# 5. INTERACTIVE PLAYER COMPARISON TOOL
# --------------------------------------------------
def ordinal(n):
    n = int(round(n))
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.header("Player Comparison Tool")

comparison_df = df.copy()

compare_metrics = ["forty", "vertical", "bench",
                   "broad_jump", "threecone", "shuttle"]

comparison_df = comparison_df.dropna(subset=compare_metrics)

players = sorted(comparison_df["player"].unique())

col1, col2 = st.columns(2)

with col1:
    player1 = st.selectbox("Select First Player", players)

with col2:
    player2 = st.selectbox("Select Second Player", players, index=1)

if player1 and player2:

    # --------------------------------------------------
    # Get Selected Player Rows FIRST
    # --------------------------------------------------
    p1_data = comparison_df[comparison_df["player"] == player1].iloc[0]
    p2_data = comparison_df[comparison_df["player"] == player2].iloc[0]

    # --------------------------------------------------
    # PLAYER IMAGES (VISUAL UPGRADE)
    # --------------------------------------------------
    def display_headshot(url):
        if (
            pd.notna(url)
            and isinstance(url, str)
            and "static.www.nfl.com" in url
        ):
            if "{formatInstructions}" in url:
                url = url.replace("{formatInstructions}", "t_headshot_desktop")
            return url
        else:
            return "no_player.png"

    def circular_image(url, size=130):
        return f"""
            <div style="text-align: center;">
                <img src="{url}" 
                     style="
                         width: {size}px;
                         height: {size}px;
                         border-radius: 50%;
                         object-fit: cover;
                         border: 3px solid #B026FF;
                         box-shadow: 0px 0px 20px rgba(176,38,255,0.7);
                     ">
            </div>
        """

    img1, img2 = st.columns(2)

    with img1:
        st.subheader(player1)
        url1 = display_headshot(p1_data["headshot"])
        st.markdown(circular_image(url1), unsafe_allow_html=True)

    with img2:
        st.subheader(player2)
        url2 = display_headshot(p2_data["headshot"])
        st.markdown(circular_image(url2), unsafe_allow_html=True)

    # --------------------------------------------------
    # Animated Percentile Comparison Bars
    # --------------------------------------------------

    st.subheader("Athletic Percentile Comparison")

    # Compute percentiles within position group
    position_df = comparison_df[
        comparison_df["position"] == p1_data["position"]
    ]

    p1_percentiles = {}
    p2_percentiles = {}

    for metric_name in compare_metrics:
        values = position_df[metric_name]
        
        p1_val = p1_data[metric_name]
        p2_val = p2_data[metric_name]
        
        p1_pct = (values < p1_val).mean() * 100
        p2_pct = (values < p2_val).mean() * 100
        
        p1_percentiles[metric_name] = p1_pct
        p2_percentiles[metric_name] = p2_pct

    # Reverse lower-is-better metrics
    lower_better = ["forty", "threecone", "shuttle"]
    for metric_name in lower_better:
        p1_percentiles[metric_name] = 100 - p1_percentiles[metric_name]
        p2_percentiles[metric_name] = 100 - p2_percentiles[metric_name]

    # Inject animation CSS
    st.markdown("""
    <style>
    .metric-container {
        margin-bottom: 6px;
    }
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .bar-background {
        background-color: #1A1A26;
        border-radius: 6px;
        height: 10px;
        overflow: hidden;
    }
    .bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #6A0DAD, #B026FF);
        width: 0%;
        transition: width 0.6s ease-in-out;
    }
    .bar-value {
        font-size: 12px;
        margin-top: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render animated bars
    for metric_name in compare_metrics:

        label = DISPLAY_LABELS[metric_name]
        p1_val = int(round(p1_percentiles[metric_name]))
        p2_val = int(round(p2_percentiles[metric_name]))

        st.markdown(f"<div class='metric-container'>", unsafe_allow_html=True)

        colA, colB = st.columns(2)

        with colA:
            st.markdown(
                f"<div class='metric-label'>{label}</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"""
            <div class='bar-background'>
                <div class='bar-fill' style='width:{p1_val}%;'></div>
            </div>
            <div class='bar-value'>{ordinal(p1_val)} percentile</div>
            """, unsafe_allow_html=True)

        with colB:
            st.markdown(
                f"<div class='metric-label'>{label}</div>",
                unsafe_allow_html=True
            )
            st.markdown(f"""
            <div class='bar-background'>
                <div class='bar-fill' style='width:{p2_val}%;'></div>
            </div>
            <div class='bar-value'>{ordinal(p2_val)} percentile</div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# End of Player Comparison section

# ----------------------------------
# Floating Watermark Signature
# ----------------------------------
st.markdown("""
<style>
.signature-watermark {
    position: fixed;
    bottom: 12px;
    right: 20px;
    color: #B026FF;
    opacity: 0.50;
    text-shadow:
        0 0 4px #B026FF,
        0 0 8px rgba(176,38,255,0.5);
    font-size: 8px;
    font-family: 'Press Start 2P', cursive;
    letter-spacing: 0.5px;
}
</style>

<div class="signature-watermark">
Developed by Sathvik Medapati
</div>
""", unsafe_allow_html=True)