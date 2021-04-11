methods {
    getSwapFee() returns uint256 envfree
    Harness_get_max_swap_fee() returns uint256 envfree
    Harness_get_max_withdraw_fee() returns uint256 envfree
    getFlashLoanFee() returns uint256 envfree
    Harness_get_max_flash_loan_fee() returns uint256 envfree
    Harness_one() returns (uint256) envfree
}

invariant swap_fee_integrity() getSwapFee() <= Harness_get_max_swap_fee()

invariant flash_loan_fee_integrity() getFlashLoanFee() <= Harness_get_max_flash_loan_fee()

invariant fee_integrity() 
    Harness_get_max_swap_fee() < Harness_one() 
    && Harness_get_max_flash_loan_fee() < Harness_one()