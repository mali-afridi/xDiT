from abc import abstractmethod, ABCMeta
from typing import List

from diffusers.schedulers import SchedulerMixin
from pipefuser.base_wrapper import PipeFuserBaseWrapper
from pipefuser.config.config import InputConfig, ParallelConfig, RuntimeConfig

class PipeFuserSchedulerBaseWrapper(PipeFuserBaseWrapper, metaclass=ABCMeta):
    def __init__(
        self,
        module: SchedulerMixin,
        parallel_config: ParallelConfig,
        runtime_config: RuntimeConfig,
    ):
        super().__init__(
            module=module,
            parallel_config=parallel_config, 
            runtime_config=runtime_config
        )

    def __setattr__(self, name, value):
        if name == 'module':
            super().__setattr__(name, value)
        elif (hasattr(self, 'module') and 
              self.module is not None and 
              hasattr(self.module, name)):
            setattr(self.module, name, value)
        else:
            super().__setattr__(name, value)

    def set_input_config(self, input_config: InputConfig):
        self.input_config = input_config

    def set_patched_mode(self, patched: bool):
        self.patched_mode = patched

    def reset_patch_idx(self):
        self.current_patch_idx = 0

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
        self.num_pipeline_patch = num_pipeline_patch
        self.patches_height = patches_height
        self.patches_start_idx = patches_start_idx
        self.pp_patches_height = pp_patches_height
        self.pp_patches_start_idx_local = pp_patches_start_idx_local
        self.pp_patches_start_end_idx = pp_patches_start_end_idx
        self.pp_patches_token_start_end_idx = pp_patches_token_start_end_idx

    @abstractmethod
    def step(self, *args, **kwargs):
        pass
