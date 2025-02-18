from abc import abstractmethod, ABCMeta
from functools import wraps
from typing import Any, List, Optional
from torch import nn

from pipefuser.config.config import InputConfig, ParallelConfig, RuntimeConfig


class PipeFuserBaseWrapper(metaclass=ABCMeta):

    def __init__(
        self, 
        module: Any,
        parallel_config: ParallelConfig,
        runtime_config: RuntimeConfig,
    ):
        self.module = module
        self.module_type = type(module)
        self.parallel_config = parallel_config
        self.runtime_config = runtime_config

        self.patched_mode = False
        self.current_patch_idx = 0
        self.num_pipeline_patch: int = parallel_config.pp_config.num_pipeline_patch
        self.patches_height: Optional[List[List[int]]] = None
        self.patches_start_idx: Optional[List[List[int]]] = None
        self.pp_patches_height: Optional[List[int]] = None
        self.pp_patches_start_idx_local: Optional[List[int]] = None
        self.pp_patches_start_end_idx: Optional[List[List[int]]] = None
        self.pp_patches_token_start_end_idx: Optional[List[List[int]]] = None
        self.input_config: Optional[InputConfig] = None

    def __getattr__(self, name: str):
        try:
            return getattr(self.module, name)
        except RecursionError:
            raise AttributeError(f"module {type(self.module).__name__} has no "
                                 f"attribute {name}")

    def __str__(self):
        return str(self.module)

    @staticmethod
    def forward_check_condition(func):
        @wraps(func)
        def check_condition_fn(self, *args, **kwargs):
            if self.input_config is None:
                raise ValueError("InputConfig is not set, please set it before "
                                 "calling forward")
            return func(self, *args, **kwargs)
        return check_condition_fn

    def patch_step(self):
        self.current_patch_idx += 1
        if self.current_patch_idx == \
                self.num_pipeline_patch:
            self.current_patch_idx = 0

    @abstractmethod
    def set_input_config(self, input_config: InputConfig):
        pass

    @abstractmethod
    def set_patched_mode(self, patched: bool):
        pass

    @abstractmethod
    def reset_patch_idx(self):
        pass

    @abstractmethod
    def set_num_pipeline_patch_and_patches_height(
        self, 
        num_pipeline_patch: int, 
        patches_height: List[List[int]], 
        patches_start_idx: List[List[int]],
        pp_patches_height: List[int],
        pp_patches_start_idx_local: List[int],
        pp_patches_start_end_idx: List[List[int]],
        pp_patches_token_start_end_idx: List[List[int]],
    ):
        pass