from __future__ import annotations
import os
from openai import OpenAI
import typing as t
import time
from loguru import logger    
import copy

from uptrain import EvalLLM, Evals, ConversationSatisfaction, Settings

import uptrain.framework.eval_assistant.parse_files_utils as file_parser

from uptrain.framework.eval_assistant.assistant_evals_prompts import (
    ASSISTANT_EVALUATOR_PROMPT,
    ASSISTANT_EVALUATOR_STARTER_PROMPT
)

__all__ = ["EvalAssistant"]

class EvalAssistant:
    def __init__(self, settings: Settings = None,
                 openai_api_key: str = None
                 ) -> None:
        if (openai_api_key is None) and (settings is None):
            raise Exception("Please provide OpenAI API Key")
        
        if settings is None:
            self.settings = Settings(openai_api_key=openai_api_key)
        else:
            self.settings = settings
        self.client = OpenAI(
            api_key = self.settings.openai_api_key
        )
        self.eval_llm = EvalLLM(self.settings)
    
    
    def create_file(
        self,
        file_list: t.Union[list]
    ):
        files_id =[]

        for file in file_list:
            try:
                file_location = open(file, "rb")
                file = self.client.files.create(file = file_location, purpose='assistants')
                files_id.append(file.id)
            except Exception as e:
                logger.warning(e)
        return files_id
    
    def create_bot(
        self,
        user_bot_name: t.Union[str],
        user_bot_instructions: t.Union[str],
        user_bot_model: t.Union[str],
        user_bot_file_list: t.Optional[list] = []
    ):
        
        file_ids = self.create_file(user_bot_file_list)
        
        # self.user_bot = UserBot(user_bot_name, user_bot_instructions, user_bot_model)
        user_bot = self.client.beta.assistants.create(
            name= user_bot_name,
            instructions=user_bot_instructions,
            model = user_bot_model,
            tools=[{"type": "retrieval"}],
            file_ids = file_ids
        )
        
        # conversation_thread = self.client.beta.threads.create()
        return user_bot.id, file_ids
    
    def create_thread(
            self,
        ):
            conversation_thread = self.client.beta.threads.create()
            return conversation_thread.id


    def generate_evaluator_message(
        self,
        evaluator_persona: t.Union[str],
        user_bot_purpose: t.Union[str],
        evaluator_bot_model: t.Union[str],
        conversation: t.Optional[list] = [],
        evaluator_max_tokens: t.Optional[int] = 200
        ):
        if len(conversation)<1:
            evaluator_response = self.client.chat.completions.create(
                    model=evaluator_bot_model, 
                    messages=[{"role": "system", "content": ASSISTANT_EVALUATOR_STARTER_PROMPT.format(evaluator_persona = evaluator_persona)}],
                    max_tokens = evaluator_max_tokens,
                    temperature = 0.5
                ).choices[0].message.content
        else: 
            evaluator_response = self.client.chat.completions.create(
                    model=evaluator_bot_model, 
                    messages=[{"role": "system", "content": ASSISTANT_EVALUATOR_PROMPT.format(evaluator_persona = evaluator_persona,user_bot_purpose = user_bot_purpose, conversation = conversation)}],
                    max_tokens = evaluator_max_tokens,
                    temperature = 0.5
                ).choices[0].message.content
            
        return evaluator_response

    def simulate_conversation(
        self,
        user_bot_name: t.Union[str],
        user_bot_instructions: t.Union[str],
        user_bot_purpose: t.Union[str],
        evaluator_persona_list: t.Union[str, list],
        user_bot_model: t.Optional[str] = "gpt-4-0125-preview",
        user_bot_file_list: t.Optional[list] = [],
        evaluator_bot_model: t.Optional[str] = "gpt-4-0125-preview",
        trial_count: t.Optional[int] = 4,
        evaluator_max_tokens: t.Optional[int] = 200,
        show_thread_id: t.Optional[bool] = True,
    ):
        if isinstance(evaluator_persona_list, str):
            evaluator_persona_list = [evaluator_persona_list]

        conversation_list = []
        
        user_bot_id, user_bot_file_id = self.create_bot(
            user_bot_name = user_bot_name,
            user_bot_instructions = user_bot_instructions,
            user_bot_model = user_bot_model,
            user_bot_file_list = user_bot_file_list
            )
        
        for index, evaluator_persona in enumerate(evaluator_persona_list):
            
            conversation = []
            i = 1
            
            user_bot_thread_id = self.create_thread()
            
            while i <= trial_count:
                evaluator_response = self.generate_evaluator_message(
                    conversation = conversation,
                    user_bot_purpose = user_bot_purpose,
                    evaluator_persona = evaluator_persona,
                    evaluator_bot_model = evaluator_bot_model,
                    evaluator_max_tokens = evaluator_max_tokens
                )
                conversation.append(
                    {
                        'role' : 'user',
                        'content' : evaluator_response
                    }    
                )
                thread_message = self.client.beta.threads.messages.create(
                                    thread_id = user_bot_thread_id,
                                    role = "user",
                                    content = evaluator_response,
                                    )
                run = self.client.beta.threads.runs.create(
                        thread_id=user_bot_thread_id,
                        assistant_id=user_bot_id,)
                
                while run.status in ['queued', 'in_progress', 'cancelling']:
                    time.sleep(1) # Wait for 1 second
                    run = self.client.beta.threads.runs.retrieve(
                        thread_id = user_bot_thread_id,
                        run_id=run.id
                    )
                    
                if run.status == 'completed': 
                    last_message_id = self.client.beta.threads.messages.list(
                        thread_id = user_bot_thread_id
                    ).first_id
                    
                    bot_message = self.client.beta.threads.messages.retrieve(
                                    message_id = last_message_id,
                                    thread_id = user_bot_thread_id,
                    ).content[0].text.value
                    conversation.append(
                        {
                            'role' : 'bot',
                            'content' : bot_message
                        }
                    )
                i+=1
            if show_thread_id:
                conversation_list.append(
                    {
                        'evaluator_persona': evaluator_persona,
                        'conversation': conversation,
                        'assistant_id': user_bot_id,
                        'thread_id':user_bot_thread_id,
                        'file_id':user_bot_file_id
                    }
                )
            
            else:
                conversation_list.append(
                    {
                        'evaluator_persona': evaluator_persona,
                        'conversation': conversation
                    }
                )
            logger.info(f"Step {index+1} of {len(evaluator_persona_list)} Completed")
            
        conversation_list_with_context = file_parser.vector_search(
            conversation = conversation_list,
            file_list = user_bot_file_list,
            openai_api_key=self.settings.openai_api_key
        )
        
        logger.success(f"Simulation Completed successfully")
        
        return conversation_list_with_context
    
    def evaluate(
        self,
        data: t.Union[list],
        checks: t.Union[list]
    ):
        data2 = copy.deepcopy(data)
        check2 = []
        for check in checks:
            if isinstance(check, ConversationSatisfaction):
                pass
            else:
                check2.append(check)
        
        
        for index_outer in range(len(data2)):
            conversation_pair = []
            eval_input = []
            for index_inner in range(len(data2[index_outer]['conversation'])):
                if (data2[index_outer]['conversation'][index_inner]['role'] == 'user') and (index_inner + 1 in range(len(data2[index_outer]['conversation']))):
                    formatted_conversation =[data2[index_outer]['conversation'][index_inner], data2[index_outer]['conversation'][index_inner+1]]
                    
                    formatted_conversation[0]['role'] = data2[index_outer]['conversation'][index_inner]['role']
                    formatted_conversation[0]['content'] = data2[index_outer]['conversation'][index_inner]['content']
                    try: formatted_conversation[0]['rewritten_query'] = data2[index_outer]['conversation'][index_inner]['rewritten_query']
                    except: pass
                    formatted_conversation[1]['role'] = data2[index_outer]['conversation'][index_inner+1]['role']
                    formatted_conversation[1]['content'] = data2[index_outer]['conversation'][index_inner+1]['content']                    
                    conversation_pair.append(formatted_conversation)
                    
            data2[index_outer]['conversation'] = conversation_pair
            
            for pair in data2[index_outer]['conversation']:
                for item in pair:
                    if item['role'] == 'user':
                        try: question = item['rewritten_query']
                        except: question = item['content']
                        context = item['retrieved_context']
                    elif item['role'] == 'bot':
                        response = item['content']
                        
                
                eval_input.append({
                            'question': question,
                            'context': context,
                            'response': response,
                        })
                    
            res = self.eval_llm.evaluate(
                                    data = eval_input,
                                    checks = check2
                                )
            res = [{k: v for k, v in item.items() if k not in ['question','context','response']} for item in res]
            
            for id, value in enumerate(res):
                scores_dict = {**value}  
                data2[index_outer]['conversation'][id].append(scores_dict)  


        if any(isinstance(check, ConversationSatisfaction) for check in checks):
            for check in checks:
                if isinstance(check, ConversationSatisfaction):
                    conversation_satisfaction_check = check
                    if (not hasattr(conversation_satisfaction_check, 'llm_persona') ):
                        llm_persona = 'bot'
                    else:
                        llm_persona = conversation_satisfaction_check.llm_persona
                        
                    if (not hasattr(conversation_satisfaction_check, 'user_persona') ):
                        user_persona = 'user'
                    else:
                        user_persona = conversation_satisfaction_check.user_persona 
                        
            res = self.eval_llm.evaluate(
                data = data,
                checks = [ConversationSatisfaction(user_persona=user_persona, llm_persona=llm_persona)]
            )
            for index in range(len(data2)):
                data2[index]['score_conversation_satisfaction'] = res[index]['score_conversation_satisfaction']
                data2[index]['explanation_conversation_satisfaction'] = res[index]['explanation_conversation_satisfaction']
        return data2