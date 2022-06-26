# Full Stack API Final Project


## Full Stack Trivia

Udacity is invested in creating bonding experiences for its employees and students. A bunch of team members got the idea to hold trivia on a regular basis and created a webpage to manage the trivia app and play the game, but their API experience is limited and still needs to be built out.

That's where the project comes in. This is the finished trivia app that can be used to hold trivia and see who's the most knowledgeable of the bunch. The application:

1. Displays questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Deletes questions.
3. Adds questions and require that they include question and answer text.
4. Searches for questions based on a text query string.
5. Plays the quiz game, randomizing either all questions or within a specific category.


## About the Stack


### Backend
The backend directory contains a Flask and SQLAlchemy server. Endpoints are defined in `__init__.py` which reference models.py for DB and SQLAlchemy setup. 

>View the [README within ./frontend for more details.](./backend/README.md)

### Frontend

The frontend directory contains a complete React frontend to consume the data from the Flask server.


>View the [README within ./frontend for more details.](./frontend/README.md)
