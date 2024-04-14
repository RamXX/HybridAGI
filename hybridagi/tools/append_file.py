"""The append file tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
import dspy
from .base import BaseTool
from ..hybridstores.filesystem.filesystem import FileSystem
from ..parsers.path import PathOutputParser
from ..types.state import AgentState

class AppendFileSignature(dspy.Signature):
    """Infer the filename and content to append into a file"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (How to do it)")
    filename = dspy.OutputField(desc = "The name of the file (short and concise) to append into without additional details")
    content = dspy.OutputField(desc = "The content to append to the file")

class AppendFileTool(BaseTool):

    def __init__(
            self,
            filesystem: FileSystem,
            agent_state: AgentState,
        ):
        super().__init__(name = "AppendFile")
        self.predict = dspy.Predict(AppendFileSignature)
        self.agent_state = agent_state
        self.filesystem = filesystem
        self.path_parser = PathOutputParser()

    def append_file(self, filename: str, content: str) -> str:
        try:
            filename = self.path_parser.parse(filename)
            filename = self.agent_state.context.eval_path(filename)
            self.filesystem.append_texts(texts = [content], ids = [filename])
            return "Successfully append"
        except Exception as err:
            return str(err)
    
    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        if not disable_inference:
            prediction = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            dspy.Suggest(
                len(prediction.filename) != 0,
                "The filename should not be empty"
            )
            dspy.Suggest(
                len(prediction.filename) < 100,
                "The filename should be short and consice"
            )
            observation = self.append_file(prediction.filename, prediction.content)
            return dspy.Prediction(
                filename = filename,
                content = prediction.content,
                observation = observation,
            )
        else:
            raise NotImplementedError("Disabling inference for AppendFile not supported")

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            filesystem = self.filesystem,
            agent_state = self.agent_state,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy