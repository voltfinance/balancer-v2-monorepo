import Task from '../../src/task';
import logger from '../../src/logger';
import { TaskRunOptions } from '../../src/types';
import { BatchRelayerDeployment } from './input';

export default async (task: Task, { force, from }: TaskRunOptions = {}): Promise<void> => {
  const output = task.output({ ensure: false });
  const input = task.input() as BatchRelayerDeployment;
  const args = [input.vault, input.stakingContract];

  if (force || !output.relayer) {
    const relayer = await task.deploy('BatchRelayer', args, from);
    task.save({ relayer });
    await task.verify('BatchRelayer', relayer.address, args);
  } else {
    logger.info(`BatchRelayer already deployed at ${output.relayer}`);
    await task.verify('BatchRelayer', output.relayer, args);
  }
};
