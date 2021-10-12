import Task from '../../src/task';
import { TaskRunOptions } from '../../src/types';
import { LinearPhantomStablePoolDeployment } from './input';

export default async (task: Task, { force, from }: TaskRunOptions = {}): Promise<void> => {
  const input = task.input() as LinearPhantomStablePoolDeployment;
  const args = [input.Vault];

  await task.deployAndVerify('LinearPoolFactory', args, from, force);
  await task.deployAndVerify('StablePhantomPoolFactory', args, from, force);
};
