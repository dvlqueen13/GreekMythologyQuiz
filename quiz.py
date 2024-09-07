import streamlit as st
import openai
import json

# Set your OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Load Greek Mythology image URL
IMAGE_URL = "https://cdn.historycollection.com/wp-content/uploads/2021/06/30the-twelve-major-olympian-gods.-pintrest-1420x640.jpg"  # Replace with a valid URL


class Question:
    def __init__(self, question, options, correct_answer, explanation=None):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation


class GreekMythologyQuiz:
    def __init__(self):
        self.questions = self.load_or_generate_questions()
        self.initialize_session_state()

    def load_or_generate_questions(self):
        if 'questions' not in st.session_state:
            st.session_state.questions = [
                Question("Who is the king of the Greek gods?", ["Zeus", "Poseidon", "Hades", "Apollo"], "Zeus",
                         "Zeus is the ruler of Mount Olympus and the god of the sky and thunder."),
                Question("Which goddess is known for wisdom and warfare?", ["Hera", "Aphrodite", "Athena", "Demeter"],
                         "Athena",
                         "Athena is the goddess of wisdom, courage, and warfare in Greek mythology."),
                Question("Who was the hero of the Trojan War?", ["Achilles", "Odysseus", "Hector", "Agamemnon"],
                         "Achilles",
                         "Achilles was a Greek hero of the Trojan War and the central character in Homer's Iliad.")
            ]
        return st.session_state.questions

    def initialize_session_state(self):
        if 'current_question_index' not in st.session_state:
            st.session_state.current_question_index = 0
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'answers_submitted' not in st.session_state:
            st.session_state.answers_submitted = 0
        if 'show_explanation' not in st.session_state:
            st.session_state.show_explanation = False

    def display_quiz(self):
        st.image(IMAGE_URL, use_column_width=True)  # Display the Greek mythology image
        st.title("Greek Mythology Quiz")
        self.update_progress_bar()

        if st.session_state.answers_submitted >= len(self.questions):
            self.display_results()
        else:
            self.display_navigation()

    def display_navigation(self):
        question = self.questions[st.session_state.current_question_index]
        st.write(f"Question {st.session_state.current_question_index + 1}: {question.question}")
        options = question.options
        answer = st.radio("Choose your answer:", options, key=f"question_{st.session_state.current_question_index}")

        if st.button("Submit Answer") and not st.session_state.show_explanation:
            self.check_answer(answer)
            st.session_state.answers_submitted += 1
            st.session_state.show_explanation = True  # Show explanation after the answer is checked

        if st.session_state.show_explanation:
            if st.button("Next"):
                self.next_question()

    def check_answer(self, user_answer):
        correct_answer = self.questions[st.session_state.current_question_index].correct_answer
        if user_answer == correct_answer:
            st.session_state.score += 1
            st.success("Correct!")
            st.write(self.questions[st.session_state.current_question_index].explanation)
        else:
            st.error("Wrong answer!")

    def next_question(self):
        st.session_state.current_question_index += 1
        st.session_state.show_explanation = False

    def display_results(self):
        st.write(f"Quiz completed! Your score: {st.session_state.score}/{len(self.questions)}")
        if st.session_state.score / len(self.questions) >= 0.7:
            st.success("Well done! You have a solid knowledge of Greek mythology.")
            st.balloons()  # Balloons only appear on successful completion
        else:
            st.error("Better luck next time! Brush up on your Greek mythology and try again.")
        if st.button("Restart Quiz"):
            self.restart_quiz()

    def update_progress_bar(self):
        total_questions = len(self.questions)
        progress = st.session_state.answers_submitted / total_questions
        st.progress(progress)

    def restart_quiz(self):
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.answers_submitted = 0
        st.session_state.show_explanation = False
        st.session_state.pop('questions', None)
        self.__init__()


def generate_and_append_question(user_prompt):
    history = ""
    for q in st.session_state.questions:
        history += f"Question: {q.question} Answer: {q.correct_answer}\n"

    gpt_prompt = '''Generate a JSON response for a trivia question including the question, options, correct answer, and explanation. The format should be as follows:

{
  "Question": "The actual question text goes here?",
  "Options": ["Option1", "Option2", "Option3", "Option4"],
  "CorrectAnswer": "TheCorrectAnswer",
  "Explanation": "A detailed explanation on why the correct answer is correct."
}'''
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=f"{gpt_prompt}\nCreate a question about: {user_prompt} that is different from those: {history}",
            max_tokens=200
        )
        gpt_response = json.loads(response.choices[0].text.strip())
        new_question = Question(
            question=gpt_response["Question"],
            options=gpt_response["Options"],
            correct_answer=gpt_response["CorrectAnswer"],
            explanation=gpt_response["Explanation"]
        )
        st.session_state.questions.append(new_question)
        st.write("New question added!")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


# Main logic
if 'quiz_initialized' not in st.session_state:
    st.session_state.quiz_initialized = False

# Welcome page
if not st.session_state.quiz_initialized:
    st.title("Welcome to the Greek Mythology Quiz!")
    if st.button("Start Quiz"):
        st.session_state.quiz_initialized = True
        st.session_state.quiz = GreekMythologyQuiz()
else:
    # Display the quiz
    st.session_state.quiz.display_quiz()

    # Option to generate new questions
    user_input = st.text_input("Add your preferences (e.g., specific mythological character or event)")

    if st.button('Generate New Question'):
        generate_and_append_question(user_input)
