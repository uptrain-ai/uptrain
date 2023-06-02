from InstructorEmbedding import INSTRUCTOR

model = INSTRUCTOR('hkunlp/instructor-xl')

def embed(sentence, feature):
    return model.encode([[f"Represent the {feature} sentence: ", sentence]])
