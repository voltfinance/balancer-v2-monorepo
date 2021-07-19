import { BigNumberish } from '@ethersproject/bignumber';
export declare enum WeightedPoolJoinKind {
    INIT = 0,
    EXACT_TOKENS_IN_FOR_BPT_OUT = 1,
    TOKEN_IN_FOR_EXACT_BPT_OUT = 2
}
export declare type JoinWeightedPoolInit = {
    kind: WeightedPoolJoinKind.INIT;
    amountsIn: BigNumberish[];
};
export declare type JoinWeightedPoolExactTokensInForBPTOut = {
    kind: WeightedPoolJoinKind.EXACT_TOKENS_IN_FOR_BPT_OUT;
    amountsIn: BigNumberish[];
    minimumBPT: BigNumberish;
};
export declare type JoinWeightedPoolTokenInForExactBPTOut = {
    kind: WeightedPoolJoinKind.TOKEN_IN_FOR_EXACT_BPT_OUT;
    bptAmountOut: BigNumberish;
    enterTokenIndex: number;
};
export declare function encodeJoinWeightedPool(joinData: JoinWeightedPoolInit | JoinWeightedPoolExactTokensInForBPTOut | JoinWeightedPoolTokenInForExactBPTOut): string;
