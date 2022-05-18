import { ethers } from 'hardhat';
import { expect } from 'chai';
import { BigNumber, ContractReceipt } from 'ethers';
import { SignerWithAddress } from '@nomiclabs/hardhat-ethers/dist/src/signer-with-address';
import { actionId } from '@balancer-labs/v2-helpers/src/models/misc/actions';
import { BigNumberish, fp, bn, fromFp, scaleDown } from '@balancer-labs/v2-helpers/src/numbers';
import { MAX_INT22, MAX_UINT10, MAX_UINT31, MIN_INT22 } from '@balancer-labs/v2-helpers/src/constants';
import { MINUTE, advanceTime, currentTimestamp, lastBlockNumber } from '@balancer-labs/v2-helpers/src/time';

import TokenList from '@balancer-labs/v2-helpers/src/models/tokens/TokenList';
import WeightedPool from '@balancer-labs/v2-helpers/src/models/pools/weighted/WeightedPool';
import { Sample, WeightedPoolType } from '@balancer-labs/v2-helpers/src/models/pools/weighted/types';

import { itBehavesAsWeightedPool } from './BaseWeightedPool.behavior';
import { itPaysProtocolFeesFromInvariantGrowth } from './InvariantYieldGrowthProtocolFees.behavior';

describe('SustainableWeightedPool', function () {
  let trader: SignerWithAddress,
    admin: SignerWithAddress,
    other: SignerWithAddress,
    lp: SignerWithAddress,
    owner: SignerWithAddress;

  before('setup signers', async () => {
    [, lp, trader, other, owner, admin] = await ethers.getSigners();
  });

  let tokens: TokenList;

  sharedBeforeEach('deploy tokens', async () => {
    // Setting varyDecimals to true will create one with 18 and one with 17 decimals
    tokens = await TokenList.create(['MKR', 'DAI'], { sorted: true, varyDecimals: true });
    // mintScaled will compute the correct scaled initial balance, from a raw number of tokens
    await tokens.mintScaled({ to: [lp, trader], amount: 100 });
  });

  let pool: WeightedPool;
  let scalingFactors: BigNumber[];
  let initialBalances: BigNumber[];
  const weights = [fp(30), fp(70)];
  const rawInitialBalances = [fp(0.9), fp(1.8)];

  sharedBeforeEach('deploy pool', async () => {
    let rateProviders: string[] = new Array(tokens.addresses.length).fill(ZERO_ADDRESS)
    let tokenRateCacheDurations = new Array(tokens.addresses.length).fill(1)
    const params = { poolType: WeightedPoolType.SUSTAINABLE_WEIGHTED_POOL, tokens, weights, rateProviders, tokenRateCacheDurations };
    pool = await WeightedPool.create(params);
    // Get the scaling factors from the pool, so that we can adjust incoming balances
    // The WeightedPool.ts computation methods expect all tokens to be 18 decimals, like the Vault
    scalingFactors = await pool.getScalingFactors();
    scalingFactors = scalingFactors.map((f) => bn(fromFp(f)));

    initialBalances = rawInitialBalances.map((b, i) => scaleDown(b, scalingFactors[i]));
  });

  describe('weights', () => {
    it('sets token weights', async () => {
      const normalizedWeights = await pool.getNormalizedWeights();

      expect(normalizedWeights).to.equalWithError(pool.normalizedWeights, 0.0000001);
    });
  });

  describe('yields', () => {
    it('scales invariant as rate provider increases', async () => {

    })
  })
});
