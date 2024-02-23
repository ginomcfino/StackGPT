'''
Python Webapp for asking coding questions using ChatGPT,
and sends answers to Stack Overflow if answer doesn't exist,
using the StackExchange REST API.
'''


import dash
from dash import Input, Output, State, dcc, html
import dash_bootstrap_components as dbc
import dash_daq as daq
import openai
import os


# Global variable
# try:
#     API_KEY = os.environ['OPENAI_API_KEY']
#     # API_KEY = os.environ['Does not exist']
# except:
#     API_KEY = None
# # print(f'APIKEY: {API_KEY}')

# openai.api_key = API_KEY

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

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
                "text-align": "center",
            },
            children=[
                html.Button(
                    "Await Connection",
                    id="refresh-button",
                    n_clicks=0,
                    style={
                        "color": "orange",
                    },
                ),
                html.Div(id="refresh-button-note"),
                html.Div(
                    style={
                        "display": "flex",
                        "flex-direction": "row",
                        "justify-content": "center",
                        "align-items": "center",
                    },
                    children=[
                        html.H3("Ask a question:"),
                    ],
                ),
            ],
        ),
        html.Div(
            style={
                "display": "flex",
                "flex-direction": "row",
                "justify-content": "center",
                "align-items": "center",
            },
            children=[
                # dcc.Dropdown(
                #     id="gpt-dropdown",
                #     options=[
                #         {"label": "Default (GPT-3.5-Turbo)", "value": "GPT-3.5-Turbo"},
                #     ],
                #     style={"max-width": "400px", "min-width": "200px"},
                # ),
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
                        dcc.Markdown(
                            id="chat-output", loading_state={"is_loading": True}
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            style = {'text-align': 'center'},
            id = 'stack-overflow-div',
        )
    ]
)

@app.callback(
    Output('chat-output', 'children'),
    Output('stack-overflow-div', 'children'),
    Input('button', 'n_clicks'),
    State('input-box', 'value')
)
def update_output(n_clicks, value):
    if n_clicks is not None and n_clicks > 0:
        if value and len(value) > 0:
            response = chat_with_gpt(value), build_stack_overflow_div()
            return response
        else:
            return 'Please enter a question.', None
    else:
        return 'response will be here', None

def build_stack_overflow_div():
    return html.Div(
        [
            html.H4('Still need help to your question?'),
            html.P('Please make sure you consult other sources also before posting to Stack Overflow.'),
            html.Button('Yes', id='good-button', n_clicks=0),
            html.Button('No', id='bad-button', n_clicks=0),
            html.Div(id='stack-overflow-question-div')
        ]
    )

@app.callback(
    Output('stack-overflow-question-div', 'children'),
    Input('good-button', 'n_clicks'),
)
def stack_overflow_question(need_help):
    if need_help is not None and need_help > 0:
        return html.Div(
            [
                html.H4("Enter your question to Stack Overflow:"),
                dcc.Input(
                    id="stack-overflow-input",
                    type="text",
                    placeholder="Type your question here...",
                ),
                html.Button("Send", id="stack-overflow-button", n_clicks=0),
                html.Div(id="stack-overflow-output"),
            ]
        )


@app.callback(
    Output("refresh-button", "style"),
    Output("refresh-button", "children"),
    Output("refresh-button-note", "children"),
    Input("refresh-button", "n_clicks"),
    State("input-box", "value"),
)
def refresh_connection(n_clicks, gpt_key):
    if n_clicks is not None:
        if openai.api_key is not None:
            return {"color": "green"}, "Connected to GPT", None
        else:
            if gpt_key and len(gpt_key) > 0:
                openai.api_key = gpt_key
                # test connection:
                try:
                    models = openai.models.list()
                    # models is not none, gpt connection established
                    return {"color": "green"}, "Connected to GPT", None
                except:
                    return {"color": "red"}, "Not connected to GPT", "Invalid API key, please enter a valid API key in question box."
            else:
                try:
                    openai.api_key = os.environ['OPENAI_API_KEY']
                    options = openai.models.list() # test connection
                    return {"color": "green"}, "Connected to GPT", None
                except:
                    return {"color": "red"}, "Not connected to GPT", "Please enter API key in question box"
            # try:
            #     openai.api_key = os.environ['OPENAI_API_KEY'] #TODO: make this user input box
            #     # options = get_avail_models()
            #     return {"color": "green"}, "Connected to GPT", None
            # except:
            #     return {"color": "red"}, "Not connected to GPT", "Please enter API key in question box"
    else:
        return {"color": "orange"}, "Await connction to GPT", "Please enter API key in question box"

# def get_avail_models():
#     """
#     Returns a list of available models from OpenAI.
#     """
#     models = openai.models.list()
#     options = []
#     for m in models:
#         option = {"label": m.id, "value": m.id}
#         options.append(option)
#     return options

def chat_with_gpt(user_input, model_name="gpt-3.5-turbo"):
    """
    Sends a message to the GPT model and returns the model's response.
    """
    completion = openai.chat.completions.create(
        model=model_name,
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
