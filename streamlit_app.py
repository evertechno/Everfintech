import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from fpdf import FPDF
import google.generativeai as genai

# Configure Google Generative AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App UI
st.set_page_config(page_title="Dynamic Factsheet Generator with AI", layout="wide")

# Title
st.title("Dynamic Factsheet Generator with AI Explanation")

# CSV Upload
uploaded_file = st.file_uploader("Upload your CSV file (with all required data)", type=["csv"])
if uploaded_file:
    # Read and Display Data
    data = pd.read_csv(uploaded_file)
    st.subheader("Uploaded Data")
    st.dataframe(data)

    # Factsheet Sections
    st.subheader("Factsheet Preview")

    # 1. Investment Growth Chart
    st.write("Investment Growth Chart")
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in data.filter(like="Investment Growth"):
        ax.plot(data['Time'], data[col], label=col)
    ax.set_title("Investment Growth")
    ax.set_xlabel("Time")
    ax.set_ylabel("Growth Value")
    ax.legend()
    st.pyplot(fig)

    # 2. Performance Table
    st.write("Performance Table")
    performance_columns = ['Return', 'Std Dev', 'Information Ratio']  # Update based on your CSV
    performance_data = data[performance_columns]
    st.table(performance_data)

    # 3. Portfolio Breakdown (Pie Charts)
    st.write("Portfolio Breakdown")
    st.write("Equity Regional Exposure")
    regions = data['Regions'] if 'Regions' in data.columns else ['North America', 'Asia', 'Europe']
    region_values = data['Regional Exposure'] if 'Regional Exposure' in data.columns else [40, 35, 25]
    regional_pie = go.Figure(data=[go.Pie(labels=regions, values=region_values)])
    st.plotly_chart(regional_pie)

    st.write("Equity Sectors")
    sectors = data['Sectors'] if 'Sectors' in data.columns else ['Energy', 'Technology', 'Healthcare']
    sector_values = data['Sector Exposure'] if 'Sector Exposure' in data.columns else [30, 50, 20]
    sector_pie = go.Figure(data=[go.Pie(labels=sectors, values=sector_values)])
    st.plotly_chart(sector_pie)

    # 4. Bar Chart for Yearly Performance
    st.write("Yearly Performance Chart")
    bar_data = pd.DataFrame({
        'Year': data['Year'] if 'Year' in data.columns else ['2013', '2014', '2015', '2016', '2017'],
        'Performance': data['Yearly Performance'] if 'Yearly Performance' in data.columns else [5, 10, 15, 7, 20]
    })
    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(bar_data['Year'], bar_data['Performance'], color='skyblue')
    ax_bar.set_title("Yearly Performance")
    ax_bar.set_xlabel("Year")
    ax_bar.set_ylabel("Performance")
    st.pyplot(fig_bar)

    # 5. Disclosures
    st.write("Disclosures")
    disclosure_text = "\n".join(data['Disclosures'].dropna() if 'Disclosures' in data.columns else ["No disclosures found."])
    st.text(disclosure_text)

    # Generate PDF
    if st.button("Generate PDF Factsheet"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="Investment Factsheet", ln=True, align="C")

        # Add Line Chart Image
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt="Investment Growth Chart", ln=True, align="L")
        fig.savefig("investment_growth.png")
        pdf.image("investment_growth.png", x=10, y=30, w=190)

        # Add Performance Table
        pdf.set_y(120)
        pdf.cell(200, 10, txt="Performance Table", ln=True, align="L")
        for index, row in performance_data.iterrows():
            pdf.cell(200, 10, txt=str(row.values), ln=True, align="L")

        # Add Pie Charts and Bar Chart
        pdf.add_page()
        pdf.cell(200, 10, txt="Portfolio Breakdown", ln=True, align="C")
        regional_pie.write_image("regional_pie.png")
        pdf.image("regional_pie.png", x=10, y=30, w=90)
        sector_pie.write_image("sector_pie.png")
        pdf.image("sector_pie.png", x=110, y=30, w=90)

        pdf.set_y(120)
        pdf.cell(200, 10, txt="Yearly Performance", ln=True, align="C")
        fig_bar.savefig("performance_bar.png")
        pdf.image("performance_bar.png", x=10, y=140, w=190)

        # Add Disclosures
        pdf.add_page()
        pdf.cell(200, 10, txt="Disclosures", ln=True, align="C")
        pdf.multi_cell(0, 10, disclosure_text)

        # Save and Provide PDF
        pdf_output = "factsheet.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            st.download_button("Download Factsheet PDF", f, file_name=pdf_output)

    # Explain Factsheet with AI
    if st.button("Explain Me This Factsheet"):
        # Generate explanation prompt dynamically
        explanation_prompt = f"""
        Explain this factsheet in detail. 
        Key points to cover:
        - The trends in investment growth.
        - Performance metrics like return and standard deviation.
        - Portfolio breakdown (regional and sector exposure).
        - Yearly performance trends.
        - Disclosures and their significance.
        """
        try:
            # Load and configure the model
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Generate response from the model
            response = model.generate_content(explanation_prompt)

            # Display AI Explanation
            st.subheader("AI Explanation")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating explanation: {e}")
