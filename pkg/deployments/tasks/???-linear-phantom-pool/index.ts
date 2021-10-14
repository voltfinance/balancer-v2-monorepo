import Task from '../../src/task';
import { TaskRunOptions } from '../../src/types';
import { LinearPoolPhantomStableDeployment } from './input';

export default async (task: Task, { force, from }: TaskRunOptions = {}): Promise<void> => {
  const input = task.input() as LinearPoolPhantomStableDeployment;

  const waDAIProvider = await task.deployAndVerify('StaticATokenRateProvider', [input.waDAI], from, force);
  const waUSDCProvider = await task.deployAndVerify('StaticATokenRateProvider', [input.waUSDC], from, force);
  const waUSDTProvider = await task.deployAndVerify('StaticATokenRateProvider', [input.waUSDT], from, force);

  const linearPoolFactory = await task.deployAndVerify('LinearPoolFactory', [input.Vault], from, force);
  await linearPoolFactory.create(
    'LINEARA-DAI',
    'LINEARA-DAI',
    input.daiToken,
    input.waDAI,
    input.linearPool.lowerTarget,
    input.linearPool.upperTarget,
    input.linearPool.swapFeePercentage,
    waDAIProvider.address,
    input.linearPool.wrappedTokenRateCacheDuration,
    input.owner
  );
  const linearPoolDai = ''; ///???

  await linearPoolFactory.create(
    'LINEAR-AUSDC',
    'LINEAR-AUSDC',
    input.usdcToken,
    input.waUSDC,
    input.linearPool.lowerTarget,
    input.linearPool.upperTarget,
    input.linearPool.swapFeePercentage,
    waUSDCProvider.address,
    input.linearPool.wrappedTokenRateCacheDuration,
    input.owner
  );
  const linearPoolUsdc = ''; ///???

  await linearPoolFactory.create(
    'LINEAR-AUSDT',
    'LINEAR-AUSDT',
    input.usdtToken,
    input.waUSDT,
    input.linearPool.lowerTarget,
    input.linearPool.upperTarget,
    input.linearPool.swapFeePercentage,
    waUSDTProvider.address,
    input.linearPool.wrappedTokenRateCacheDuration,
    input.owner
  );
  const linearPoolUsdt = ''; ///???

  const stablePhantomPoolFactory = await task.deployAndVerify('StablePhantomPoolFactory', [input.Vault], from, force);
  await stablePhantomPoolFactory.create(
    'STABAL3',
    'STABAL3',
    [linearPoolDai, linearPoolUsdc, linearPoolUsdt],
    input.stablePhantomPool.amplificationParameter,
    [linearPoolDai, linearPoolUsdc, linearPoolUsdt],
    [0, 0, 0],
    input.stablePhantomPool.swapFeePercentage,
    input.owner
  );
};
