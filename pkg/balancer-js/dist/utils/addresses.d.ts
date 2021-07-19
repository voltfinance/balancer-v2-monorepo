import { Signer } from '@ethersproject/abstract-signer';
import { Provider } from '@ethersproject/providers';
import { BalancerHelpers, LiquidityBootstrappingPoolFactory, StablePoolFactory, Vault, WeightedPool2TokensFactory, WeightedPoolFactory } from '../typechain';
export declare type BalancerDeployment = {
    authorizer: string;
    weth: string;
    vault: string;
    balancerHelpers: string;
    weightedPoolFactory: string;
    weightedOraclePoolFactory: string;
    lbpPoolFactory: string;
    stablePoolFactory: string;
};
export declare const getBalancerAddresses: (chainId: number) => BalancerDeployment;
export declare class BalancerContracts {
    contractAddresses: BalancerDeployment;
    private provider;
    static fromProvider(provider: Provider): Promise<BalancerContracts>;
    constructor(provider: Signer | Provider, chainId: number);
    getBalancerVault: (provider?: Signer | Provider) => Vault;
    getBalancerHelpers: (provider?: Signer | Provider) => BalancerHelpers;
    getWeightedPoolFactory: (provider?: Signer | Provider) => WeightedPoolFactory;
    getWeightedOraclePoolFactory: (provider?: Signer | Provider) => WeightedPool2TokensFactory;
    getLBPPoolFactory: (provider?: Signer | Provider) => LiquidityBootstrappingPoolFactory;
    getStablePoolFactory: (provider?: Signer | Provider) => StablePoolFactory;
}
