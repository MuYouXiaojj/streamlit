import streamlit as sl


container = sl.container()

if 'messages' not in sl.session_state:
    sl.session_state.messages = []

prompt = sl.chat_input('请输入你要问的问题')
if prompt:
    sl.session_state.messages.append(prompt)
    
with container:
    with sl.chat_message('user'):
        for message in sl.session_state.messages:
            sl.write(message)