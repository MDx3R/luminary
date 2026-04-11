from typing import Any, ClassVar

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


class MappedOpenAIEmbedding(OpenAIEmbedding):
    """Maps logical embedding model names to provider-specific model ids.

    Some OpenAI-compatible providers use prefixed model ids (e.g. openai/text-embedding-3-small).
    This class maps the configured embed_model to the actual API model via MODEL_MAP.
    """

    MODEL_MAP: ClassVar[dict[str, str]] = {}

    def __init__(self, model: str, **kwargs: Any) -> None:
        api_model = self.MODEL_MAP.get(model, model)
        kwargs["model_name"] = api_model
        super().__init__(model=model, **kwargs)

    @classmethod
    def override(cls, key: str, value: str) -> None:
        cls.MODEL_MAP[key] = value


class MappedOpenAI(OpenAI):
    """MappedOpenAI overrides logic for building model request kwargs.

    Some OpenAI-compatible providers add prefixes to model identifiers, which
    doesn't work correctly with LlamaIndex. This class maps model names to their
    correct identifiers.
    """

    MODEL_MAP: ClassVar = {
        "gpt-5-nano": "openai/gpt-5-nano",
        "gpt-5-mini": "openai/gpt-5-mini",
        "gpt-5": "openai/gpt-5",
    }

    def _get_model_kwargs(self, **kwargs: Any) -> dict[str, Any]:
        result = super()._get_model_kwargs(**kwargs)

        model = result.get("model", self.model)
        if model in self.MODEL_MAP:
            result["model"] = self.MODEL_MAP[model]

        return result

    @classmethod
    def override(cls, key: str, value: str) -> None:
        cls.MODEL_MAP[key] = value
