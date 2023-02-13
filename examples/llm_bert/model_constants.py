model_checkpoint = "distilbert-base-uncased"
chunk_size = 128
wwm_probability = 0.2
train_size = 0.9 # 100
test_size = 0.1 # int(0.1 * train_size)
batch_size = 64
mlm_probability = 0.15