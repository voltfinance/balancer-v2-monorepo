import { BigNumberish } from '@ethersproject/bignumber';
export declare enum StablePoolExitKind {
    EXACT_BPT_IN_FOR_ONE_TOKEN_OUT = 0,
    EXACT_BPT_IN_FOR_TOKENS_OUT = 1,
    BPT_IN_FOR_EXACT_TOKENS_OUT = 2
}
export declare type ExitStablePoolExactBPTInForOneTokenOut = {
    kind: StablePoolExitKind.EXACT_BPT_IN_FOR_ONE_TOKEN_OUT;
    bptAmountIn: BigNumberish;
    exitTokenIndex: number;
};
export declare type ExitStablePoolExactBPTInForTokensOut = {
    kind: StablePoolExitKind.EXACT_BPT_IN_FOR_TOKENS_OUT;
    bptAmountIn: BigNumberish;
};
export declare type ExitStablePoolBPTInForExactTokensOut = {
    kind: StablePoolExitKind.BPT_IN_FOR_EXACT_TOKENS_OUT;
    amountsOut: BigNumberish[];
    maxBPTAmountIn: BigNumberish;
};
export declare function encodeExitStablePool(exitData: ExitStablePoolExactBPTInForOneTokenOut | ExitStablePoolExactBPTInForTokensOut | ExitStablePoolBPTInForExactTokensOut): string;
