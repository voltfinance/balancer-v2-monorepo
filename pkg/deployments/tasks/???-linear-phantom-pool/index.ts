import * as expectEvent from '@balancer-labs/v2-helpers/src/test/expectEvent';

import Task from '../../src/task';
import { TaskRunOptions } from '../../src/types';
import { LinearPoolPhantomStableDeployment } from './input';

export default async (task: Task, { force, from }: TaskRunOptions = {}): Promise<void> => {
  let receipt, event, name;

  const input = task.input() as LinearPoolPhantomStableDeployment;

  const waDAIProvider = await task.deployAndVerify('StaticATokenRateProvider', [input.waDAI], from, force);
  const waUSDCProvider = await task.deployAndVerify('StaticATokenRateProvider', [input.waUSDC], from, force);
  const waUSDTProvider = await task.deployAndVerify('StaticATokenRateProvider', [input.waUSDT], from, force);

  const linearPoolFactory = await task.deployAndVerify('LinearPoolFactory', [input.Vault], from, force);
  name = 'LINEAR-ADAI';
  receipt = await linearPoolFactory.create(
    name,
    name,
    input.daiToken,
    input.waDAI,
    input.linearPool.lowerTarget,
    input.linearPool.upperTarget,
    input.linearPool.swapFeePercentage,
    waDAIProvider.address,
    input.linearPool.wrappedTokenRateCacheDuration,
    input.owner
  );
  event = expectEvent.inReceipt(await receipt.wait(), 'PoolCreated');
  const linearPoolDai = event.args.pool;
  console.log(`${name} deployed at ${linearPoolDai}`);

  name = 'LINEAR-AUSDC';
  receipt = await linearPoolFactory.create(
    name,
    name,
    input.usdcToken,
    input.waUSDC,
    input.linearPool.lowerTarget,
    input.linearPool.upperTarget,
    input.linearPool.swapFeePercentage,
    waUSDCProvider.address,
    input.linearPool.wrappedTokenRateCacheDuration,
    input.owner
  );
  event = expectEvent.inReceipt(await receipt.wait(), 'PoolCreated');
  const linearPoolUsdc = event.args.pool;
  console.log(`${name} deployed at ${linearPoolUsdc}`);

  name = 'LINEAR-AUSDT';
  receipt = await linearPoolFactory.create(
    name,
    name,
    input.usdtToken,
    input.waUSDT,
    input.linearPool.lowerTarget,
    input.linearPool.upperTarget,
    input.linearPool.swapFeePercentage,
    waUSDTProvider.address,
    input.linearPool.wrappedTokenRateCacheDuration,
    input.owner
  );
  event = expectEvent.inReceipt(await receipt.wait(), 'PoolCreated');
  const linearPoolUsdt = event.args.pool;
  console.log(`${name} deployed at ${linearPoolUsdt}`);

  const stablePhantomPoolFactory = await task.deployAndVerify('StablePhantomPoolFactory', [input.Vault], from, force);
  name = 'STABAL3';
  receipt = await stablePhantomPoolFactory.create(
    name,
    name,
    [linearPoolDai, linearPoolUsdc, linearPoolUsdt],
    input.stablePhantomPool.amplificationParameter,
    [linearPoolDai, linearPoolUsdc, linearPoolUsdt],
    [0, 0, 0],
    input.stablePhantomPool.swapFeePercentage,
    input.owner
  );
  event = expectEvent.inReceipt(await receipt.wait(), 'PoolCreated');
  console.log(`${name} deployed at ${event.args.pool}`);
};
