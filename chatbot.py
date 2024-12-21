import speech_recognition as sr
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

# Initialize recognizer and lemmatizer
recognizer = sr.Recognizer()
lemmatizer = WordNetLemmatizer()

# Load intents, words, classes, and trained model
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot.h5')

# Function to clean and lemmatize the sentence
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# Function to convert sentence into a bag of words
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

# Function to predict the class of the input
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

# Function to get a random response for the predicted intent
def get_responses(intent, intents_json):
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == intent:
            return random.choice(i['responses'])
    return "I didn't understand that."

# Function for speech recognition
def recognize_speech():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please speak.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Waiting for your voice...")
        audio_data = recognizer.listen(source)
        print("Recognition in progress...")
        try:
            text = recognizer.recognize_google(audio_data, language='en')
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Service error; {e}")
            return None

# Main function to run the chatbot
if __name__ == "__main__":
    while True:
        print("Choose an option:")
        print("1. Type your message")
        print("2. Speak your message")
        print("Type 'exit' to quit.")
        choice = input("Your choice: ")
        
        if choice == "1":
            user_input = input("You: ")
        elif choice == "2":
            user_input = recognize_speech()
            if user_input is None:
                continue  # Skip iteration if no valid input from speech
        elif choice.lower() == "exit":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1 or 2.")
            continue

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Chatbot: Goodbye!")
            break
        
        predictions = predict_class(user_input)
        if predictions:
            intent = predictions[0]['intent']
            res = get_responses(intent, intents)
            print(f"Chatbot: {res}")
        else:
            print("Chatbot: I'm not sure how to respond to that.")
