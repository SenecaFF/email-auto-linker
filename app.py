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
    st.write(link_data)  # Display the fetched data


# Function to auto-link text
def auto_link_text(email_text, link_data):
    for _, row in link_data.iterrows():
        keyword = row["Keyword"]
        url = row["URL"]
        
        # Ensure words are replaced only if they are standalone and not part of another word
        email_text = re.sub(rf'(?<![\w]){re.escape(keyword)}(?![\w])', f'<a href="{url}">{keyword}</a>', email_text)
    
    return email_text

# Streamlit UI
st.title("Email Auto-Linking & HTML Formatter")

sheet_id = "1Q1tQse5i6zXM-Yiud7-cd71U6qB0PwjYfudu0V5H5t8"
range_name = "Sheet1!A:B"  # Adjust if needed

st.write("Paste your email text below:")
email_text = st.text_area("Email Draft", height=300)

if st.button("Generate HTML Email"):
    link_data = get_google_sheet_data(sheet_id, range_name)
    formatted_email = auto_link_text(email_text, link_data)
    
    # Wrap the final email in basic HTML structure
    formatted_html = f"""
    <html>
    <body>
    <p>{formatted_email.replace('\n', '<br>')}</p>
    </body>
    </html>
    """
    
    st.subheader("Formatted Email HTML:")
    st.code(formatted_html, language='html')
    st.download_button("Download HTML File", formatted_html, "email.html", "text/html")

