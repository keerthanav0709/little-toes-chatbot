import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import cohere
import os
from dotenv import load_dotenv
import webbrowser
from threading import Timer

# Load environment variables
load_dotenv()

# Securely get API key
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("Cohere API key not found in .env file")

# Initialize Cohere client
co = cohere.Client(cohere_api_key)

# Function to get Cohere chatbot response
# Function to get baby-style chatbot response
def get_cohere_response(user_input, chat_history):
    # Define baby-safe keywords
    baby_keywords = ["baby", "diaper", "milk", "toy", "sleep", "giggle", "cry", "cute", "nursery", "mom", "dad", "feeding", "baby food", "play", "infant", "crib", "stroller"]

    # Check if input is baby-related
    if not any(word in user_input.lower() for word in baby_keywords):
        return "🚫 Oopsie! I can only talk about baby things like toys, diapers, food, sleep, giggles, and cuddles! 👶💖"

    # Baby-friendly prompt
    prompt =""

    for chat in chat_history:
        prompt += f"User: {chat['user']}\nBabyBot: {chat['bot']}\n"
    prompt += f"User: {user_input}\nBabyBot:"

    response = co.generate(
        model='command-xlarge',
        prompt=prompt,
        max_tokens=100,
        temperature=0.8
    )
    return response.generations[0].text.strip()

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Cohere Chatbot"

# App layout
app.layout = html.Div(style={
    'background': 'linear-gradient(to right, #ffe4e1, #fff0f5)',
    'fontFamily': '"Comic Sans MS", cursive, sans-serif',
    'padding': '20px',
    'minHeight': '100vh',
    'overflow': 'auto'
}, children=[
    html.H1("Hey Mom!", style={
        'textAlign': 'center',
        'color': '#ff69b4',
        'fontSize': '36px',
        'marginBottom': '10px',
        'textShadow': '1px 1px 2px white'
    }),

    html.P("Ask me Anything about your Little Munchkin🧸", style={
        'textAlign': 'center',
        'fontSize': '20px',
        'color': '#d63384',
        'marginBottom': '30px'
    }),

    html.Div([
        dcc.Textarea(
            id='chat-history',
            value='👶 Welcome to BabyBot! Let’s giggle and babble together!',
            style={
                'width': '100%',
                'height': '300px',
                'backgroundColor': '#fff0f5',
                'color': '#333',
                'border': '2px solid #ffb6c1',
                'borderRadius': '10px',
                'padding': '10px',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
                'fontSize': '16px'
            },
            readOnly=True
        ),

        html.Div([
            dcc.Input(
                id='user-input',
                type='text',
                placeholder='Type here... 🍼',
                style={
                    'width': '75%',
                    'padding': '10px',
                    'backgroundColor': '#fff0f5',
                    'color': '#333',
                    'border': '2px solid #ffb6c1',
                    'borderRadius': '8px',
                    'marginRight': '10px',
                    'fontSize': '16px'
                }
            ),

            html.Button('Ask 👶', id='send-btn', n_clicks=0, style={
                'backgroundColor': '#ff69b4',
                'color': 'white',
                'border': 'none',
                'padding': '10px 15px',
                'borderRadius': '8px',
                'fontSize': '16px',
                'cursor': 'pointer'
            }),

            html.Button('Clear Chat 🧼', id='clear-btn', n_clicks=0, style={
                'backgroundColor': '#dc143c',
                'color': 'white',
                'border': 'none',
                'padding': '10px 15px',
                'borderRadius': '8px',
                'marginLeft': '10px',
                'fontSize': '16px',
                'cursor': 'pointer'
            })
        ], style={'marginTop': '20px', 'textAlign': 'center'})
    ]),

    dcc.Store(id='chat-store', data=[])
])


# Callback to handle chat
@app.callback(
    [Output('chat-history', 'value'), Output('chat-store', 'data'), Output('user-input', 'value')],
    [Input('send-btn', 'n_clicks'), Input('clear-btn', 'n_clicks')],
    [State('user-input', 'value'), State('chat-store', 'data')]
)
def update_chat(n_clicks_send, n_clicks_clear, user_input, chat_history):
    if n_clicks_clear > 0:
        return 'Welcome to the chatbot! Ask me anything.', [], ''

    if n_clicks_send > 0 and user_input:
        bot_response = get_cohere_response(user_input, chat_history)
        chat_history.append({"user": user_input, "bot": bot_response})
        chat_display = "\n\n".join([f"User: {chat['user']}\nBot: {chat['bot']}" for chat in chat_history])
        return chat_display, chat_history, ''

    return dash.no_update, dash.no_update, dash.no_update

# Function to open browser
def open_browser(port):
    webbrowser.open_new(f'http://127.0.0.1:{port}/')

# Run server
if __name__ == '__main__':
    port = 8051
    Timer(1, open_browser, [port]).start()
    app.run_server(debug=False, use_reloader=False, port=port)
