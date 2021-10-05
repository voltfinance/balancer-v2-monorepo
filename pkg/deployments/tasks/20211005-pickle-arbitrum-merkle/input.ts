import Task from '../../src/task';

export type MerkleRedeemDeployment = {
  Vault: string;
  rewardToken: string;
};

const Vault = new Task('20210418-vault');

export default {
  arbitrum: {
    Vault,
    rewardToken: '0x965772e0e9c84b6f359c8597c891108dcf1c5b1a',
  },
};
