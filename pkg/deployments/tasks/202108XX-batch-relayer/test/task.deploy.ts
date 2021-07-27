import hre from 'hardhat';
import { expect } from 'chai';

import Task from '../../../src/task';

describe('BatchRelayer', function () {
  const task = Task.fromHRE('202108XX-batch-relayer', hre);

  it('references the vault correctly', async () => {
    const input = task.input();
    const output = task.output();

    const relayer = await task.instanceAt('LidoBatchRelayer', output.relayer);

    expect(await relayer.getVault()).to.be.equal(input.vault);
  });

  it('references the staking contract correctly', async () => {
    const input = task.input();
    const output = task.output();

    const relayer = await task.instanceAt('LidoBatchRelayer', output.relayer);

    expect(await relayer.getStakingContract()).to.be.equal(input.stakingContract);
  });
});
