import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import plotly.graph_objects as go
import google.generativeai as genai

# Configure Google Generative AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Streamlit App Configuration
st.set_page_config(page_title="2-Page Factsheet Generator with AI Explanation", layout="wide")
st.title("2-Page Factsheet Generator with AI Explanation")

# CSV Upload
uploaded_file = st.file_uploader("Upload your CSV file (with all required data)", type=["csv"])

if uploaded_file:
    # Read CSV Data
    data = pd.read_csv(uploaded_file)
    st.subheader("Uploaded Data")
    st.dataframe(data)

    # Generate Factsheet
    if st.button("Generate Factsheet"):
        # Set up PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        # **Page 1: Performance & Portfolio Data**
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="Investment Factsheet", ln=True, align="C")

        # Section 1: Investment Growth Chart
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Investment Growth Chart", ln=True, align="L")
        fig, ax = plt.subplots(figsize=(10, 5))
        for col in data.filter(like="Investment Growth"):
            ax.plot(data['Time'], data[col], label=col)
        ax.set_title("Investment Growth")
        ax.set_xlabel("Time")
        ax.set_ylabel("Growth Value")
        ax.legend()
        fig.savefig("investment_growth.png")
        pdf.image("investment_growth.png", x=10, y=30, w=190)

        # Section 2: Performance Data
        pdf.set_y(120)
        pdf.cell(200, 10, txt="Performance Data", ln=True, align="L")
        performance_columns = ['Return', 'Std Dev', 'Information Ratio']  # Update based on your CSV
        performance_data = data[performance_columns]
        for index, row in performance_data.iterrows():
            pdf.cell(200, 10, txt=str(row.values), ln=True, align="L")

        # Section 3: Portfolio Breakdown
        pdf.add_page()
        pdf.cell(200, 10, txt="Portfolio Breakdown", ln=True, align="L")

        # Regional Exposure Chart
        regions = data['Regions'] if 'Regions' in data.columns else ['North America', 'Asia', 'Europe']
        region_values = data['Regional Exposure'] if 'Regional Exposure' in data.columns else [40, 35, 25]
        regional_pie = go.Figure(data=[go.Pie(labels=regions, values=region_values)])
        regional_pie.write_image("regional_pie.png")
        pdf.image("regional_pie.png", x=10, y=50, w=90)

        # Equity Sectors Chart
        sectors = data['Sectors'] if 'Sectors' in data.columns else ['Energy', 'Technology', 'Healthcare']
        sector_values = data['Sector Exposure'] if 'Sector Exposure' in data.columns else [30, 50, 20]
        sector_pie = go.Figure(data=[go.Pie(labels=sectors, values=sector_values)])
        sector_pie.write_image("sector_pie.png")
        pdf.image("sector_pie.png", x=110, y=50, w=90)

        # Yearly Performance Chart
        pdf.set_y(150)
        bar_data = pd.DataFrame({
            'Year': data['Year'] if 'Year' in data.columns else ['2013', '2014', '2015', '2016', '2017'],
            'Performance': data['Yearly Performance'] if 'Yearly Performance' in data.columns else [5, 10, 15, 7, 20]
        })
        fig_bar, ax_bar = plt.subplots()
        ax_bar.bar(bar_data['Year'], bar_data['Performance'], color='skyblue')
        ax_bar.set_title("Yearly Performance")
        ax_bar.set_xlabel("Year")
        ax_bar.set_ylabel("Performance")
        fig_bar.savefig("performance_bar.png")
        pdf.image("performance_bar.png", x=10, y=180, w=190)

        # **Page 2: Disclosures**
        pdf.add_page()
        pdf.cell(200, 10, txt="Disclosures", ln=True, align="C")
        disclosure_text = "\n".join(data['Disclosures'].dropna() if 'Disclosures' in data.columns else ["No disclosures found."])
        pdf.multi_cell(0, 10, disclosure_text)

        # Save and Provide PDF
        pdf_output = "factsheet.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            st.download_button("Download Factsheet PDF", f, file_name=pdf_output)

    # AI Explanation
    if st.button("Explain Me This Factsheet"):
        explanation_prompt = f"""
        Provide a detailed explanation of the factsheet. Include:
        - Key trends in investment growth.
        - Performance metrics (e.g., Return, Std Dev, Information Ratio).
        - Regional and sector breakdowns.
        - Yearly performance analysis.
        - Importance of the disclosures section.
        """
        try:
            # Load and configure the model
            model = genai.GenerativeModel("gemini-1.5-flash")

            # Generate explanation from AI
            response = model.generate_content(explanation_prompt)

            # Display AI Explanation
            st.subheader("AI Explanation")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating explanation: {e}")
