import mistral

exercise = None
conversation_context = []

def generateExercise():
    prompt = """Generate an easy programming exercise for absolute beginners who are currently in elementary school.
    The exercise is supposed to be language independent.
    Also generate a possible solution written in *python3*, as well as EXACTLY 5 test cases for the exercise.
    The solution and test cases are supposed to work together to evalute the answer. Therefore the Test case should be the EXACT
    input for th exercise and the solution should be the EXACT output that is supposed to be computed.
    The exercise should only include: Datatypes = \{Integer\}, DataStructures=\{Variables, List\}, Arithmetic=\{+, -, *, /\}, Loops=\{Single For Loop, While True\}
    Answer EXACTLY in this format:
    'ExerciseDescription|PossibleSolution|Testcase&Solution|Testcase&Solution|...'

    Example:
    'Increment an integer.|def solution(x):\n    return x+1|1&2|3&4|8&9|12&13|99&100'

    """
    return mistral.sendMessage([], "", prompt)[-1]['content']

def extractExercise(exerciseString : str):
    data = exerciseString.split("|")
    exercise = {}
    exercise["Description"] = data[0]
    exercise["Solution"] = data[1]
    for i in range(2, 7):
        exercise[f"Test{i}"] = {}
        exercise[f"Test{i}"]["Case"] = data[i].split("&")[0]
        exercise[f"Test{i}"]["Solution"] = data[i].split("&")[1]
    return exercise

print(generateExercise())



