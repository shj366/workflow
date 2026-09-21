import importlib
import logging


class ReflectUtil:
    @staticmethod
    def new_instance(clazz: str, **kwargs):
        """
        根据类名反射实例
        @param clazz: 类字符串
        
        规则一：约定包名和类名不一致：module.path::ClassName
        规则二：约定包名和类名一致，例：module.path.ClassName
        """
        module_path = clazz
        handle_class_name = clazz.split(".")[-1]
        
        # 支持 :: 分隔符
        arr = clazz.split("::")
        if len(arr) == 2:
            module_path = arr[0]
            handle_class_name = arr[1]
        
        try:
            model_module = importlib.import_module(module_path)
            HandleClass = getattr(model_module, handle_class_name)
            if kwargs:
                handle_instance = HandleClass(**kwargs)
            else:
                handle_instance = HandleClass()
            return handle_instance
        except (ImportError, AttributeError) as e:
            logging.error(f"Failed to load class {clazz}: {e}")
            return None

