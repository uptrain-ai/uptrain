import re
from uptrain.v0.core.lib.helper_funcs import read_json, dependency_required
from uptrain.v0.core.classes.measurables import Measurable

try:
    import openai
except:
    openai = None


def extractNumber(text):
    return int(re.findall(r'\d+', text)[0])


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
        name = 'grammar_feature'
        if self.feature_name:
            name = name + '_' + self.feature_name
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
                {"role": "system", "content": "You are a grammatical correctnes evaluator who only gives only a number and no explanation."},
                {"role": "user", "content": "Score following sentence on grammatical correctness on a scale of 0 to 100: \n\n {statement}".format(statement=summary)},
            ],
            temperature=0,
        )
        try:
            return extractNumber(response.choices[0]['message']['content'])
        except:
            return -1

