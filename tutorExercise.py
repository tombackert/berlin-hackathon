import mistral

exercise = None
conversation_context = []
NUMBEROFTESTS = 5

def generateExercise():
    prompt = f"""Generate an easy programming exercise for absolute beginners who are currently in elementary school.
    The exercise is supposed to be language independent.
    Also generate a possible solution written in *python3*, as well as EXACTLY {NUMBEROFTESTS} test cases for the exercise.
    The solution and test cases are supposed to work together to evalute the answer. Therefore the Test case should be the EXACT
    input for th exercise and the solution should be the EXACT output that is supposed to be computed.
    # The exercise should only include: Datatypes = (Integer), DataStructures=(Variables, List), Arithmetic=(+, -, *, /), Loops=(Single For Loop, While True)
    Answer EXACTLY in this format:
    'ExerciseDescription|PossibleSolution|Testcase&Solution|Testcase&Solution|...'

    Example:
    'Increment an integer.|def solution(x):\n    return x+1|1&2|3&4|8&9|12&13|99&100'
    """
    return mistral.sendMessage([], "", prompt)[-1]['content']

def extractExercise(exerciseString : str):
    global exercise
    data = exerciseString.split("|")
    exercise = {}
    exercise["Description"] = data[0]
    exercise["Solution"] = data[1]
    for i in range(2, 7):
        exercise[f"Test{i}"] = {}
        exercise[f"Test{i}"]["Case"] = data[i].split("&")[0]
        exercise[f"Test{i}"]["Solution"] = data[i].split("&")[1]
    exercise["Current"] = "Empty"
    return exercise


def discussion(user_input):
    global exercise
    global conversation_context
    system_prompt = f"""
    You are a nice, helpful tutor who currently teaches an elementary school child the basics of programming.
    Currently you guide the child to find a solution to a coding problem.
    This is the problem: "{exercise['Description']}".
    This is a possible solution to it: "{exercise['Solution']}". DO NOT give the solution, but help the child to find it itself.
    This is the current code of the child: "{exercise['Current']}".
    The child can not write code and shall not learn it. You only teach the concepts. You are supposed to make sense of the child's
    response and translate it into python, maybe cut something out. If there is nothing you can turn into code, keep the code unchanged.
    The solution is to be written as a function called "userSolution".
    Your answer is made up of 3 parts and you have to split the 3 parts with "|":
    "WhatYouTellTheChild|NewStatusOfCode|DoesTheCodeLookGoodAtFirstGlance"

    Examples (Don't emphasize the person in your answer):
    1. Current code = "Empty"
    Child: "I don't understand anything. I don't want to do this anymore"
    Tutor: "I understand your frustration. You are doing well, so don't give up. What is it exactly that you don't understand?|Empty|No"

    2. Current code = "def userSolution(x):\n    x = x\n    return x"
    Child: "I might have an idea, but maybe it is wrong. I think we have to increment the number. Does this make sense?"
    Tutor: "That is a great idea! Do you want to run it?|def userSolution(x):\n    x += 1\n    return x|Yes"
    """

    response = mistral.sendMessage(conversation_context, user_input, system_prompt)[-1]["content"].split("|")
    conversation_context.append({"role": "user", "content": user_input})
    conversation_context.append({"role": "assistant", "content": response[0]})
    print(response[0])
    exercise["Current"] = response[1]
    return response[2] == "Yes"

def agreeToEval(user_input):
    global conversation_context
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

    response = mistral.sendMessage(conversation_context, user_input, system_prompt)[-1]["content"]
    conversation_context.append({"role": "user", "content": user_input})
    return response
    
def evaluateCode():
    global exercise
    global conversation_context

    exec(exercise["Solution"])
    exec(exercise["Current"])
    evaluation = ""
    passed = True
    for i in range(NUMBEROFTESTS):
        if not eval(f"userSolution({exercise[f'Test{i}']}) == Solution({exercise[f'Test{i}']})"):
            evaluation += f"The code failed on Test {i+1}/{NUMBEROFTESTS}. The input was {exercise[f'Test{i}']}.\n"
            passed = False
    if passed:
        evaluation = "All tests were passed."

    system_prompt = f"""
    You are a nice, helpful tutor who currently teaches an elementary school child the basics of programming.
    Currently you guide the child to find a solution to a coding problem.
    This is the problem: "{exercise['Description']}".
    This is a possible solution to it: "{exercise['Solution']}". DO NOT give the solution, but help the child to find it itself.
    This is the current code of the child: "{exercise['Current']}".
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
    response = mistral.sendMessage(conversation_context, "<Child waits for response>", system_prompt)[-1]["content"].split("|")
    print(response[0])
    return response[1] == "Yes"

def exerciseRoutine():
    extractExercise(generateExercise())
    currentState = 0
    while True:
        print(f"Exercise: {exercise['Description']}\n\nCurrent Code:\n{exercise['Current']}")
        user_message = input("> ")
        if currentState == 0:
            if discussion(user_message):
                currentState = 1
        elif currentState == 1:
            currentState = int(agreeToEval(user_message))
        elif currentState == 2:
            if evaluateCode():
                break
            else:
                currentState = 0
    print("\n\n\n***EXERCISE FINISHED***")

exerciseRoutine()


