import re
import yaml


class TemplateEngine:
    def __init__(self, data):
        self.path_matcher = re.compile(r'\$\{([^}^{]+)\}')
        self.data = data

    def path_constructor(self, loader, node):
        value = node.value
        match = self.path_matcher.match(value)
        var = match.group()[2:-1]
        val = self.data.get(var)
        # needed to prevent converting integers to strings
        if value[match.end():] == "":
            return val
        else:
            return str(val) + value[match.end():]

    def load_yaml(self, filename):
        yaml.add_implicit_resolver('!path', self.path_matcher)
        yaml.add_constructor('!path', self.path_constructor)

        cont = open(filename)
        p = yaml.load(cont, Loader=yaml.FullLoader)
        return p

    def replace(self, filename):
        y = self.load_yaml(filename)
        return yaml.dump(y, Dumper=yaml.Dumper)
