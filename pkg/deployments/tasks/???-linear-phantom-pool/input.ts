import Task from '../../src/task';
import { BigNumber } from 'ethers';
import { fp } from '@balancer-labs/v2-helpers/src/numbers';
import { StringifyOptions } from 'querystring';

const Vault = new Task('20210418-vault');

export type LinearPoolPhantomStableDeployment = {
  Vault: string;
  daiToken: string;
  usdcToken: string;
  usdtToken: string;
  waDAI: string;
  waUSDC: string;
  waUSDT: string;
  linearPool: {
    lowerTarget: BigNumber;
    upperTarget: BigNumber;
    swapFeePercentage: BigNumber;
    wrappedTokenRateCacheDuration: BigNumber;
  };
  stablePhantomPool: {
    amplificationParameter: BigNumber;
    swapFeePercentage: BigNumber;
  };
  owner: string;
};

export default {
  Vault,
  daiToken: '0xFf795577d9AC8bD7D90Ee22b6C1703490b6512FD',
  usdcToken: '0xe22da380ee6B445bb8273C81944ADEB6E8450422',
  usdtToken: '0x13512979ADE267AB5100878E2e0f485B568328a4',
  waDAI: '0x4811A7Bb9061A46753486E5e84B3CD3D668fB596',
  waUSDC: '0x0FbdDC06a4720408a2f5Eb78e62Bc31AC6E2A3c4',
  waUSDT: '0xE8191aACfcdb32260Cda25830Dc6C9342142f310',
  linearPool: {
    lowerTarget: fp(1900000),
    upperTarget: fp(2100000),
    swapFeePercentage: fp(0.0001),
    wrappedTokenRateCacheDuration: 0,
  },
  stablePhantomPool: {
    amplificationParameter: fp(400000),
    swapFeePercentage: fp(0.01),
  },
  owner: '0xac38B8E606A4833e58c44678661Fbc456c18d21f',
};
