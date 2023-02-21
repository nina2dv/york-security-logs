import streamlit as st


def get_st_button_a_tag(url_link, button_name):
    """
    generate html a tag
    :param url_link:
    :param button_name:
    :return:
    """
    return f'''
    <a href={url_link}><button style="
    fontWeight: 400;
    padding: 0.25rem 0.75rem;
    borderRadius: 0.25rem;
    margin: 0px;
    lineHeight: 1.6;
    width: auto;
    userSelect: none;
    backgroundColor: #FFFFFF;
    border: 1px solid rgba(49, 51, 63, 0.2);">{button_name}</button></a>
    '''


def app():
    st.title('Home')

    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.markdown(get_st_button_a_tag('https://www.yorku.ca/safety/tips/', 'Safety Tips'), unsafe_allow_html=True)
    with middle_column:
        st.markdown(get_st_button_a_tag('https://www.yorku.ca/safety/gosafe/', 'GoSafe'), unsafe_allow_html=True)
    with right_column:
        st.markdown(get_st_button_a_tag('https://www.yorku.ca/safety/how-to-report/', 'Report Here'),
                    unsafe_allow_html=True)
    st.markdown("""
    #### Life-Threatening Situations: 911 and 416-736-5333 | extension 33333 | TTY 416-736-5470
    #### Non-Urgent Situations: 416-650-8000 | extension 58000 | TTY 416-736-5470
    #### Sexual Violence: 416-736-5211
    #### Lost & Found: 416 736 5534 | extension 55534
    """)

