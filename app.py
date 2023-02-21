import streamlit as st
from multipage import MultiPage
from apps import home, data

app = MultiPage()
st.set_page_config(page_title="York University Community Safety", page_icon=":blossom:", layout="wide")

st.markdown("""
# York University Community Safety

##### Welcome! Visit the official _YorkU_ safety site [here](https://www.yorku.ca/safety/).

""")

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Data", data.app)
st.markdown("""---""")
app.run()
