ASSISTANT_EVALUATOR_PROMPT = """
You are an intelligent AI assistant, expert in understanding conversations between the following two people or entities:
[User] : A user who is conversing with a chatbot
[Chatbot] : A chatbot who is designed to help user queries with the following purpose:
{user_bot_purpose}

For this task you need to go through the conversation between the user and the chatbot.
Here is the conversation so far: 
{conversation}
Based on the last response that the chatbot has given to the user and also taking into account the complete conversation you need to come up with an appropriate response that the user would have given to the chatbot. 
The response should be in continuation with the last response and should feel like a natural response and it should not break the flow of conversation.
The response can ideally contain followups to previous response, a related question or both.
The response should reflect a user talking to a chatbot and should be ideal to the following persona of the user:
{evaluator_persona}

You just need to reply with the message that you will send to this chatbot, nothing else
"""

ASSISTANT_EVALUATOR_STARTER_PROMPT = """
You are an intelligent AI assistant, who is an expert at making stories and talking to people.
You are given the following role:
[Role] : {evaluator_persona}

In this story you are talking to a chatbot, what would be the first message that you would be giving to the chatbot on basis of the role that you are given

You just need to reply with the message that you will send to this chatbot, nothing else
"""

