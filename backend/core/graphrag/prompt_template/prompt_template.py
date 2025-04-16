from jinja2 import Template

class PromptTemplate:
    def __init__(self, template: str,input_variables):
        self.template = Template(template)
        self.input_variables = input_variables
    def render(self, **kwargs) -> str:
        return self.template.render(**kwargs)