class ExprUtil(object):

    @staticmethod
    def eval(expr: str, context: dict):
        if not expr:
            return None
        try:
            # 使用 eval 执行表达式，限制 globals 为空，locals 为 context
            return eval(expr, {"__builtins__": None}, context)
        except Exception as e:
            print(f"Error evaluating expression '{expr}': {e}")
            return False
