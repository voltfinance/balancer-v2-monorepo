import { BigNumberish } from '@ethersproject/bignumber';
export declare enum WeightedPoolExitKind {
    EXACT_BPT_IN_FOR_ONE_TOKEN_OUT = 0,
    EXACT_BPT_IN_FOR_TOKENS_OUT = 1,
    BPT_IN_FOR_EXACT_TOKENS_OUT = 2
}
export declare type ExitWeightedPoolExactBPTInForOneTokenOut = {
    kind: WeightedPoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT;
    bptAmountIn: BigNumberish;
    exitTokenIndex: number;
};
export declare type ExitWeightedPoolExactBPTInForTokensOut = {
    kind: WeightedPoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT;
    bptAmountIn: BigNumberish;
};
export declare type ExitWeightedPoolBPTInForExactTokensOut = {
    kind: WeightedPoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT;
    amountsOut: BigNumberish[];
    maxBPTAmountIn: BigNumberish;
};
export declare function encodeExitWeightedPool(exitData: ExitWeightedPoolExactBPTInForOneTokenOut | ExitWeightedPoolExactBPTInForTokensOut | ExitWeightedPoolBPTInForExactTokensOut): string;
