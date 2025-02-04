
# Import required libraries
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv  # Load environment variables from .env file
import os  # Operating system interface for environment variables
import google.generativeai as genai  # Google's Generative AI library for Gemini
from pathlib import Path  # Path handling functionality
import webbrowser  # Open a URL in a browser programmatically
from threading import Timer  # Schedule a function to run after a delay
import logging  # Logging for debugging and error tracking
import markdown # Convert markdown to HTML
import bleach # Sanitize HTML output

# Configure basic logging for the application
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)

class GeminiAPI:
    """
    A class to manage interactions with Google's Gemini AI API.
    It handles:
    - Initialization of the API
    - Text generation
    - Chat sessions
    - Code analysis
    """
    
    def __init__(self):
        """
        Initialize the GeminiAPI class.
        Sets up the API key and configures the Gemini model.
        Raises ValueError if the API key is not found in environment variables.
        """
        load_dotenv()  # Load environment variables from .env file
        api_key = os.getenv('GOOGLE_API_KEY')  # Fetch the API key from environment variables
        
        # If the API key doesn't exist, raise an error
        if not api_key:
            raise ValueError("KEY not found in environment variables")
        
        # Configure Gemini with the API key
        genai.configure(api_key=api_key)
        
        # Initialize the Gemini Pro model
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate a text response from the Gemini model.
        
        Args:
            prompt (str): Input text prompt for content generation.
        
        Returns:
            str: Generated response text from the model or error message.
        """
        try:
            # Generate content using the model based on the prompt
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # If there is an error generating content, log it and return a user-friendly error message
            logging.error(f"Error generating response: {e}", exc_info=True)
            return "I apologize, but I encountered an error processing your request."
    
    def chat_session(self):
        """
        Initialize a new chat session with Gemini AI.
        
        Returns:
            ChatSession: A new chat session object with an empty history.
        """
        return self.model.start_chat(history=[])
    
    def analyze_code(self, code: str) -> str:
        """
        Analyze code using Gemini's capabilities.
        
        Args:
            code (str): The source code to analyze.
        
        Returns:
            str: Detailed analysis of the code, including quality, improvements, and security considerations.
        """
        # Construct a prompt to send to the model for code analysis
        prompt = f"""Please analyze this code and provide insights about:
        1. Code quality
        2. Potential improvements
        3. Security considerations
        
        Code:
        {code}
        """
        return self.generate_text(prompt)

# Flask route definitions

@app.route('/')
def home():
    """
    Route handler for the home page.
    This renders the main chat interface template.

    Returns:
        rendered HTML template
    """
    return render_template('index.html')  # Renders the 'index.html' template as the homepage

@app.route('/ask', methods=['POST'])
def ask():
    """
    API endpoint to handle chat requests.
    Receives questions from the frontend (as JSON) and returns AI responses.
    
    Returns:
        JSON response containing AI's answer or error message
    """
    try:
        # Extract the 'question' key from the incoming JSON data in the POST request
        question = request.json.get('question', '')
        
        # If no question is provided, return a 400 Bad Request response
        if not question:
            logging.warning("Received empty question")
            return jsonify({'response': 'No question provided'}), 400
        
        # Initialize the Gemini API instance
        gemini = GeminiAPI()
        
        # Generate the AI response based on the question
        response = gemini.generate_text(question)

        # Convert the Markdown response to HTML
        html_response = markdown.markdown(response)

        # Clean response
        # clean_response = bleach.clean(html_response, tags=[], strip=True)
        
        # Return the response as a JSON object
        return jsonify({'response': html_response})
    
    except Exception as e:
        # Log the error with the full stack trace for debugging
        logging.error(f"Error in /ask route: {e}", exc_info=True)
        # Return a 500 Internal Server Error response if an exception occurred

def main():
    """
    Main function to run the application.
    Initializes the Gemini API and starts the Flask server.
    
    Handles:
        - API initialization
        - Server startup
        - Error logging
    """
    try:
        # Test Gemini API initialization to ensure everything is set up correctly
        gemini = GeminiAPI()
        logging.info("Gemini API initialized successfully!")
        
        # Print message to indicate where the server is running
        logging.info("Starting web interface on http://127.0.0.1:5000")
        
        # Use Timer to delay opening the browser by 1 second after Flask starts
        Timer(1, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
        
        # Start the Flask server with the specified host and port (127.0.0.1:5000)
        app.run(host='127.0.0.1', port=5000, debug=True)
    
    except Exception as e:
        # If there is an error during startup, log the error and return
        logging.error(f"Error starting application: {e}", exc_info=True)
        return

# Ensure that the script runs only when it is executed directly (not imported)
if __name__ == "__main__":
    # Call the main function to start the application
    main()

