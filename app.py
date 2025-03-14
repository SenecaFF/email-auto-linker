import streamlit as st
import pandas as pd
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheet Connection Setup
def get_google_sheet_data(sheet_id, range_name):
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return pd.DataFrame(result.get("values", []), columns=["Keyword", "URL"])

# Function to auto-link text while preserving HTML structure
def auto_link_text(email_text, link_data):
    """
    Replaces occurrences of product names with hyperlinks in the given email text.
    Ensures words are replaced even if they are part of a longer phrase.
    """
    # Sort keywords by length (longer phrases first to avoid partial double replacements)
    link_data = link_data.sort_values(by="Keyword", key=lambda x: x.str.len(), ascending=False)

    for _, row in link_data.iterrows():
        keyword = row["Keyword"].strip()
        url = row["URL"].strip()

        # Match the keyword even if it's part of a longer phrase
        pattern = rf'(?<!\w){re.escape(keyword)}(?!\w)'
        replacement = f'<a href="{url}">{keyword}</a>'

        email_text = re.sub(pattern, replacement, email_text, flags=re.IGNORECASE)

    return email_text

# Streamlit UI
st.title("Email Auto-Linking & HTML Formatter")

sheet_id = "1Q1tQse5i6zXM-Yiud7-cd71U6qB0PwjYfudu0V5H5t8"
range_name = "Sheet1!A:B"  # Adjust if needed

st.write("Paste your email text below (Supports Raw HTML Input):")
email_text = st.text_area("Email Draft", height=300)

if st.button("Generate HTML Email"):
    link_data = get_google_sheet_data(sheet_id, range_name)
    formatted_email = auto_link_text(email_text, link_data)

    # ✅ FIX: Preserve existing HTML structure without overriding formatting
    if "<html>" in formatted_email and "<body>" in formatted_email:
        # If the input already has <html> and <body> tags, don't wrap it again
        formatted_html = formatted_email
    else:
        formatted_html = f"""
        <html>
        <body>
        {formatted_email}
        </body>
        </html>
        """

    st.subheader("Formatted Email HTML:")
    st.code(formatted_html, language='html')
    st.download_button("Download HTML File", formatted_html, "email.html", "text/html")
