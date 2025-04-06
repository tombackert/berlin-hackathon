import streamlit as st
import mistral
from conversation_bot import VoiceInterface
from tutorExercise import extractExercise
from tutorExercise import generateExercise

if "exercise" not in st.session_state:
    st.session_state["exercise"] = extractExercise(generateExercise())

if "conversation_context" not in st.session_state:
    st.session_state["conversation_context"] = []

if "speak" not in st.session_state:
    st.session_state["speak"] = False


NUMBEROFTESTS = 5

if "voice_interface" not in st.session_state:
    st.session_state["voice_interface"] = VoiceInterface()

if "lastResponse" not in st.session_state:
    st.session_state["lastResponse"] = None

str1 = """def solution(x):
    return x+1"""
str2 = """def userSolution(x):
    x = x
    return x"""

str3 = """def userSolution(x):
    x += 1
    return x"""

def displayQuestion(q : str):
    if q != None:
        st.markdown(f"#### {q}")
        st.divider()

def displayLastResponse(r : str):
    if r != None:
        st.markdown(f"##### {r}")
        st.divider()

def displayCode(c : str):
    st.markdown(f"""```python
                {c}""")
    st.divider()

def displayUI(q:str, r:str, c:str):
    displayQuestion(q)
    displayLastResponse(r)
    displayCode(c)

def discussion(user_input):
    print("Now Discussing")
    system_prompt = f"""
    You are a nice, helpful tutor who currently teaches an elementary school child the basics concepts of programming.

    Currently you guide the child to find a solution to a coding problem.

    The child is giving an exercise for absolute beginners who are currently in elementary school.
    The exercise is about a simple task that can be solved with a few lines of code.
    Always explain the concepts in a way that a child can understand.
    The exercise is supposed to be language independent. The child doesn't know the concepts of programming languages yet, therefore this exercise is supposed to be about the concepts of programming itself.
    The exercise is supposed to be fun and relatable to the child, like counting apples, animals or adding numbers.

    Give the child a hint to help him find the solution. The hint should be easy to understand and should not require any prior knowledge of programming.

    This is the problem: "{st.session_state["exercise"]['Description']}".
    This is the current code of the child: "{st.session_state["exercise"]['Current']}".

    The child SHALL NEVER write any code by hand.
    Instead YOU convert the child's spoken intentions into python code. If there is nothing you can turn into code, keep the code unchanged.

    Don't give the child the solution, but help the child to find it itself.
    Don't just write out the solution, but rather try to only translate the child's spoken intentions into code.
    Keep the whole solution for a later stages.

    The solution is to be written as a function called "userSolution".
    Your answer is made up of 3 parts and you have to split the 3 parts with "|":
    "WhatYouTellTheChild|NewStatusOfCode|DoesTheCodeLookGoodAtFirstGlance"

    Examples (Don't emphasize the person in your answer):

    1. Current code = "Empty"
    Child: "I don't understand anything. I don't want to do this anymore"
    Tutor: "I understand your frustration. You are doing well, so don't give up. What is it exactly that you don't understand?|Empty|No"

    2. Current code = "{str2}"
    Child: "I might have an idea, but maybe it is wrong. I think we have to increment the number. Does this make sense?"
    Tutor: "That is a great idea! Do you want to run it?|{str3}|Yes"
    """

    response = mistral.sendMessage(st.session_state["conversation_context"], user_input, system_prompt)[-1]["content"].split("|")
    st.session_state["conversation_context"].append({"role": "user", "content": user_input})
    st.session_state["conversation_context"].append({"role": "assistant", "content": response[0]})
    
    st.session_state["lastResponse"] = response[0]
    
    st.session_state["exercise"]["Current"] = response[1]

def agreeToEval(user_input):
    system_prompt = """
    The following message is an answer to a Yes/No question.
    Your answer is supposed to only contain a single character. A numerical character between 0 and 2
    If you interpret the answer as "Yes", you shall ONLY and EXACTLY say "2"
    If you interpret the answer as "No", you shall ONLY and EXACTLY say "0"
    If you can't interpret the answer as either, you shall ONLY and EXACTLY say "1"

    Examples (Don't emphasize the person in your answer):
    1. User: "I would agree"
    Assistent: "2"
    2. User: "Are trees big?"
    Agent: "1"
    3. User: "NEVER!"
    Agent: "0"
    """

    response = mistral.sendMessage(st.session_state["conversation_context"], user_input, system_prompt)[-1]["content"]
    st.session_state["conversation_context"].append({"role": "user", "content": user_input})
    return response

