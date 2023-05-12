import re
from uptrain.core.lib.helper_funcs import read_json, dependency_required
from uptrain.core.classes.measurables import Measurable

try:
    import openai
except:
    openai = None


def extractNumber(text):
    return int(re.findall(r"\d+", text)[0])


@dependency_required(openai, "openai")
class GrammerScoreMeasurable(Measurable):
    def __init__(self, framework, feature_name) -> None:
        super().__init__(framework)
        self.feature_name = feature_name
        openai_key = framework.config_obj.license_args.openai_key
        if openai_key:
            openai.api_key = openai_key
        else:
            raise Exception("OpenAI key not found in config")

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None):
        if self.feature_name:
            vals = inputs[self.feature_name]
        else:
            vals = outputs
        vals = [self.getGrammaticalCorrectnessScore(x) for x in vals]
        return vals

    def col_name(self) -> str:
        name = "grammar_feature"
        if self.feature_name:
            name = name + "_" + self.feature_name
        return name

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        vals = x[self.feature_name]
        vals = [self.getGrammaticalCorrectnessScore(y) for y in vals]
        return vals

    def getGrammaticalCorrectnessScore(self, summary):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a grammatical correctnes evaluator who only gives only a number and no explanation.",
                },
                {
                    "role": "user",
                    "content": "Score following sentence on grammatical correctness on a scale of 0 to 100: \n\n {statement}".format(
                        statement=summary
                    ),
                },
            ],
            temperature=0,
        )
        try:
            return extractNumber(response.choices[0]["message"]["content"])
        except:
            return -1


@dependency_required(openai, "openai")
class SentenceSimilarityMeasurable(Measurable):
    def __init__(self, framework, feature1, feature2) -> None:
        super().__init__(framework)
        self.feature1 = feature1
        self.feature2 = feature2
        openai_key = framework.config_obj.license_args.openai_key
        if openai_key:
            openai.api_key = openai_key
        else:
            raise Exception("OpenAI key not found in config")

    def _compute(self, inputs=None, outputs=None, gts=None, extra=None):
        sent1_list = inputs[self.feature1]
        sent2_list = inputs[self.feature2]
        vals = [
            self.getSentenceSimilarity(sent1_list[i], sent2_list[i])
            for i in range(len(sent1_list))
        ]
        return vals

    def col_name(self) -> str:
        return "sentence_similarity_openai"

    # TODO: Decommission and find a generic way
    def extract_val_from_training_data(self, x):
        sent1_list = x[self.feature1]
        sent2_list = x[self.feature2]
        vals = [
            self.getSentenceSimilarity(sent1_list[i], sent2_list[i])
            for i in range(len(sent1_list))
        ]
        return vals

    def getSentenceSimilarity(self, sent1, sent2):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentence comparator who only gives only a dissimilarity score and no explanation.",
                },
                {
                    "role": "user",
                    "content": f"Score following two sentences on dissimilarity on a scale of 0 to 100: \n\n Sentence 1: {sent1} \n Sentence 2: {sent2}",
                },
            ],
            temperature=0,
        )
        try:
            output = response.choices[0]["message"]["content"]
            return extractNumber(output)
        except:
            return -1
