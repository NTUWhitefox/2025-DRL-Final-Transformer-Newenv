from typing import Tuple
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from transformer_agent.base_agent import Actor, CategoricalMasked
from transformer_agent.weighted_agent import WeightedCritic


def reshape_observation_mixed_embedded(x: torch.Tensor, device: str) -> Tuple[
    torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Converts original Micro-RTS observation into datastructures necessary to the transformer.
    :param x: [batch_dim,height,width,observation_state]
    :param device: cpu or gpu device
    :return:
    reshaped observation [batch_dim, height * width, embed_size]
    boolean padding mask (pass on to transformer) [batch_dim, height * width]
    all entity counts (players and resource) [batch_dim]
    player unit positions bitmap [batch_dim, height * width]
    player unit mask [batch_dim, height * width]
    enemy unit mask [batch_dim, height * width]
    neutral unit mask [batch_dim, height * width]
    """
    # indices in observation where unit and resource positions are encoded.
    player_1, player_2, resource = 11, 12, 14
    N, H, W, C = x.shape
    x_reshaped = x.view(N, H * W, C)
    out = torch.zeros(N, H * W, C + 1, dtype=torch.int16).to(device)  # unit coordinate + features
    entity_mask = torch.ones(N, H * W, dtype=torch.bool).to(device)
    player_unit_mask = torch.ones(N, H * W, dtype=torch.bool).to(device)
    enemy_unit_mask = torch.ones(N, H * W, dtype=torch.bool).to(device)
    neutral_unit_mask = torch.ones(N, H * W, dtype=torch.bool).to(device)
    # TODO this loop can be removed using torch.split()
    entity_pos = [torch.cat((o[:, player_1].nonzero(),
                             o[:, player_2].nonzero(),
                             o[:, resource].nonzero())) for o in x_reshaped]
    entity_unit_counts = (x_reshaped[:, :, player_1].count_nonzero(axis=1) +
                          x_reshaped[:, :, player_2].count_nonzero(axis=1) +
                          x_reshaped[:, :, resource].count_nonzero(axis=1)).to(device)
    player_unit_counts = x_reshaped[:, :, player_1].count_nonzero(axis=1)
    enemy_unit_indices = player_unit_counts + x_reshaped[:, :, player_2].count_nonzero(axis=1)
    neutral_unit_indices = enemy_unit_indices + x_reshaped[:, :, resource].count_nonzero(axis=1)

    for i in range(N):
        num_entities = entity_pos[i].shape[0]
        # Get position feature
        unit_positions = entity_pos[i][:, 0]
        out[i, :num_entities, 0] = unit_positions
        # Get one-hot encodings for all other features
        out[i, :num_entities, 1:] = x_reshaped[i, unit_positions]

        entity_mask[i, :num_entities] = False
        player_unit_mask[i, :player_unit_counts[i]] = False
        enemy_unit_mask[i, player_unit_counts[i]:enemy_unit_indices[i]] = False
        neutral_unit_mask[i, enemy_unit_indices[i]:neutral_unit_indices[i]] = False

    player_unit_positions = x_reshaped[:, :, player_1].to(device)
    return out, entity_mask, entity_unit_counts, player_unit_positions, \
           player_unit_mask, enemy_unit_mask, neutral_unit_mask


class MixedEmbeddedAgent(nn.Module):
    def __init__(self, map_size, envs, device, num_layers=5, dim_feedforward=512, num_heads=7,
                 padding=0, embed_size=64):
        super(MixedEmbeddedAgent, self).__init__()

        # Presently arbitrarily chosen to match original size, except for position.
        self.max_embed_value = map_size
        self.map_size = map_size
        self.embed_size = embed_size
        self.device = device
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.input_size = self.embed_size + 27  # position embedding size + size of other features
        self.padding = padding
        self.padded_size = self.input_size + padding
        self.map_embedder = nn.Embedding(self.max_embed_value, self.embed_size)
        encoder_layer = nn.TransformerEncoderLayer(d_model=self.padded_size,
                                                   nhead=self.num_heads,
                                                   dim_feedforward=dim_feedforward)
        self.network = nn.TransformerEncoder(encoder_layer, num_layers=self.num_layers)
        self.actor = Actor(self.padded_size, map_size, envs, device)
        self.critic = WeightedCritic(device, self.padded_size, envs)

    # TODO Type this stuff
    def forward(self, x, bool_mask):
        N, S, _ = x.shape
        map_positions = x[:, :, 0].type(torch.IntTensor).to(self.device)
        map_embeddings = self.map_embedder(map_positions)
        combined = torch.cat((map_embeddings, x[:, :, 1:]), dim=-1)
        rearranged = combined.reshape(N, S, -1).permute(1, 0, 2)
        padded = F.pad(rearranged, (0, self.padding))
        return self.network(padded, src_key_padding_mask=bool_mask)

    def get_action(self, x,
                   entity_mask,
                   entity_count,
                   player_unit_position,
                   player_unit_mask,
                   action=None, invalid_action_masks=None, envs=None):
        # There's no point in passing in tensors we will mask out anyway, so we trim them here.
        max_units_in_batch = torch.max(entity_count)
        trimmed_x = x[:, :max_units_in_batch, :]
        trimmed_ent_mask = entity_mask[:, :max_units_in_batch]
        trimmed_unit_mask = player_unit_mask[:, :max_units_in_batch]
        base_out = self.forward(trimmed_x, trimmed_ent_mask)
        logits = self.actor(base_out, player_unit_position, trimmed_unit_mask)
        # OLD CODE - DO NOT CHANGE
        grid_logits = logits.view(-1, envs.action_space.nvec[1:].sum())
        split_logits = torch.split(grid_logits, envs.action_space.nvec[1:].tolist(), dim=1)

        # Called during exploration
        if action is None:
            invalid_action_masks = torch.tensor(np.array(envs.vec_client.getMasks(0)), dtype=torch.bool).to(self.device)
            invalid_action_masks = invalid_action_masks.view(-1, invalid_action_masks.shape[-1])
            split_invalid_action_masks = torch.split(invalid_action_masks[:, 1:],
                                                     envs.action_space.nvec[1:].tolist(),
                                                     dim=1)
            multi_categoricals = [CategoricalMasked(self.device, logits=logits, masks=iam) for (logits, iam) in
                                  zip(split_logits, split_invalid_action_masks)]
            action = torch.stack([categorical.sample() for categorical in multi_categoricals])
        # Called during PPO
        else:
            invalid_action_masks = invalid_action_masks.view(-1, invalid_action_masks.shape[-1])
            action = action.view(-1, action.shape[-1]).T
            split_invalid_action_masks = torch.split(invalid_action_masks[:, 1:],
                                                     envs.action_space.nvec[1:].tolist(),
                                                     dim=1)
            multi_categoricals = [CategoricalMasked(self.device, logits=logits, masks=iam) for (logits, iam) in
                                  zip(split_logits, split_invalid_action_masks)]
        logprob = torch.stack([categorical.log_prob(a) for a, categorical in zip(action, multi_categoricals)])
        entropy = torch.stack([categorical.entropy() for categorical in multi_categoricals])
        num_predicted_parameters = len(envs.action_space.nvec) - 1
        logprob = logprob.T.view(-1, self.map_size, num_predicted_parameters)
        entropy = entropy.T.view(-1, self.map_size, num_predicted_parameters)
        action = action.T.view(-1, self.map_size, num_predicted_parameters)
        invalid_action_masks = invalid_action_masks.view(-1, self.map_size, envs.action_space.nvec[1:].sum() + 1)
        return action, logprob.sum(1).sum(1), entropy.sum(1).sum(1), invalid_action_masks

    def get_value(self, x, entity_mask, entity_count, player_unit_mask, enemy_unit_mask, neutral_unit_mask):
        max_units_in_batch = torch.max(entity_count)
        trimmed_x = x[:, :max_units_in_batch, :]
        trimmed_mask = entity_mask[:, :max_units_in_batch]
        trimmed_player = player_unit_mask[:, :max_units_in_batch]
        trimmed_enemy = enemy_unit_mask[:, :max_units_in_batch]
        trimmed_neutral = neutral_unit_mask[:, :max_units_in_batch]

        return self.critic(self.forward(trimmed_x, trimmed_mask), trimmed_player, trimmed_enemy, trimmed_neutral)

    # TODO this is not correct. Need to fix here an elsewhere
    def network_size(self):
        print(f'Main NN params: {sum([p.numel() for p in self.network.parameters()])}')
        print(f'Trainable params: {sum([p.numel() for p in self.network.parameters() if p.requires_grad])}')
