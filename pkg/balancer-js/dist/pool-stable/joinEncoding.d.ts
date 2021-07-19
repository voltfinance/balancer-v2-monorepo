import { BigNumberish } from '@ethersproject/bignumber';
export declare enum StablePoolJoinKind {
    INIT = 0,
    EXACT_TOKENS_IN_FOR_BPT_OUT = 1,
    TOKEN_IN_FOR_EXACT_BPT_OUT = 2
}
export declare type JoinStablePoolInit = {
    kind: StablePoolJoinKind.INIT;
    amountsIn: BigNumberish[];
};
export declare type JoinStablePoolExactTokensInForBPTOut = {
    kind: StablePoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT;
    amountsIn: BigNumberish[];
    minimumBPT: BigNumberish;
};
export declare type JoinStablePoolTokenInForExactBPTOut = {
    kind: StablePoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT;
    bptAmountOut: BigNumberish;
    enterTokenIndex: number;
};
export declare function encodeJoinStablePool(joinData: JoinStablePoolInit | JoinStablePoolExactTokensInForBPTOut | JoinStablePoolTokenInForExactBPTOut): string;
