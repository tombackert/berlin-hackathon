import streamlit as st
import tutorExercise

st.header("Learn Programming")

def displayCode(code):
    st.markdown(f"""```python
                {code}
                """)
    
displayCode("print(\"Hello World\")")