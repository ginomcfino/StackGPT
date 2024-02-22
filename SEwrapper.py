'''
Python Webapp for asking coding questions using ChatGPT,
and sends answers to Stack Overflow if answer doesn't exist,
using the StackExchange REST API.
'''


import dash
from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import openai
import os


# Global variable
try:
    API_KEY = os.environ['OPENAI_API_KEY']
    # API_KEY = os.environ['Does not exist']
except:
    API_KEY = None
# print(f'APIKEY: {API_KEY}')

openai.api_key = API_KEY

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# suppress_callback_exceptions=True

app.layout = html.Div(
    [
        html.Div(
            style={
                "display": "flex",
                "flex-direction": "column",
                "justify-content": "center",
                "align-items": "center",
            },
            children=[
                html.H1("StackGPT Tool"),
                html.P(
                    "Ask a question and get an answer from ChatGPT. If answer still needed, ask Stack Overflow. (MVP version)"
                ),
            ],
        ),
        html.Div(
            style={
                'text-align': 'center',
            },
            children = [
                html.H3("Ask a question: "),
            ]
        ),
        html.Div(
            style={
                "display": "flex",
                "flex-direction": "row",
                "justify-content": "center",
                "align-items": "center",
            },
            children=[
                # html.H4("Ask a question: "),
                dcc.Dropdown(
                    id='my-dropdown',
                    options=[
                        {'label': 'Option 1', 'value': 'OPT1'},
                        {'label': 'Option 2', 'value': 'OPT2'},
                        {'label': 'Option 3', 'value': 'OPT3'}
                    ],
                    style={'max-width': '120px', 'min-width': '100px'}
                ),
                dcc.Input(
                    id="input-box",
                    type="text",
                    placeholder="Type your question here...",
                    style={"width": "60%", "overflow": "auto"},
                ),
                html.Button("Send", id="button", n_clicks=0),
            ],
        ),
        html.Div(
            style={
                "display": "flex",
                "flex-direction": "column",
                "justify-content": "center",
                "align-items": "center",
            },
            children=[
                dcc.Loading(
                    id="loading-1",
                    type="default",  # You can change this to "circle", "cube", etc.
                    children=[
                        dcc.Markdown(id="chat-output", loading_state={"is_loading": True}),
                    ],
                ),
                
            ],
        ),
    ]
)

@app.callback(
    Output('chat-output', 'children'),
    Input('button', 'n_clicks'),
    State('input-box', 'value')
)
def update_output(n_clicks, value):
    if n_clicks is not None and n_clicks > 0:
        if value and len(value) > 0:
            response = chat_with_gpt3_5_turbo(value)
            print(response)
            return response
        else:
            return 'Please enter a question.'
    else:
        return 'response will be here'

def chat_with_gpt3_5_turbo(user_input):
    """
    Sends a message to the GPT-3.5 Turbo model and returns the model's response.
    """
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": user_input,
            },
        ],
    )
    return completion.choices[0].message.content

if __name__ == '__main__':
    app.run_server(debug=True)
