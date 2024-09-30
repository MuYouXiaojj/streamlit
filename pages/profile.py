import streamlit as sl
from pydantic import BaseModel

# 构建和大模型聊天chain
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import AIMessage,HumanMessage

model = ChatTongyi(model_name='qwen-max', streaming=True)

memory_key = 'history'

prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name=memory_key),
        ('human', '{input}')
    ]
)

class Message(BaseModel):
    content: str
    role: str


if "messages" not in sl.session_state:
    sl.session_state.messages = []
    
def to_messages_holder(messages):
    return [
        AIMessage(content=message['content']) if message['role'] == 'ai' else HumanMessage(content=message['content'])
        for message in messages
    ]
    
chain = {
    'input': lambda x: x['input'],
    'history': lambda x:to_messages_holder(x['messages'])
} | prompt | model | StrOutputParser()


left, right = sl.columns([0.7,0.3])

with left:
    # 聊天信息
    container = sl.container()
    with container:
        for message in sl.session_state.messages:
            with sl.chat_message(message['role']):
                sl.write(message['content'])
                
    prompt = sl.chat_input("您好，请问有什么可以帮助您的吗？")
    if prompt:
        sl.session_state.messages.append(Message(content=prompt, role="human").model_dump())
        with container:
            with sl.chat_message("human"):
                sl.write(prompt)
    
    # 获取大模型返回信息
    with container: 
        with sl.chat_message("ai"):
            response = sl.write_stream(chain.stream({'input': prompt, 'messages':sl.session_state.messages}))
            sl.session_state.messages.append(Message(content=response, role="ai").model_dump())
    
with right:
    # 聊天记录
    sl.json(sl.session_state.messages)