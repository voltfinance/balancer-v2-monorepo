(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('@ethersproject/abi'), require('@ethersproject/constants'), require('@ethersproject/bignumber'), require('@ethersproject/bytes'), require('@ethersproject/abstract-signer')) :
    typeof define === 'function' && define.amd ? define(['exports', '@ethersproject/abi', '@ethersproject/constants', '@ethersproject/bignumber', '@ethersproject/bytes', '@ethersproject/abstract-signer'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global['balancer-js'] = {}, global.abi, global.constants, global.bignumber, global.bytes, global.abstractSigner));
}(this, (function (exports, abi, constants, bignumber, bytes, abstractSigner) { 'use strict';

    exports.StablePoolJoinKind = void 0;
    (function (StablePoolJoinKind) {
        StablePoolJoinKind[StablePoolJoinKind["INIT"] = 0] = "INIT";
        StablePoolJoinKind[StablePoolJoinKind["EXACT_TOKENS_IN_FOR_BPT_OUT"] = 1] = "EXACT_TOKENS_IN_FOR_BPT_OUT";
        StablePoolJoinKind[StablePoolJoinKind["TOKEN_IN_FOR_EXACT_BPT_OUT"] = 2] = "TOKEN_IN_FOR_EXACT_BPT_OUT";
    })(exports.StablePoolJoinKind || (exports.StablePoolJoinKind = {}));
    exports.StablePoolExitKind = void 0;
    (function (StablePoolExitKind) {
        StablePoolExitKind[StablePoolExitKind["EXACT_BPT_IN_FOR_ONE_TOKEN_OUT"] = 0] = "EXACT_BPT_IN_FOR_ONE_TOKEN_OUT";
        StablePoolExitKind[StablePoolExitKind["EXACT_BPT_IN_FOR_TOKENS_OUT"] = 1] = "EXACT_BPT_IN_FOR_TOKENS_OUT";
        StablePoolExitKind[StablePoolExitKind["BPT_IN_FOR_EXACT_TOKENS_OUT"] = 2] = "BPT_IN_FOR_EXACT_TOKENS_OUT";
    })(exports.StablePoolExitKind || (exports.StablePoolExitKind = {}));
    class StablePoolEncoder {
        /**
         * Cannot be constructed.
         */
        constructor() {
            // eslint-disable-next-line @typescript-eslint/no-empty-function
        }
    }
    /**
     * Encodes the userData parameter for providing the initial liquidity to a StablePool
     * @param initialBalances - the amounts of tokens to send to the pool to form the initial balances
     */
    StablePoolEncoder.joinInit = (amountsIn) => abi.defaultAbiCoder.encode(['uint256', 'uint256[]'], [exports.StablePoolJoinKind.INIT, amountsIn]);
    /**
     * Encodes the userData parameter for joining a StablePool with exact token inputs
     * @param amountsIn - the amounts each of token to deposit in the pool as liquidity
     * @param minimumBPT - the minimum acceptable BPT to receive in return for deposited tokens
     */
    StablePoolEncoder.joinExactTokensInForBPTOut = (amountsIn, minimumBPT) => abi.defaultAbiCoder.encode(['uint256', 'uint256[]', 'uint256'], [exports.StablePoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT, amountsIn, minimumBPT]);
    /**
     * Encodes the userData parameter for joining a StablePool with to receive an exact amount of BPT
     * @param bptAmountOut - the amount of BPT to be minted
     * @param enterTokenIndex - the index of the token to be provided as liquidity
     */
    StablePoolEncoder.joinTokenInForExactBPTOut = (bptAmountOut, enterTokenIndex) => abi.defaultAbiCoder.encode(['uint256', 'uint256', 'uint256'], [exports.StablePoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT, bptAmountOut, enterTokenIndex]);
    /**
     * Encodes the userData parameter for exiting a StablePool by removing a single token in return for an exact amount of BPT
     * @param bptAmountIn - the amount of BPT to be burned
     * @param enterTokenIndex - the index of the token to removed from the pool
     */
    StablePoolEncoder.exitExactBPTInForOneTokenOut = (bptAmountIn, exitTokenIndex) => abi.defaultAbiCoder.encode(['uint256', 'uint256', 'uint256'], [exports.StablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT, bptAmountIn, exitTokenIndex]);
    /**
     * Encodes the userData parameter for exiting a StablePool by removing tokens in return for an exact amount of BPT
     * @param bptAmountIn - the amount of BPT to be burned
     */
    StablePoolEncoder.exitExactBPTInForTokensOut = (bptAmountIn) => abi.defaultAbiCoder.encode(['uint256', 'uint256'], [exports.StablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT, bptAmountIn]);
    /**
     * Encodes the userData parameter for exiting a StablePool by removing exact amounts of tokens
     * @param amountsOut - the amounts of each token to be withdrawn from the pool
     * @param maxBPTAmountIn - the minimum acceptable BPT to burn in return for withdrawn tokens
     */
    StablePoolEncoder.exitBPTInForExactTokensOut = (amountsOut, maxBPTAmountIn) => abi.defaultAbiCoder.encode(['uint256', 'uint256[]', 'uint256'], [exports.StablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT, amountsOut, maxBPTAmountIn]);

    exports.WeightedPoolJoinKind = void 0;
    (function (WeightedPoolJoinKind) {
        WeightedPoolJoinKind[WeightedPoolJoinKind["INIT"] = 0] = "INIT";
        WeightedPoolJoinKind[WeightedPoolJoinKind["EXACT_TOKENS_IN_FOR_BPT_OUT"] = 1] = "EXACT_TOKENS_IN_FOR_BPT_OUT";
        WeightedPoolJoinKind[WeightedPoolJoinKind["TOKEN_IN_FOR_EXACT_BPT_OUT"] = 2] = "TOKEN_IN_FOR_EXACT_BPT_OUT";
    })(exports.WeightedPoolJoinKind || (exports.WeightedPoolJoinKind = {}));
    exports.WeightedPoolExitKind = void 0;
    (function (WeightedPoolExitKind) {
        WeightedPoolExitKind[WeightedPoolExitKind["EXACT_BPT_IN_FOR_ONE_TOKEN_OUT"] = 0] = "EXACT_BPT_IN_FOR_ONE_TOKEN_OUT";
        WeightedPoolExitKind[WeightedPoolExitKind["EXACT_BPT_IN_FOR_TOKENS_OUT"] = 1] = "EXACT_BPT_IN_FOR_TOKENS_OUT";
        WeightedPoolExitKind[WeightedPoolExitKind["BPT_IN_FOR_EXACT_TOKENS_OUT"] = 2] = "BPT_IN_FOR_EXACT_TOKENS_OUT";
    })(exports.WeightedPoolExitKind || (exports.WeightedPoolExitKind = {}));
    class WeightedPoolEncoder {
        /**
         * Cannot be constructed.
         */
        constructor() {
            // eslint-disable-next-line @typescript-eslint/no-empty-function
        }
    }
    /**
     * Encodes the userData parameter for providing the initial liquidity to a WeightedPool
     * @param initialBalances - the amounts of tokens to send to the pool to form the initial balances
     */
    WeightedPoolEncoder.joinInit = (amountsIn) => abi.defaultAbiCoder.encode(['uint256', 'uint256[]'], [exports.WeightedPoolJoinKind.INIT, amountsIn]);
    /**
     * Encodes the userData parameter for joining a WeightedPool with exact token inputs
     * @param amountsIn - the amounts each of token to deposit in the pool as liquidity
     * @param minimumBPT - the minimum acceptable BPT to receive in return for deposited tokens
     */
    WeightedPoolEncoder.joinExactTokensInForBPTOut = (amountsIn, minimumBPT) => abi.defaultAbiCoder.encode(['uint256', 'uint256[]', 'uint256'], [exports.WeightedPoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT, amountsIn, minimumBPT]);
    /**
     * Encodes the userData parameter for joining a WeightedPool with to receive an exact amount of BPT
     * @param bptAmountOut - the amount of BPT to be minted
     * @param enterTokenIndex - the index of the token to be provided as liquidity
     */
    WeightedPoolEncoder.joinTokenInForExactBPTOut = (bptAmountOut, enterTokenIndex) => abi.defaultAbiCoder.encode(['uint256', 'uint256', 'uint256'], [exports.WeightedPoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT, bptAmountOut, enterTokenIndex]);
    /**
     * Encodes the userData parameter for exiting a WeightedPool by removing a single token in return for an exact amount of BPT
     * @param bptAmountIn - the amount of BPT to be burned
     * @param enterTokenIndex - the index of the token to removed from the pool
     */
    WeightedPoolEncoder.exitExactBPTInForOneTokenOut = (bptAmountIn, exitTokenIndex) => abi.defaultAbiCoder.encode(['uint256', 'uint256', 'uint256'], [exports.WeightedPoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT, bptAmountIn, exitTokenIndex]);
    /**
     * Encodes the userData parameter for exiting a WeightedPool by removing tokens in return for an exact amount of BPT
     * @param bptAmountIn - the amount of BPT to be burned
     */
    WeightedPoolEncoder.exitExactBPTInForTokensOut = (bptAmountIn) => abi.defaultAbiCoder.encode(['uint256', 'uint256'], [exports.WeightedPoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT, bptAmountIn]);
    /**
     * Encodes the userData parameter for exiting a WeightedPool by removing exact amounts of tokens
     * @param amountsOut - the amounts of each token to be withdrawn from the pool
     * @param maxBPTAmountIn - the minimum acceptable BPT to burn in return for withdrawn tokens
     */
    WeightedPoolEncoder.exitBPTInForExactTokensOut = (amountsOut, maxBPTAmountIn) => abi.defaultAbiCoder.encode(['uint256', 'uint256[]', 'uint256'], [exports.WeightedPoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT, amountsOut, maxBPTAmountIn]);

    /**
     * Normalize an array of token weights to ensure they sum to `1e18`
     * @param weights - an array of token weights to be normalized
     * @returns an equivalent set of normalized weights
     */
    function toNormalizedWeights(weights) {
        const sum = weights.reduce((total, weight) => total.add(weight), constants.Zero);
        if (sum.eq(constants.WeiPerEther))
            return weights;
        const normalizedWeights = [];
        let normalizedSum = constants.Zero;
        for (let index = 0; index < weights.length; index++) {
            if (index < weights.length - 1) {
                normalizedWeights[index] = weights[index].mul(constants.WeiPerEther).div(sum);
                normalizedSum = normalizedSum.add(normalizedWeights[index]);
            }
            else {
                normalizedWeights[index] = constants.WeiPerEther.sub(normalizedSum);
            }
        }
        return normalizedWeights;
    }
    /**
     * Check whether a set of weights are normalized
     * @param weights - an array of potentially unnormalized weights
     * @returns a boolean of whether the weights are normalized
     */
    const isNormalizedWeights = (weights) => {
        const totalWeight = weights.reduce((total, weight) => total.add(weight), constants.Zero);
        return totalWeight.eq(constants.WeiPerEther);
    };

    var isProduction = process.env.NODE_ENV === 'production';
    var prefix = 'Invariant failed';
    function invariant(condition, message) {
        if (condition) {
            return;
        }
        if (isProduction) {
            throw new Error(prefix);
        }
        throw new Error(prefix + ": " + (message || ''));
    }

    /**
     * Splits a poolId into its components, i.e. pool address, pool specialization and its nonce
     * @param poolId - a bytes32 string of the pool's ID
     * @returns an object with the decomposed poolId
     */
    const splitPoolId = (poolId) => {
        return {
            address: getPoolAddress(poolId),
            specialization: getPoolSpecialization(poolId),
            nonce: getPoolNonce(poolId),
        };
    };
    /**
     * Extracts a pool's address from its poolId
     * @param poolId - a bytes32 string of the pool's ID
     * @returns the pool's address
     */
    const getPoolAddress = (poolId) => {
        invariant(poolId.length === 66, 'Invalid poolId length');
        return poolId.slice(0, 42);
    };
    /**
     * Extracts a pool's specialization from its poolId
     * @param poolId - a bytes32 string of the pool's ID
     * @returns the pool's specialization
     */
    const getPoolSpecialization = (poolId) => {
        invariant(poolId.length === 66, 'Invalid poolId length');
        // Only have 3 pool specializations so we can just pull the relevant character
        const specializationCode = parseInt(poolId[45]);
        invariant(specializationCode < 3, 'Invalid pool specialization');
        return specializationCode;
    };
    /**
     * Extracts a pool's nonce from its poolId
     * @param poolId - a bytes32 string of the pool's ID
     * @returns the pool's nonce
     */
    const getPoolNonce = (poolId) => {
        invariant(poolId.length === 66, 'Invalid poolId length');
        return bignumber.BigNumber.from(`0x${poolId.slice(46)}`);
    };

    const balancerErrorCodes = {
        '000': 'ADD_OVERFLOW',
        '001': 'SUB_OVERFLOW',
        '002': 'SUB_UNDERFLOW',
        '003': 'MUL_OVERFLOW',
        '004': 'ZERO_DIVISION',
        '005': 'DIV_INTERNAL',
        '006': 'X_OUT_OF_BOUNDS',
        '007': 'Y_OUT_OF_BOUNDS',
        '008': 'PRODUCT_OUT_OF_BOUNDS',
        '009': 'INVALID_EXPONENT',
        '100': 'OUT_OF_BOUNDS',
        '101': 'UNSORTED_ARRAY',
        '102': 'UNSORTED_TOKENS',
        '103': 'INPUT_LENGTH_MISMATCH',
        '104': 'ZERO_TOKEN',
        '200': 'MIN_TOKENS',
        '201': 'MAX_TOKENS',
        '202': 'MAX_SWAP_FEE_PERCENTAGE',
        '203': 'MIN_SWAP_FEE_PERCENTAGE',
        '204': 'MINIMUM_BPT',
        '205': 'CALLER_NOT_VAULT',
        '206': 'UNINITIALIZED',
        '207': 'BPT_IN_MAX_AMOUNT',
        '208': 'BPT_OUT_MIN_AMOUNT',
        '209': 'EXPIRED_PERMIT',
        '210': 'NOT_TWO_TOKENS',
        '300': 'MIN_AMP',
        '301': 'MAX_AMP',
        '302': 'MIN_WEIGHT',
        '303': 'MAX_STABLE_TOKENS',
        '304': 'MAX_IN_RATIO',
        '305': 'MAX_OUT_RATIO',
        '306': 'MIN_BPT_IN_FOR_TOKEN_OUT',
        '307': 'MAX_OUT_BPT_FOR_TOKEN_IN',
        '308': 'NORMALIZED_WEIGHT_INVARIANT',
        '309': 'INVALID_TOKEN',
        '310': 'UNHANDLED_JOIN_KIND',
        '311': 'ZERO_INVARIANT',
        '312': 'ORACLE_INVALID_SECONDS_QUERY',
        '313': 'ORACLE_NOT_INITIALIZED',
        '314': 'ORACLE_QUERY_TOO_OLD',
        '315': 'ORACLE_INVALID_INDEX',
        '316': 'ORACLE_BAD_SECS',
        '317': 'AMP_END_TIME_TOO_CLOSE',
        '318': 'AMP_ONGOING_UPDATE',
        '319': 'AMP_RATE_TOO_HIGH',
        '320': 'AMP_NO_ONGOING_UPDATE',
        '321': 'STABLE_INVARIANT_DIDNT_CONVERGE',
        '322': 'STABLE_GET_BALANCE_DIDNT_CONVERGE',
        '323': 'RELAYER_NOT_CONTRACT',
        '324': 'BASE_POOL_RELAYER_NOT_CALLED',
        '325': 'REBALANCING_RELAYER_REENTERED',
        '326': 'GRADUAL_UPDATE_TIME_TRAVEL',
        '327': 'SWAPS_DISABLED',
        '328': 'CALLER_IS_NOT_LBP_OWNER',
        '329': 'PRICE_RATE_OVERFLOW',
        '400': 'REENTRANCY',
        '401': 'SENDER_NOT_ALLOWED',
        '402': 'PAUSED',
        '403': 'PAUSE_WINDOW_EXPIRED',
        '404': 'MAX_PAUSE_WINDOW_DURATION',
        '405': 'MAX_BUFFER_PERIOD_DURATION',
        '406': 'INSUFFICIENT_BALANCE',
        '407': 'INSUFFICIENT_ALLOWANCE',
        '408': 'ERC20_TRANSFER_FROM_ZERO_ADDRESS',
        '409': 'ERC20_TRANSFER_TO_ZERO_ADDRESS',
        '410': 'ERC20_MINT_TO_ZERO_ADDRESS',
        '411': 'ERC20_BURN_FROM_ZERO_ADDRESS',
        '412': 'ERC20_APPROVE_FROM_ZERO_ADDRESS',
        '413': 'ERC20_APPROVE_TO_ZERO_ADDRESS',
        '414': 'ERC20_TRANSFER_EXCEEDS_ALLOWANCE',
        '415': 'ERC20_DECREASED_ALLOWANCE_BELOW_ZERO',
        '416': 'ERC20_TRANSFER_EXCEEDS_BALANCE',
        '417': 'ERC20_BURN_EXCEEDS_ALLOWANCE',
        '418': 'SAFE_ERC20_CALL_FAILED',
        '419': 'ADDRESS_INSUFFICIENT_BALANCE',
        '420': 'ADDRESS_CANNOT_SEND_VALUE',
        '421': 'SAFE_CAST_VALUE_CANT_FIT_INT256',
        '422': 'GRANT_SENDER_NOT_ADMIN',
        '423': 'REVOKE_SENDER_NOT_ADMIN',
        '424': 'RENOUNCE_SENDER_NOT_ALLOWED',
        '425': 'BUFFER_PERIOD_EXPIRED',
        '426': 'CALLER_IS_NOT_OWNER',
        '427': 'NEW_OWNER_IS_ZERO',
        '428': 'CODE_DEPLOYMENT_FAILED',
        '500': 'INVALID_POOL_ID',
        '501': 'CALLER_NOT_POOL',
        '502': 'SENDER_NOT_ASSET_MANAGER',
        '503': 'USER_DOESNT_ALLOW_RELAYER',
        '504': 'INVALID_SIGNATURE',
        '505': 'EXIT_BELOW_MIN',
        '506': 'JOIN_ABOVE_MAX',
        '507': 'SWAP_LIMIT',
        '508': 'SWAP_DEADLINE',
        '509': 'CANNOT_SWAP_SAME_TOKEN',
        '510': 'UNKNOWN_AMOUNT_IN_FIRST_SWAP',
        '511': 'MALCONSTRUCTED_MULTIHOP_SWAP',
        '512': 'INTERNAL_BALANCE_OVERFLOW',
        '513': 'INSUFFICIENT_INTERNAL_BALANCE',
        '514': 'INVALID_ETH_INTERNAL_BALANCE',
        '515': 'INVALID_POST_LOAN_BALANCE',
        '516': 'INSUFFICIENT_ETH',
        '517': 'UNALLOCATED_ETH',
        '518': 'ETH_TRANSFER',
        '519': 'CANNOT_USE_ETH_SENTINEL',
        '520': 'TOKENS_MISMATCH',
        '521': 'TOKEN_NOT_REGISTERED',
        '522': 'TOKEN_ALREADY_REGISTERED',
        '523': 'TOKENS_ALREADY_SET',
        '524': 'TOKENS_LENGTH_MUST_BE_2',
        '525': 'NONZERO_TOKEN_BALANCE',
        '526': 'BALANCE_TOTAL_OVERFLOW',
        '527': 'POOL_NO_TOKENS',
        '528': 'INSUFFICIENT_FLASH_LOAN_BALANCE',
        '600': 'SWAP_FEE_PERCENTAGE_TOO_HIGH',
        '601': 'FLASH_LOAN_FEE_PERCENTAGE_TOO_HIGH',
        '602': 'INSUFFICIENT_FLASH_LOAN_FEE_AMOUNT',
    };
    class BalancerErrors {
        /**
         * Cannot be constructed.
         */
        constructor() {
            // eslint-disable-next-line @typescript-eslint/no-empty-function
        }
    }
    BalancerErrors.isErrorCode = (error) => {
        if (!error.includes('BAL#'))
            return false;
        const errorCode = error.replace('BAL#', '');
        return Object.keys(balancerErrorCodes).includes(errorCode);
    };
    /**
     * Decodes a Balancer error code into the corresponding reason
     * @param error - a Balancer error code of the form `BAL#000`
     * @returns The decoded error reason
     */
    BalancerErrors.parseErrorCode = (error) => {
        if (!error.includes('BAL#'))
            throw new Error('Error code not found');
        const errorCode = error.replace('BAL#', '');
        const actualError = balancerErrorCodes[errorCode];
        if (!actualError)
            throw new Error('Error code not found');
        return actualError;
    };
    /**
     * Decodes a Balancer error code into the corresponding reason
     * @param error - a Balancer error code of the form `BAL#000`
     * @returns The decoded error reason if passed a valid error code, otherwise returns passed input
     */
    BalancerErrors.tryParseErrorCode = (error) => {
        try {
            return BalancerErrors.parseErrorCode(error);
        }
        catch {
            return error;
        }
    };
    /**
     * Tests whether a string is a known Balancer error message
     * @param error - a string to be checked verified as a Balancer error message
     */
    BalancerErrors.isBalancerError = (error) => Object.values(balancerErrorCodes).includes(error);
    /**
     * Encodes an error string into the corresponding error code
     * @param error - a Balancer error message string
     * @returns a Balancer error code of the form `BAL#000`
     */
    BalancerErrors.encodeError = (error) => {
        const encodedError = Object.entries(balancerErrorCodes).find(([, message]) => message === error);
        if (!encodedError)
            throw Error('Error message not found');
        return `BAL#${encodedError[0]}`;
    };

    async function accountToAddress(account) {
        if (typeof account == 'string')
            return account;
        if (abstractSigner.Signer.isSigner(account))
            return account.getAddress();
        if (account.address)
            return account.address;
        throw new Error('Could not read account address');
    }
    exports.RelayerAction = void 0;
    (function (RelayerAction) {
        RelayerAction["JoinPool"] = "JoinPool";
        RelayerAction["ExitPool"] = "ExitPool";
        RelayerAction["Swap"] = "Swap";
        RelayerAction["BatchSwap"] = "BatchSwap";
        RelayerAction["SetRelayerApproval"] = "SetRelayerApproval";
    })(exports.RelayerAction || (exports.RelayerAction = {}));
    class RelayerAuthorization {
        /**
         * Cannot be constructed.
         */
        constructor() {
            // eslint-disable-next-line @typescript-eslint/no-empty-function
        }
    }
    RelayerAuthorization.encodeCalldataAuthorization = (calldata, deadline, signature) => {
        const encodedDeadline = bytes.hexZeroPad(bytes.hexValue(deadline), 32).slice(2);
        const { v, r, s } = bytes.splitSignature(signature);
        const encodedV = bytes.hexZeroPad(bytes.hexValue(v), 32).slice(2);
        const encodedR = r.slice(2);
        const encodedS = s.slice(2);
        return `${calldata}${encodedDeadline}${encodedV}${encodedR}${encodedS}`;
    };
    RelayerAuthorization.signJoinAuthorization = (validator, user, allowedSender, allowedCalldata, deadline, nonce) => RelayerAuthorization.signAuthorizationFor(exports.RelayerAction.JoinPool, validator, user, allowedSender, allowedCalldata, deadline, nonce);
    RelayerAuthorization.signExitAuthorization = (validator, user, allowedSender, allowedCalldata, deadline, nonce) => RelayerAuthorization.signAuthorizationFor(exports.RelayerAction.ExitPool, validator, user, allowedSender, allowedCalldata, deadline, nonce);
    RelayerAuthorization.signSwapAuthorization = (validator, user, allowedSender, allowedCalldata, deadline, nonce) => RelayerAuthorization.signAuthorizationFor(exports.RelayerAction.Swap, validator, user, allowedSender, allowedCalldata, deadline, nonce);
    RelayerAuthorization.signBatchSwapAuthorization = (validator, user, allowedSender, allowedCalldata, deadline, nonce) => RelayerAuthorization.signAuthorizationFor(exports.RelayerAction.BatchSwap, validator, user, allowedSender, allowedCalldata, deadline, nonce);
    RelayerAuthorization.signSetRelayerApprovalAuthorization = (validator, user, allowedSender, allowedCalldata, deadline, nonce) => RelayerAuthorization.signAuthorizationFor(exports.RelayerAction.SetRelayerApproval, validator, user, allowedSender, allowedCalldata, deadline, nonce);
    RelayerAuthorization.signAuthorizationFor = async (type, validator, user, allowedSender, allowedCalldata, deadline = constants.MaxUint256, nonce) => {
        const { chainId } = await validator.provider.getNetwork();
        if (!nonce) {
            const userAddress = await user.getAddress();
            nonce = (await validator.getNextNonce(userAddress));
        }
        const domain = {
            name: 'Balancer V2 Vault',
            version: '1',
            chainId,
            verifyingContract: validator.address,
        };
        const types = {
            [type]: [
                { name: 'calldata', type: 'bytes' },
                { name: 'sender', type: 'address' },
                { name: 'nonce', type: 'uint256' },
                { name: 'deadline', type: 'uint256' },
            ],
        };
        const value = {
            calldata: allowedCalldata,
            sender: await accountToAddress(allowedSender),
            nonce: nonce.toString(),
            deadline: deadline.toString(),
        };
        return user._signTypedData(domain, types, value);
    };

    const signPermit = async (token, owner, spender, amount, deadline = constants.MaxUint256, nonce) => {
        const { chainId } = await token.provider.getNetwork();
        const ownerAddress = await owner.getAddress();
        if (!nonce)
            nonce = (await token.nonces(ownerAddress));
        const domain = {
            name: await token.name(),
            version: '1',
            chainId,
            verifyingContract: token.address,
        };
        const types = {
            Permit: [
                { name: 'owner', type: 'address' },
                { name: 'spender', type: 'address' },
                { name: 'value', type: 'uint256' },
                { name: 'nonce', type: 'uint256' },
                { name: 'deadline', type: 'uint256' },
            ],
        };
        const value = {
            owner: ownerAddress,
            spender: await accountToAddress(spender),
            value: amount,
            nonce,
            deadline,
        };
        const signature = await owner._signTypedData(domain, types, value);
        return { ...bytes.splitSignature(signature), deadline: bignumber.BigNumber.from(deadline), nonce: bignumber.BigNumber.from(nonce) };
    };

    exports.PoolSpecialization = void 0;
    (function (PoolSpecialization) {
        PoolSpecialization[PoolSpecialization["GeneralPool"] = 0] = "GeneralPool";
        PoolSpecialization[PoolSpecialization["MinimalSwapInfoPool"] = 1] = "MinimalSwapInfoPool";
        PoolSpecialization[PoolSpecialization["TwoTokenPool"] = 2] = "TwoTokenPool";
    })(exports.PoolSpecialization || (exports.PoolSpecialization = {}));
    // Swaps
    exports.SwapKind = void 0;
    (function (SwapKind) {
        SwapKind[SwapKind["GivenIn"] = 0] = "GivenIn";
        SwapKind[SwapKind["GivenOut"] = 1] = "GivenOut";
    })(exports.SwapKind || (exports.SwapKind = {}));
    // Balance Operations
    exports.UserBalanceOpKind = void 0;
    (function (UserBalanceOpKind) {
        UserBalanceOpKind[UserBalanceOpKind["DepositInternal"] = 0] = "DepositInternal";
        UserBalanceOpKind[UserBalanceOpKind["WithdrawInternal"] = 1] = "WithdrawInternal";
        UserBalanceOpKind[UserBalanceOpKind["TransferInternal"] = 2] = "TransferInternal";
        UserBalanceOpKind[UserBalanceOpKind["TransferExternal"] = 3] = "TransferExternal";
    })(exports.UserBalanceOpKind || (exports.UserBalanceOpKind = {}));
    exports.PoolBalanceOpKind = void 0;
    (function (PoolBalanceOpKind) {
        PoolBalanceOpKind[PoolBalanceOpKind["Withdraw"] = 0] = "Withdraw";
        PoolBalanceOpKind[PoolBalanceOpKind["Deposit"] = 1] = "Deposit";
        PoolBalanceOpKind[PoolBalanceOpKind["Update"] = 2] = "Update";
    })(exports.PoolBalanceOpKind || (exports.PoolBalanceOpKind = {}));

    exports.BalancerErrors = BalancerErrors;
    exports.RelayerAuthorization = RelayerAuthorization;
    exports.StablePoolEncoder = StablePoolEncoder;
    exports.WeightedPoolEncoder = WeightedPoolEncoder;
    exports.accountToAddress = accountToAddress;
    exports.getPoolAddress = getPoolAddress;
    exports.getPoolNonce = getPoolNonce;
    exports.getPoolSpecialization = getPoolSpecialization;
    exports.isNormalizedWeights = isNormalizedWeights;
    exports.signPermit = signPermit;
    exports.splitPoolId = splitPoolId;
    exports.toNormalizedWeights = toNormalizedWeights;

    Object.defineProperty(exports, '__esModule', { value: true });

})));
//# sourceMappingURL=index.umd.js.map
