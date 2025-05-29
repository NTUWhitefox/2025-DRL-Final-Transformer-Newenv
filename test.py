import time
from typing import Union, Tuple, List

import numpy as np
from gym.spaces import MultiDiscrete
from gym_microrts import microrts_ai
from gym_microrts.envs.vec_env import MicroRTSGridModeVecEnv
from stable_baselines3.common.vec_env import VecEnvWrapper, VecVideoRecorder

flatten_action = np.full((8* 8, 7), [0,0,0,0,0,0,0])

envs1 = MicroRTSGridModeVecEnv(
        num_selfplay_envs=0,
        num_bot_envs=1,
        max_steps=2000,
        render_theme=2,
        ai2s=[microrts_ai.coacAI],
        map_paths=["maps/16x16/basesWorkers16x16.xml"],
        reward_weight=[0 ,0 ,0 ,0 ,0 ,0],
    )

print(envs1.action_space)
print(envs1.action_space.shape)