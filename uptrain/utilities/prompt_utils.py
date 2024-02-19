SCENARIO_DESCRIPTION_TEMPLATE = """Here is a brief description of the scenario under which the given response was generated.
{scenario_description}
"""


def parse_scenario_description(scenario_description):
    """
    Parses a scenario description and extracts variables enclosed within '{{' and '}}' or '{' and '}'.

    Args:
        scenario_description (str): The scenario description containing variables.

    Returns:
        tuple: A tuple containing the parsed scenario description and a list of extracted variables.
               The first element is the parsed scenario description with variables formatted as '{var}'.
               The second element is a list of extracted variables.
    """
    scenario_vars = []
    if scenario_description is not None and len(scenario_description):
        scenario_description = SCENARIO_DESCRIPTION_TEMPLATE.format(
            scenario_description=scenario_description
        )
        if "{{" in scenario_description:
            scenario_vars = [
                x.split("}}")[0] for x in scenario_description.split("{{")[1:]
            ]
            for var in scenario_vars:
                scenario_description = scenario_description.replace(
                    "{{" + var + "}}", "{" + var + "}"
                )
        elif "{" in scenario_description:
            scenario_vars = [
                x.split("}")[0] for x in scenario_description.split("{")[1:]
            ]
    else:
        scenario_description = ""
    return scenario_description, scenario_vars
