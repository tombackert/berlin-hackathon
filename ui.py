import streamlit as st

def displayQuestion(q : str):
    if q != None:
        st.markdown(f"## {q}")
        st.divider()

def displayLastResponse(r : str):
    if r != None:
        st.markdown(f"### {r}")
        st.divider()

def displayCode(c : str):
    st.markdown(f"""```python
                {c}""")
    st.divider()

def displayUI(q : str, r : str, c : str):
    st.empty()
    displayQuestion(q)
    displayLastResponse(r)
    displayCode(c)