def evaluateCode():
    print("Evaluating")
    exec(st.session_state["exercise"]["Solution"])
    exec(st.session_state["exercise"]["Current"])
    evaluation = ""
    passed = True
    for i in range(NUMBEROFTESTS):
        if not eval(f"userSolution({st.session_state['exercise'][f'Test{i}']['Case']}) == solution({st.session_state['exercise'][f'Test{i}']['Case']})"):
            evaluation += f"The code failed on Test {i+1}/{NUMBEROFTESTS}. The input was {st.session_state['exercise'][f'Test{i}']}.\n"
            passed = False
    if passed:
        evaluation = "All tests were passed."

    system_prompt = f"""
    You are a nice, helpful tutor who currently teaches an elementary school child the basics of programming.
    Currently you guide the child to find a solution to a coding problem.
    This is the problem: "{st.session_state["exercise"]['Description']}".
    This is a possible solution to it: "{st.session_state["exercise"]['Solution']}". DO NOT give the solution, but help the child to find it itself.
    This is the current code of the child: "{st.session_state["exercise"]['Current']}".
    The code was just evaluated and this is the result:
    "{evaluation}"

    If it was successful, congratulate the child and add "(Applause)" to your message.
    If it wasn't successful, encourage the child to continue and offer help.

    Format your message like this:
    "MessageToChild|Successful?"

    Examples:
    1. (All tests passed)
    "You did an outstanding job, you can be proud of yourself.|Yes"

    2. (Failed on Test 3/5)
    "Unfortunately the code isn't correct. Don't worry, we will fix it together...|No"
    """
    response = mistral.sendMessage(st.session_state["conversation_context"], "<Child waits for response>", system_prompt)[-1]["content"].split("|")
    
    st.session_state["lastResponse"] = response[0]
    
    return passed

def process_user_interaction():
    """Get user input via voice recording.
    
    Returns:
        The transcribed text from the voice recording.
    """
    print("Press 's' to start recording, then 's' again to stop...")
    
    # Start recording when user presses 's'
    while True:
        key = st.session_state["voice_interface"].get_user_input()
        if key == 's':
            st.session_state["voice_interface"].start_recording()
            print("Recording started... Press 's' to stop")
            break
        elif key == 'q':
            return "quit"
    
    # Stop recording when user presses 's' again
    while True:
        key = st.session_state["voice_interface"].get_user_input()
        if key == 's':
            audio_buffer = st.session_state["voice_interface"].stop_recording()
            print("\nProcessing...")
            transcribed_text = st.session_state["voice_interface"].speech_to_text(audio_buffer)
            print(f"Transcribed: {transcribed_text}")
            return transcribed_text
        elif key == 'q':
            audio_buffer = st.session_state["voice_interface"].stop_recording()
            return "quit"


if "currentState" not in st.session_state:
    st.session_state["currentState"] = 0

displayQuestion(st.session_state["exercise"]["Description"])
displayLastResponse(st.session_state["lastResponse"])
displayCode(st.session_state["exercise"]["Current"])

if st.session_state["speak"]:
    st.session_state["voice_interface"].text_to_speech(st.session_state["lastResponse"])
    st.session_state["speak"] = False

if "onlyDoOnce" not in st.session_state:
    st.session_state["onlyDoOnce"] = True
    st.session_state["voice_interface"].text_to_speech("Let's start the exercise!")
    st.session_state["voice_interface"].text_to_speech(st.session_state["exercise"]["Description"])

if "discuss" not in st.session_state:
    st.session_state["discuss"] = True


if st.session_state["discuss"]:

    if "recording" not in st.session_state:
        st.session_state["recording"] = False

    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state["recording"] and st.button("Start Recording"):
            st.session_state["voice_interface"].start_recording()
            st.session_state["recording"] = True
            st.rerun()

    with col2:
        if st.session_state["recording"] and st.button("Stop Recording"):
            audio_buffer = st.session_state["voice_interface"].stop_recording()
            transcribed_text = st.session_state["voice_interface"].speech_to_text(audio_buffer)
            st.session_state["recording"] = False
            
            if transcribed_text and transcribed_text != "quit":
                discussion(transcribed_text)
                st.session_state["speak"] = True
                st.rerun()


if "eval_clicked" not in st.session_state:
    st.session_state["eval_clicked"] = False

if st.button("Eval"):
    print("Clicked Eval")
    st.session_state["eval_clicked"] = True

if st.session_state["eval_clicked"]:
    print("In Eval routine")
    st.session_state["eval_clicked"] = False
    b = evaluateCode()
    st.session_state["speak"] = True
    if b:
        st.success("SUPER")
    else:
        st.session_state["discuss"] = True
        st.rerun()

# Reset
if "reset" not in st.session_state:
    st.session_state["reset"] = False

if st.button("Reset"):
    st.session_state["reset"] = True

if st.session_state["reset"]:
    st.session_state["reset"] = False
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()