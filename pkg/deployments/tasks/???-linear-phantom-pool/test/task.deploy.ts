import hre from 'hardhat';
import { expect } from 'chai';

import Task from '../../../src/task';

describe('LinearPoolFactory', function () {
  const task = Task.fromHRE('???-linear-phantom-pool', hre);

  it('has a vault reference', async () => {
    const input = task.input();

    const factory = await task.deployedInstance('LinearPoolFactory');

    expect(await factory.getVault()).to.be.equal(input.Vault);
  });
});

describe('StablePhantomPoolFactory', function () {
  const task = Task.fromHRE('???-linear-phantom-pool', hre);

  it('has a vault reference', async () => {
    const input = task.input();

    const factory = await task.deployedInstance('StablePhantomPoolFactory');

    expect(await factory.getVault()).to.be.equal(input.Vault);
  });
});
