import io
import time
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="ML Prediction Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    
    .status-success {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid;
        margin: 1rem 0;
    }
    
    .status-error {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.25rem;
        border: 1px solid;
        margin: 1rem 0;
    }
    
    .upload-section {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        transition: border-color 0.3s ease;
    }
    
    .upload-section:hover {
        border-color: #667eea;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
<div class="main-header">
    <h1>🤖 ML Prediction Dashboard</h1>
    <p>Upload your CSV file to get predictions from our trained XGBoost model</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar for information and settings
with st.sidebar:
    st.header("📊 Model Information")

    # Check backend health.
    try:
        health_response = requests.get("http://backend:8000/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success("✅ Backend is healthy")
            st.info(
                f"Model Status: {'Loaded' if health_data.get('model_loaded') else 'Not Loaded'}"
            )
        else:
            st.error("❌ Backend health check failed")
    except requests.RequestException:
        st.error("❌ Cannot connect to backend")

    st.markdown("---")

    st.subheader("📋 Required Columns")
    expected_cols = [
        "trf",
        "age",
        "gndr",
        "tenure",
        "age_dev",
        "dev_man",
        "device_os_name",
        "dev_num",
        "is_dualsim",
        "simcard_type",
        "region",
    ]

    for i, col in enumerate(expected_cols, 1):
        st.write(f"{i}. `{col}`")

    st.markdown("---")

    st.subheader("⚙️ Settings")
    show_data_preview = st.checkbox("Show data preview", value=True)
    max_preview_rows = st.slider("Max preview rows", 5, 50, 10)
    show_statistics = st.checkbox("Show data statistics", value=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📁 File Upload")

    # Custom upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Upload a CSV file containing the required columns for prediction",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.subheader("📈 Quick Stats")
    if uploaded_file is None:
        st.info("Upload a file to see statistics")

# Process uploaded file
if uploaded_file is not None:
    try:
        # Read the file content once and store it
        file_content = uploaded_file.read()

        # Create a StringIO object for reading the CSV with robust parsing
        try:
            # Try reading with different parameters to handle problematic CSVs
            df = pd.read_csv(
                io.StringIO(file_content.decode("utf-8")),
                dtype=str,  # Read all columns as strings initially
                na_filter=False,  # Don't convert to NaN
                skipinitialspace=True,  # Skip whitespace after delimiter
                encoding_errors="replace",  # Replace problematic characters
            )
        except UnicodeDecodeError:
            # Try different encoding if UTF-8 fails
            try:
                df = pd.read_csv(
                    io.StringIO(file_content.decode("latin-1")),
                    dtype=str,
                    na_filter=False,
                    skipinitialspace=True,
                )
                st.warning("File was read using Latin-1 encoding")
            except Exception as e:
                st.error(f"Error with encoding: {str(e)}")
                st.stop()
        except Exception as csv_error:
            st.error(f"Error parsing CSV: {str(csv_error)}")
            st.error("Please check that your CSV file is properly formatted")
            st.stop()

        # Update quick stats in sidebar
        with col2:
            st.metric("📊 Total Rows", len(df))
            st.metric("📋 Total Columns", len(df.columns))
            st.metric("💾 File Size", f"{len(file_content) / 1024:.1f} KB")

        # Data validation section
        st.subheader("🔍 Data Validation")

        # Check for expected columns
        missing_cols = [col for col in expected_cols if col not in df.columns]
        extra_cols = [col for col in df.columns if col not in expected_cols]

        col_status1, col_status2 = st.columns(2)

        with col_status1:
            if missing_cols:
                st.markdown(
                    f"""
                <div class="status-error">
                    <strong>❌ Missing Columns ({len(missing_cols)}):</strong><br>
                    {', '.join(missing_cols)}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                <div class="status-success">
                    <strong>✅ All required columns present!</strong>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        with col_status2:
            if extra_cols:
                st.info(
                    f"📎 Extra columns found: {', '.join(extra_cols[:3])}{'...' if len(extra_cols) > 3 else ''}"
                )

        # Data preview section.
        if show_data_preview:
            st.subheader("👀 Data Preview")

            preview_tabs = st.tabs(
                ["📋 Data Sample", "📊 Column Info", "🔢 Summary Stats"]
            )

            with preview_tabs[0]:
                st.dataframe(
                    df.head(max_preview_rows), use_container_width=True, hide_index=True
                )

            with preview_tabs[1]:
                col_info = pd.DataFrame(
                    {
                        "Column": df.columns,
                        "Data Type": df.dtypes,
                        "Non-Null Count": df.count(),
                        "Null Count": df.isnull().sum(),
                        "Unique Values": df.nunique(),
                    }
                )
                st.dataframe(col_info, use_container_width=True)

            with preview_tabs[2]:
                if show_statistics:
                    # Convert numeric columns for statistics
                    numeric_cols = []
                    for col in ["age", "tenure", "age_dev", "dev_num"]:
                        if col in df.columns:
                            try:
                                pd.to_numeric(df[col], errors="coerce")
                                numeric_cols.append(col)
                            except ValueError:
                                print("error converting column:", col)

                    if numeric_cols:
                        st.write("Numeric columns statistics:")
                        numeric_df = df[numeric_cols].apply(
                            pd.to_numeric, errors="coerce"
                        )
                        st.dataframe(numeric_df.describe(), use_container_width=True)
                    else:
                        st.info("No numeric columns found for statistical analysis")

        # Prediction section
        st.subheader("🎯 Make Predictions")

        prediction_col1, prediction_col2 = st.columns([1, 1])

        with prediction_col1:
            # Only show prediction button if all required columns are present
            if not missing_cols:
                if st.button(
                    "🚀 Get Predictions", type="primary", use_container_width=True
                ):
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # Update progress
                        progress_bar.progress(25)
                        status_text.text("Preparing data...")
                        time.sleep(0.5)

                        # Create a new file-like object from the content for sending to API
                        files = {
                            "file": ("uploaded_file.csv", file_content, "text/csv")
                        }

                        # Update progress
                        progress_bar.progress(50)
                        status_text.text("Sending to model...")

                        # Send the file to the FastAPI backend for prediction
                        response = requests.post(
                            "http://backend:8000/predict", files=files, timeout=30
                        )

                        # Update progress
                        progress_bar.progress(75)
                        status_text.text("Processing results...")

                        # Check if the request was successful
                        if response.status_code == 200:
                            result = response.json()
                            predictions = result.get("predictions", [])
                            num_predictions = result.get("num_predictions", 0)

                            # Update progress
                            progress_bar.progress(100)
                            status_text.text("Complete!")
                            time.sleep(0.5)

                            # Clear progress indicators
                            progress_bar.empty()
                            status_text.empty()

                            # Display results
                            st.success(
                                f"✅ Successfully generated {num_predictions} predictions!"
                            )

                            # Results tabs
                            result_tabs = st.tabs(
                                [
                                    "📊 Results Overview",
                                    "📈 Visualization",
                                    "💾 Download Results",
                                ]
                            )

                            with result_tabs[0]:
                                # Create results dataframe
                                results_df = df.copy()
                                results_df["Prediction"] = predictions

                                st.dataframe(
                                    results_df,
                                    use_container_width=True,
                                    hide_index=True,
                                )

                                # Prediction statistics
                                pred_series = pd.Series(predictions)
                                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(
                                    4
                                )

                                with col_stat1:
                                    st.metric("Total Predictions", len(predictions))

                                with col_stat2:
                                    if pred_series.dtype in ["int64", "float64"]:
                                        st.metric(
                                            "Mean Prediction",
                                            f"{pred_series.mean():.2f}",
                                        )
                                    else:
                                        unique_preds = pred_series.nunique()
                                        st.metric("Unique Predictions", unique_preds)

                                with col_stat3:
                                    if pred_series.dtype in ["int64", "float64"]:
                                        st.metric(
                                            "Min Prediction", f"{pred_series.min():.2f}"
                                        )
                                    else:
                                        most_common = (
                                            pred_series.mode().iloc[0]
                                            if not pred_series.empty
                                            else "N/A"
                                        )
                                        st.metric("Most Common", str(most_common))

                                with col_stat4:
                                    if pred_series.dtype in ["int64", "float64"]:
                                        st.metric(
                                            "Max Prediction", f"{pred_series.max():.2f}"
                                        )
                                    else:
                                        st.metric("Data Type", str(pred_series.dtype))

                            with result_tabs[1]:
                                # Visualization based on prediction type
                                pred_series = pd.Series(predictions)

                                try:
                                    # Try to convert to numeric for better analysis
                                    pred_numeric = pd.to_numeric(
                                        pred_series, errors="coerce"
                                    )
                                    is_numeric = not pred_numeric.isnull().all()
                                except ValueError:
                                    is_numeric = False
                                    print("Error converting predictions to numeric")

                                if is_numeric:
                                    # Numeric predictions - histogram and box plot
                                    fig, (ax1, ax2) = plt.subplots(
                                        1, 2, figsize=(12, 5)
                                    )

                                    # Histogram
                                    ax1.hist(
                                        pred_numeric.dropna(),
                                        bins=20,
                                        color="#667eea",
                                        alpha=0.7,
                                        edgecolor="black",
                                    )
                                    ax1.set_title("Distribution of Predictions")
                                    ax1.set_xlabel("Prediction Value")
                                    ax1.set_ylabel("Frequency")
                                    ax1.grid(True, alpha=0.3)

                                    # Box plot
                                    ax2.boxplot(
                                        pred_numeric.dropna(),
                                        patch_artist=True,
                                        boxprops=dict(facecolor="#764ba2", alpha=0.7),
                                    )
                                    ax2.set_title("Prediction Statistics")
                                    ax2.set_ylabel("Prediction Value")
                                    ax2.grid(True, alpha=0.3)

                                    plt.tight_layout()
                                    st.pyplot(fig)

                                    # Line plot for sequence
                                    if len(predictions) > 1:
                                        fig2, ax3 = plt.subplots(figsize=(10, 4))
                                        ax3.plot(
                                            range(len(pred_numeric)),
                                            pred_numeric,
                                            color="#667eea",
                                            linewidth=2,
                                            marker="o",
                                            markersize=3,
                                        )
                                        ax3.set_title("Predictions Over Rows")
                                        ax3.set_xlabel("Row Index")
                                        ax3.set_ylabel("Prediction")
                                        ax3.grid(True, alpha=0.3)
                                        plt.tight_layout()
                                        st.pyplot(fig2)

                                else:
                                    # Categorical predictions - bar chart and pie chart
                                    value_counts = pred_series.value_counts()

                                    col_viz1, col_viz2 = st.columns(2)

                                    with col_viz1:
                                        # Bar chart
                                        fig1, ax1 = plt.subplots(figsize=(8, 6))
                                        bars = ax1.bar(
                                            range(len(value_counts)),
                                            value_counts.values,
                                            color="#667eea",
                                            alpha=0.7,
                                        )
                                        ax1.set_title("Prediction Distribution")
                                        ax1.set_xlabel("Prediction Categories")
                                        ax1.set_ylabel("Count")
                                        ax1.set_xticks(range(len(value_counts)))
                                        ax1.set_xticklabels(
                                            value_counts.index, rotation=45, ha="right"
                                        )
                                        ax1.grid(True, alpha=0.3)

                                        # Add value labels on bars
                                        for bar in bars:
                                            height = bar.get_height()
                                            ax1.text(
                                                bar.get_x() + bar.get_width() / 2.0,
                                                height,
                                                f"{int(height)}",
                                                ha="center",
                                                va="bottom",
                                            )

                                        plt.tight_layout()
                                        st.pyplot(fig1)

                                    with col_viz2:
                                        # Pie chart
                                        fig2, ax2 = plt.subplots(figsize=(8, 6))
                                        colors = plt.cm.Set3(range(len(value_counts)))
                                        wedges, texts, autotexts = ax2.pie(
                                            value_counts.values,
                                            labels=value_counts.index,
                                            autopct="%1.1f%%",
                                            colors=colors,
                                            startangle=90,
                                        )
                                        ax2.set_title("Prediction Distribution")
                                        plt.tight_layout()
                                        st.pyplot(fig2)

                                # Display value counts table
                                st.subheader("📊 Prediction Summary")
                                value_counts_df = pd.DataFrame(
                                    {
                                        "Prediction": value_counts.index,
                                        "Count": value_counts.values,
                                        "Percentage": (
                                            value_counts.values / len(predictions) * 100
                                        ).round(2),
                                    }
                                )
                                st.dataframe(
                                    value_counts_df,
                                    use_container_width=True,
                                    hide_index=True,
                                )

                            with result_tabs[2]:
                                # Download section
                                results_df = df.copy()
                                results_df["Prediction"] = predictions
                                results_df["Timestamp"] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )

                                csv_buffer = io.StringIO()
                                results_df.to_csv(csv_buffer, index=False)
                                csv_string = csv_buffer.getvalue()

                                st.download_button(
                                    label="📥 Download Results as CSV",
                                    data=csv_string,
                                    file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                    mime="text/csv",
                                    use_container_width=True,
                                )

                                # JSON download option
                                json_data = {
                                    "metadata": {
                                        "timestamp": datetime.now().isoformat(),
                                        "total_predictions": len(predictions),
                                        "model_version": "xgb_model",
                                        "file_name": uploaded_file.name,
                                    },
                                    "predictions": predictions,
                                    "summary_statistics": {
                                        "unique_values": len(set(predictions)),
                                        "most_common": max(
                                            set(predictions), key=predictions.count
                                        )
                                        if predictions
                                        else None,
                                    },
                                }

                                st.download_button(
                                    label="📥 Download Results as JSON",
                                    data=pd.Series(json_data).to_json(),
                                    file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    mime="application/json",
                                    use_container_width=True,
                                )

                                st.info(
                                    "💡 Results include original data plus predictions and timestamp"
                                )

                        else:
                            progress_bar.empty()
                            status_text.empty()

                            error_msg = response.text
                            try:
                                error_data = response.json()
                                error_msg = error_data.get("detail", error_msg)
                            except ValueError:
                                print("Error parsing response JSON")

                            st.error(f"❌ Prediction failed: {error_msg}")

                            # Show detailed error information
                            with st.expander("🔧 Troubleshooting"):
                                st.write("**Common issues:**")
                                st.write(
                                    "- Check that all required columns are present"
                                )
                                st.write("- Ensure data types are correct")
                                st.write("- Verify there are no missing values")
                                st.write("- Check file encoding (UTF-8 recommended)")

                    except requests.RequestException as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"❌ Connection error: {str(e)}")
                        st.info("💡 Make sure the backend service is running")

                    except Exception as e:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"❌ Unexpected error: {str(e)}")
            else:
                st.warning("⚠️ Cannot make predictions: Missing required columns")
                st.info(
                    "Please upload a CSV file with all required columns listed in the sidebar"
                )

        # Data preview section (moved below prediction for better flow)
        if show_data_preview and not missing_cols:
            st.subheader("📋 Data Preview")

            # Display data with better formatting
            display_df = df.head(max_preview_rows)
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Data quality indicators
            if show_statistics:
                st.subheader("📊 Data Quality Report")

                quality_col1, quality_col2, quality_col3 = st.columns(3)

                with quality_col1:
                    null_count = df.isnull().sum().sum()
                    st.metric("🔍 Null Values", null_count)

                with quality_col2:
                    duplicate_count = df.duplicated().sum()
                    st.metric("📋 Duplicates", duplicate_count)

                with quality_col3:
                    completeness = (1 - null_count / (len(df) * len(df.columns))) * 100
                    st.metric("✅ Completeness", f"{completeness:.1f}%")

                # Column-wise analysis
                if st.checkbox("Show detailed column analysis"):
                    for col in expected_cols:
                        if col in df.columns:
                            col_data = df[col]
                            unique_vals = col_data.nunique()

                            with st.expander(f"📊 {col} Analysis"):
                                col_analysis1, col_analysis2 = st.columns(2)

                                with col_analysis1:
                                    st.write(f"**Unique values:** {unique_vals}")
                                    st.write(
                                        f"**Missing values:** {col_data.isnull().sum()}"
                                    )

                                with col_analysis2:
                                    if unique_vals <= 10:
                                        st.write("**Value distribution:**")
                                        value_counts = col_data.value_counts().head(5)
                                        for val, count in value_counts.items():
                                            st.write(f"- {val}: {count}")
                                    else:
                                        st.write(
                                            f"**Sample values:** {', '.join(map(str, col_data.unique()[:5]))}"
                                        )

    except Exception as e:
        st.error(f"❌ Error reading the CSV file: {str(e)}")

        with st.expander("🔧 File Reading Tips"):
            st.write("**Try these solutions:**")
            st.write("- Ensure your CSV is properly formatted")
            st.write("- Check file encoding (UTF-8 is recommended)")
            st.write("- Verify column headers match expected format")
            st.write("- Remove any special characters from headers")

else:
    # Welcome section when no file is uploaded
    st.subheader("🌟 Welcome to ML Prediction Dashboard")

    welcome_col1, welcome_col2 = st.columns([2, 1])

    with welcome_col1:
        st.write(
            """
        This dashboard allows you to upload CSV files and get predictions from our trained XGBoost model.
        
        **How to use:**
        1. 📁 Upload a CSV file using the file uploader above
        2. 🔍 Review the data validation and preview
        3. 🎯 Click "Get Predictions" to run the model
        4. 📊 Explore results with interactive visualizations
        5. 💾 Download results in CSV or JSON format
        
        **Features:**
        - Real-time data validation
        - Interactive data preview
        - Statistical analysis
        - Multiple visualization options
        - Easy result download
        """
        )

    with welcome_col2:
        st.info(
            """
        **💡 Tips for best results:**
        
        - Ensure CSV has UTF-8 encoding
        - Include all required columns
        - Remove any missing values
        - Use consistent data formats
        """
        )

# Footer
st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🤖 ML Prediction Dashboard | Powered by FastAPI & Streamlit</p>
</div>
""",
    unsafe_allow_html=True,
)
