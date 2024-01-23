from litellm import acompletion, completion
import logging
import re
import json

EVALS_GENERATION_PROMPT_SIMPLE = """Here is my prompt template:

"{prompt}"

Based on the above prompt, I want to write assertions for my LLM pipeline to run on all pipeline responses. Here are some categories of assertion concepts I want to check for:

- Presentation Format: Is there a specific format for the response, like a comma-separated list or a JSON object?
- Example Demonstration: Does theh prompt template include any examples of good responses that demonstrate any specific headers, keys, or structures?
- Workflow Description: Does the prompt template include any descriptions of the workflow that the LLM should follow, indicating possible assertion concepts?
- Count: Are there any instructions regarding the number of items of a certain type in the response, such as “at least”, “at most”, or an exact number?
- Inclusion: Are there keywords that every LLM response should include?
- Exclusion: Are there keywords that every LLM response should never mention?
- Qualitative Assessment: Are there qualitative criteria for assessing good responses, including specific requirements for length, tone, or style?
- Other: Based on the prompt template, are there any other concepts to check in assertions that are not covered by the above categories, such as correctness, completeness, or consistency?

Give me a list of concepts to check for in LLM responses. Each item in the list should contain a string description of a concept to check for, its corresponding category, and the source, or phrase in the prompt template that triggered the concept.
For example, if the prompt template is "I am a still-life artist. Give me a bulleted list of colors that I can use to paint <object>.", then a concept might be "The response should include a bulleted list of colors." with category "Presentation Format" and source "Give me a bulleted list of colors".

Your answer should be a JSON list of objects within ```json ``` markers, where each object has the following fields: "concept", "category", and "source". Choose the most relevant assertion concepts and limit your choice to 5. Be specific and reasonable. MAKE SURE TO AVOID SIMILAR ASSERTIONS"""


def generate_evaluations(
    prompt_template: str,
    llm: str
) -> dict:
    """
    Generate assertion concepts to check for in the prompt template.

    Args:
    - prompt_template: the template for the prompt
    - llm: which LLM to use for generating evals 

    Returns:
    - concepts: the assertion concepts to check for in the prompt template
    """

    # Construct prompt to LLM
    messages = [
        {
            "content": "You are an expert Python programmer who is helping me write assertions for my LLM pipeline. The LLM pipeline accepts an example and prompt template, fills the template's placeholders with the example, and generates a response.",
            "role": "system",
        },
        {
            "content": EVALS_GENERATION_PROMPT_SIMPLE.format(prompt=prompt_template),
            "role": "user",
        },
    ]

    # Generate concepts
    try:
        response = completion(model=llm, messages=messages)

        reply = response["choices"][0]["message"]["content"]

        # Parse reply within ```json ``` markers
        reply = re.search(r"```json(.*?)\n```", reply, re.DOTALL).group(1)

        concepts = json.loads(reply)
        return {"concepts": concepts}

    except Exception as e:
        logging.error(e)
        return None


def generate_response(
    prompt_template: str,
    llm: str,
    task_data: dict
) -> str:
    
    """
    Generate responses for the given task data.

    Args:
    - prompt_template: the template for the prompt
    - llm: which LLM to use for generating responses
    - task_data: task variables to fill into prompt template

    Returns:
    - response: LLM output
    """

    # Construct prompt to LLM
    messages = [{
        "content": prompt_template.format(**task_data),
        "role": "user",
    }]
    
    try:
        response = completion(model=llm, messages=messages)
        reply = response["choices"][0]["message"]["content"]
        return reply
    except Exception as e:
        logging.error(e)
        return None


EXAMPLES = [
    {
        "topic": "Enhancing Team Collaboration with Project Management Software",
        "context": "Efficient team collaboration is crucial for project success. Delays, miscommunication, and disorganized tasks can hinder progress and impact the overall outcome. Project management software streamlines workflows, improves communication, and ensures that everyone is on the same page, fostering a collaborative and productive work environment.",
    },
    {
        "topic": "Maximizing Business Efficiency with Cloud-Based Accounting Solutions",
        "context": "Outdated accounting practices can impede business growth, leading to errors and inefficiencies. Cloud-based accounting solutions provide real-time insights, streamline financial processes, and ensure accuracy. Embracing this technology is the key to staying competitive and maximizing overall business efficiency.",
    },
    {
        "topic": "Elevating Customer Engagement Through Social Media Marketing Tools",
        "context": "In the digital age, effective social media engagement is paramount for businesses. Social media marketing tools empower businesses to analyze, strategize, and optimize their online presence. Elevate your customer engagement by harnessing the power of these tools to connect with your audience in meaningful ways.",
    },
    {
        "topic": "Simplifying Expense Management with AI-Powered Accounting Software",
        "context": "Managing expenses manually is time-consuming and prone to errors. AI-powered accounting software automates expense tracking, categorization, and reporting. Experience the ease of managing finances with our solution, allowing you to focus more on your business and less on tedious administrative tasks.",
    },
    {
        "topic": "Enhancing Customer Support with AI Chatbots",
        "context": "Providing prompt and personalized customer support is a challenge. AI chatbots offer a scalable solution, providing instant responses and freeing up human agents for more complex queries. Elevate your customer support game with our AI-driven chatbot technology.",
    },
    {
        "topic": "Accelerating Software Development with Continuous Integration Tools",
        "context": "In today's fast-paced development environment, delays can be detrimental. Continuous Integration tools automate code integration and testing, ensuring a smooth and rapid software development lifecycle. Boost your team's efficiency and deliver high-quality code with our CI/CD solution.",
    },
    {
        "topic": "Securing Business Data with Cloud-Based Encryption Services",
        "context": "Data security is a top concern for businesses in the digital age. Our cloud-based encryption services provide robust protection for sensitive information, safeguarding against unauthorized access and potential data breaches. Strengthen your business's defense against cyber threats with our encryption solution.",
    },
    {
        "topic": "Streamlining HR Processes with Cloud-Based Employee Management",
        "context": "Traditional HR processes can be cumbersome and time-consuming. Our cloud-based employee management solution simplifies HR tasks, from onboarding to performance reviews. Elevate your HR efficiency and create a positive employee experience with our intuitive and comprehensive platform.",
    },
    {
        "topic": "Facilitating Remote Collaboration with Virtual Workspace Solutions",
        "context": "The rise of remote work necessitates efficient collaboration tools. Our virtual workspace solution provides a centralized platform for seamless communication, file sharing, and project management. Empower your remote teams to collaborate effectively and enhance productivity with our innovative technology.",
    },
    {
        "topic": "Improving Website Performance with AI-Driven Optimization",
        "context": "A slow website can result in user frustration and lost opportunities. Our AI-driven optimization tool enhances website performance by analyzing user behavior and making real-time adjustments. Elevate user experience and ensure optimal website speed with our cutting-edge solution.",
    },
    {
        "topic": "Empowering Sales Teams with AI-Enhanced CRM",
        "context": "Sales success depends on effective customer relationship management. Our AI-enhanced CRM system automates tasks, predicts customer preferences, and provides actionable insights. Transform your sales processes and drive revenue growth with our intelligent CRM solution.",
    },
    {
        "topic": "Ensuring Code Quality with Automated Code Review Tools",
        "context": "Code quality is paramount in software development. Our automated code review tools analyze codebase, identify issues, and ensure adherence to coding standards. Elevate your development process and deliver high-quality code with our efficient code review solution.",
    }
]

