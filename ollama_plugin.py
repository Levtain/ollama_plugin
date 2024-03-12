import os
import json
import plugins
import ollama
from ollama import chat
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from plugins import *
from bridge import bridge
from common.expired_dict import ExpiredDict
from .util import *

# 消息队列 map
queue_map = dict()

# 响应队列 map
reply_map = dict()

@plugins.register(
    name="Ollama on wechat",
    desc="在微信上使用本地部署的ollama，更方便使用自用的猫娘（bushi）",
    version="0.1.0",
    author="drgcandle",
)

class Ollama (Plugin):
    def __init__(self): #自动载入配置文件中的配置
        super().__init__()
        self.host = conf().get("ollama_host")
        self.model = conf().get("ollama_model")

    def reply(self, query, context: Context = None) -> Reply:
            # Add prompt to active chats object
        response = ollama.chat(model='llama2', messages=[
        { 'role': 'user','content': 'Context',
        },])
        return Reply(content=response['message']['content'], type=ReplyType.TEXT)


    def get_help_text(self, verbose=False, **kwargs):
        help_text = "在微信使用Ollama的一些主要功能\n"
        if not verbose:
            return help_text
        trigger_prefix = conf().get("plugin_trigger_prefix", "$")
        help_text = f"使用方法:\n{trigger_prefix}" + " ollama_model: 设定当前模型为{选定的Ollama模型}。\n"
        help_text += f"{trigger_prefix}OM_L"+ " OM_L: 列出所有可选用的{ollama_model}。\n"
        help_text += "\n可选用的Ollama模型: \n"
        return help_text

    def _load_config_template(self):
        logger.debug("Ollama配置文件config.json没找到, 先用plugins/Ollama/config.json.template凑合凑合")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)

USER_FILE_MAP = ExpiredDict(conf().get("expires_in_seconds") or 60 * 30)