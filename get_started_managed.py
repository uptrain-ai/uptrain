from uptrain import APIClient, Evals, CritiqueTone
import json

UPTRAIN_API_KEY = "up-***************" 

data = [{
    'question': 'Which is the most popular global sport?',
    'context': "The popularity of sports can be measured in various ways, including TV viewership, social media presence, number of participants, and economic impact. Football is undoubtedly the world's most popular sport with major events like the FIFA World Cup and sports personalities like Ronaldo and Messi, drawing a followership of more than 4 billion people. Cricket is particularly popular in countries like India, Pakistan, Australia, and England. The ICC Cricket World Cup and Indian Premier League (IPL) have substantial viewership. The NBA has made basketball popular worldwide, especially in countries like the USA, Canada, China, and the Philippines. Major tennis tournaments like Wimbledon, the US Open, French Open, and Australian Open have large global audiences. Players like Roger Federer, Serena Williams, and Rafael Nadal have boosted the sport's popularity. Field Hockey is very popular in countries like India, Netherlands, and Australia. It has a considerable following in many parts of the world.",
    'response': 'Football is the most popular sport with around 4 billion followers worldwide'
}]

client = APIClient(uptrain_api_key=UPTRAIN_API_KEY)
results = client.log_and_evaluate(
    project_name="Sample-Project",
    data=data,
    evals=[Evals.CONTEXT_RELEVANCE, Evals.FACTUAL_ACCURACY, Evals.RESPONSE_RELEVANCE, CritiqueTone(persona="teacher")]
)

print(json.dumps(results, indent=3))
