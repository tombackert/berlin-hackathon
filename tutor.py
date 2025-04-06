import mistral
from conversation_bot import VoiceInterface

exercise = None
conversation_context = []
NUMBEROFTESTS = 5

class Tutor:
    def __init__(self):
        self.voice_interface = VoiceInterface()
        self.current_state = 0
        self.exercise = None
        self.conversation_context = []
        
        # Override system prompt für den Tutor
        self.voice_interface.system_prompt = """
        You are a programming tutor for children. Guide them through coding exercises.
        Explain concepts simply and encourage problem solving.
        """
    
    

    def generate_exercise(self):
        str1 = """def solution(x):
            return x+1"""
        
        prompt = f"""Generate an easy programming exercise for absolute beginners who are currently in elementary school.
        The exercise is supposed to be language independent. The child doesn't know the concepts of programming languages, therefore
        this exercise is made to be about the concepts of programming itself.
        ALWAYS MAKE SURE to generate a possible solution function (which is called "solution()") written in *python3*, as well as EXACTLY {NUMBEROFTESTS} test cases for the exercise.
        The solution and test cases are supposed to work together to evalute the answer. Therefore the Test case should be the EXACT
        input for th exercise and the solution should be the EXACT output that is supposed to be computed.
        The exercise should only include: Datatypes = (Integer), DataStructures=(Variables, List), Arithmetic=(+, -, *, /), Loops=(Single For Loop, While True)
        Answer EXACTLY in this format:
        'ExerciseDescription|PossibleSolution|Testcase&Solution|Testcase&Solution|...'

        Example:
        'Increment an integer.|{str1}|1&2|3&4|8&9|12&13|99&100'
        """
        return mistral.sendMessage([], "", prompt)[-1]['content']

    def extract_exercise(self, exercise_string):
        data = exercise_string.split("|")
        self.exercise = {}
        self.exercise["Description"] = data[0]
        self.exercise["Solution"] = data[1]
        for i in range(2, 7):
            self.exercise[f"Test{i-2}"] = {}
            self.exercise[f"Test{i-2}"]["Case"] = data[i].split("&")[0]
            self.exercise[f"Test{i-2}"]["Solution"] = data[i].split("&")[1]
        self.exercise["Current"] = "def userSolution():\n    pass"
        return self.exercise

    def discussion(self, user_input):
        str2 = """def userSolution(x):
            x = x
            return x"""

        str3 = """def userSolution(x):
            x += 1
            return x"""

        system_prompt = f"""
            You are a nice, helpful tutor who currently teaches an elementary school child the basics of programming.
            Currently you guide the child to find a solution to a coding problem.
            This is the problem: "{exercise['Description']}".
            This is the current code of the child: "{exercise['Current']}".
            The child SHALL NEVER write any code by hand.
            Instead YOU convert the child's spoken intentions into python code. If there is nothing you can turn into code, keep the code unchanged.
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
        response = mistral.sendMessage(conversation_context, user_input, system_prompt)[-1]["content"].split("|")
        
        # Sprachausgabe der Antwort
        self.voice_interface.text_to_speech(response[0])
        
        self.exercise["Current"] = response[1]
        return response[2] == "Yes"

    def evaluate_code(self):
        # Unchanged evaluation logic
        response = ...
        self.voice_interface.text_to_speech(response[0])
        return response[1] == "Yes"

    def handle_interaction(self, user_text):
        if self.current_state == 0:
            if self.discussion(user_text):
                self.current_state = 1
        elif self.current_state == 1:
            self.current_state = int(self.agree_to_eval(user_text))
            if self.current_state == 2:
                if self.evaluate_code():
                    return True
                else:
                    self.current_state = 0
        return False

    def run_exercise(self):
        self.extract_exercise(self.generate_exercise())
        
        def voice_callback(audio_buffer):
            user_text = self.voice_interface.speech_to_text(audio_buffer)
            if user_text:
                return self.handle_interaction(user_text)
            return False

        print("Starting exercise...")
        self.voice_interface.text_to_speech("Let's start the exercise! Press and hold S to speak")
        
        while True:
            key = self.voice_interface.get_user_input()
            if key == 's':
                if not self.voice_interface.is_recording:
                    self.voice_interface.start_recording()
                else:
                    audio_buffer = self.voice_interface.stop_recording()
                    if voice_callback(audio_buffer):
                        break
            elif key == 'q':
                break

        self.voice_interface.text_to_speech("Exercise completed! Great job!")

if __name__ == "__main__":
    ExerciseManager().run_exercise()