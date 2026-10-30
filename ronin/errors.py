class RoninError(Exception):
    code = 1
class SyntaxError(RoninError):
    code = 1
class SemanticError(RoninError):
    code = 2
class ExecutionError(RoninError):
    code = 3
class ConfigurationError(RoninError):
    code = 4
