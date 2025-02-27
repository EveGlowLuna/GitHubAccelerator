def pre_safe_import_module(api):
    """GitHubAccelerator专用签名绕过钩子"""
    import os
    from PyInstaller.utils.hooks import logger
    
    # 禁用Python优化以保留调试信息
    os.environ['PYTHONOPTIMIZE'] = '0'  
    
    # 添加核心模块的运行时依赖
    api.add_runtime_package('requests')
    api.add_runtime_package('pythonping')
    
    # 日志输出验证
    logger.info("GitHubAccelerator macOS签名验证绕过钩子已激活")