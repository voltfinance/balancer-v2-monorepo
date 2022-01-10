type ContractSettings = Record<
  string,
  {
    version: string;
    runs: number;
  }
>;

const contractSettings: ContractSettings = {
  '@balancer-labs/v2-vault/contracts/Vault.sol': {
    version: '0.8.9',
    runs: 1500,
  },
  '@balancer-labs/v2-pool-weighted/contracts/WeightedPool2TokensFactory.sol': {
    version: '0.8.9',
    runs: 200,
  },
  '@balancer-labs/v2-pool-weighted/contracts/LiquidityBootstrappingPoolFactory.sol': {
    version: '0.8.9',
    runs: 200,
  },
  '@balancer-labs/v2-pool-stable/contracts/meta/MetaStablePool.sol': {
    version: '0.8.9',
    runs: 200,
  },
  '@balancer-labs/v2-pool-stable/contracts/meta/MetaStablePoolFactory.sol': {
    version: '0.8.9',
    runs: 200,
  },
};

type SolcConfig = {
  version: string;
  settings: {
    optimizer: {
      enabled: boolean;
      runs?: number;
    };
  };
};

type NetworkConfig = {
  allowUnlimitedContractSize?: boolean;
  initialBaseFeePerGas?: number;
};

type NetworksConfig = {
  hardhat: NetworkConfig;
};

export const compilers: [SolcConfig] = [
  {
    version: '0.8.9',
    settings: {
      optimizer: {
        enabled: false,
        runs: 200,
      },
    },
  },
];

export const networks: NetworksConfig = {
  hardhat: {
    allowUnlimitedContractSize: true,
    initialBaseFeePerGas: 0,
  },
};

export const overrides = (packageName: string): Record<string, SolcConfig> => {
  const overrides: Record<string, SolcConfig> = {};

  for (const contract of Object.keys(contractSettings)) {
    overrides[contract.replace(`${packageName}/`, '')] = {
      version: contractSettings[contract].version,
      settings: {
        optimizer: {
          enabled: false,
          runs: contractSettings[contract].runs,
        },
      },
    };
  }

  return overrides;
};
