import torch

model_checkpoint = "distilbert-base-uncased"
chunk_size = 128
wwm_probability = 0.2
train_size = 0.9 # 100
test_size = 0.1 # int(0.1 * train_size)
batch_size = 32
mlm_probability = 0.15

num_train_epochs = 2
model_save_file_name = 'distilbert-base-uncased-finetuned-llm-uptrain'

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# We will be generating some data ourselves using the lists below

# Note that some sentences may not make complete sense in comparison to spoken
# english but for the sake of demonstration, it's alright

PRODUCTS = [
    'gym wear', 'jackets', 'shirts',
    'running shoes', 'basketballs', 'caps', 'pants', 'socks',
    'trousers', 'training shoes', 'basketball shoes', 'shoes',
    'athletic wear', 'sports wear', 'footballs',
    'performance gear', 'hats', 'sweaters', 'tshirts', 'wristbands',
    'backpacks', 'tshirts', 'hoodies', 'trainers',
    'soccer shoes',
]

POSITIVE_SENTIMENT_ADJECTIVES = [
    'user-friendly', 'innovative', 'support', 'good-looking', 'efficient',
    'stylish', 'breathable', 'flexibility', 'trendsetting', 'performance',
    'impressive', 'resilient', 'durability', 'durable', 'athletic', 'breathability',
    'cheap', 'comfort', 'comfortable', 'inexpensive', 'premium', 'sleek',
    'performance-oriented', 'fashionable', 'quality', 'flexible', 'stability',
    'look', 'functional', 'sporty', 'lightweight', 'bounce', 'grip', 'modern',
    'fit', 'ergonomic', 'versatile', 'style', 'design', 'cushioning', 'traction',
    'high-quality', 'revolutionary'
]

NEGATIVE_SENTIMENT_ADJECTIVES = [
    'uncomfortable', 'flimsy', 'poor quality', 'outdated', 'unfashionable',
    'heavy', 'inferior', 'unathletic', 'expensive', 'costly',
    'overpriced', 'defective', 'ugly', 'dirty', 'faulty',
    'non-durable', 'tacky', 'lacking in performance', 'clunky', 'bulky',
    'awkward', 'disappointing', 'unreliable', 'displeasing', 'unsatisfactory'
]

ADJECTIVES = POSITIVE_SENTIMENT_ADJECTIVES + NEGATIVE_SENTIMENT_ADJECTIVES

COMPANIES = [
  # repeat a couple of times for higher positive examples of Nike
    'nike', 'nike', 'nike', 'nike', 'nike', 'nike', 'nike', 'adidas', 'puma',
    'under armour', 'reebok', 'converse', 'vans', 'fila', 'asics'
]

JOINERS = [
    'are', 'is', 'offer', 'provide', 'feature', 'boast',
    'are known for being', 'are recognized for being', 'are famous for being',
    'are renowned for being', 'are praised for being',
]
