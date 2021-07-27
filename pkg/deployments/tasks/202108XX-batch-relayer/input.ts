import Task from '../../src/task';

export type BatchRelayerDeployment = {
  vault: string;
  stakingContract: string;
};

const vault = new Task('20210418-vault');

// TODO: replace with canonical staking contract
const stakingContract = '0x0000000000000000000000000000000000000000';

export default {
  vault,
  stakingContract,
};
