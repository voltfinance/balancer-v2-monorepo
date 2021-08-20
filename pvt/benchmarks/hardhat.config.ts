import '@nomiclabs/hardhat-ethers';

import { hardhatBaseConfig } from '@balancer-labs/v2-common';
import { name } from './package.json';

export default {
  solidity: {
    compilers: hardhatBaseConfig.compilers,
    overrides: { ...hardhatBaseConfig.overrides(name) },
  },
  networks: {
    kovan: {
      saveDeployments: true,
      //gas: 8000000,
      //gasPrice: 90000000000,
      url: `https://kovan.infura.io/v3/${process.env.INFURA_KEY}`,
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
    },
    mainnet: {
      saveDeployments: true,
      //gas: 8000000,
      //gasPrice: 90000000000,
      url: `https://mainnet.infura.io/v3/${process.env.INFURA_KEY}`,
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
    },
    polygon: {
      saveDeployments: true,
      gas: 8000000,
      url: `https://polygon-mainnet.infura.io/v3/${process.env.INFURA_KEY}`,
      accounts: {
        mnemonic: process.env.MNEMONIC,
      },
    },
  },
};
