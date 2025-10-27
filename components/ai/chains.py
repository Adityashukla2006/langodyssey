from langchain_classic.chains import LLMChain
from components.ai.prompt_templates import PromptTemplates
from langchain_openai import ChatOpenAI


class Chains:
    def __init__(self):
        self.prompt_templates = PromptTemplates()
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-5-nano")

    def init_apis_and_chains(self):
        lesson_prompt, tutor_prompt, evaluation_prompt = self.prompt_templates.init_prompts()

        lesson_chain = LLMChain(llm=self.llm, prompt=lesson_prompt)
        evaluation_chain = LLMChain(llm=self.llm, prompt=evaluation_prompt)
        tutor_chain = LLMChain(llm=self.llm, prompt=tutor_prompt)

        return lesson_chain, evaluation_chain, tutor_chain