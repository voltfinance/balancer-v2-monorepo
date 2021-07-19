import { Provider } from '@ethersproject/abstract-provider';
import { BigNumber } from '@ethersproject/bignumber';
import { BalancerHelpers, Vault } from '../typechain';
import { BatchSwapStep, ExitPoolRequest, FundManagement, JoinPoolRequest, SingleSwap, SwapKind } from '../types';
export declare class ActionQueryService {
    readonly provider: Provider;
    readonly vault: Vault;
    readonly balancerHelpers: BalancerHelpers;
    static fromProvider(provider: Provider): Promise<ActionQueryService>;
    constructor(provider: Provider, vault: string, balancerHelpers: string);
    querySwap(swap: SingleSwap, funds: FundManagement): Promise<BigNumber>;
    queryBatchSwap(kind: SwapKind, swaps: BatchSwapStep[], assets: string[], funds: FundManagement): Promise<BigNumber[]>;
    queryJoin(poolId: string, sender: string, address: string, request: JoinPoolRequest): Promise<[BigNumber, BigNumber[]] & {
        bptOut: BigNumber;
        amountsIn: BigNumber[];
    }>;
    queryExit(poolId: string, sender: string, address: string, request: ExitPoolRequest): Promise<[BigNumber, BigNumber[]] & {
        bptIn: BigNumber;
        amountsOut: BigNumber[];
    }>;
}
