using SymbolicVault as Vault

methods {    
    //getters for specific distribution
    getStakingToken(bytes32) returns address /*IERC20*/ envfree
    getDistributionToken(bytes32) returns address /*IERC20*/ envfree
    getOwner(bytes32) returns address envfree
    getTotalSupply(bytes32) returns uint256 envfree
    getDuration(bytes32) returns uint256 envfree
    getPeriodFinish(bytes32) returns uint256 envfree
    getPaymentRate(bytes32) returns uint256 envfree    
    getLastUpdateTime(bytes32) returns uint256 envfree
    getGlobalTokensPerStake(bytes32) returns uint256 envfree

    // getters for user staking
    getUserTokensPerStake(bytes32, address, address) returns uint256 envfree
    getUserSubscribedDistributionIdByIndex(address, address, uint256) returns bytes32 envfree
    getUserSubscribedDistributionIndexById(address, address, bytes32) returns uint256 envfree
    getDistIdContainedInUserSubscribedDistribution(address, address, bytes32) returns bool envfree
    getUserBalance(address, address) returns uint256 envfree
    getUserSetLength(address, address) returns uint256 envfree

    // view functions
    isSubscribed(bytes32, address) returns bool envfree
    getDistributionId(address stakingToken, address distributionToken, address owner) returns bytes32 envfree => uniqueHashGhost(stakingToken, distributionToken, owner)


    // non view functions
    createDistribution(address, address, uint256) returns bytes32
    setDistributionDuration(bytes32, uint256)
    fundDistribution(bytes32, uint256)
    subscribeDistributions(bytes32[])
    unsubscribeDistributions(bytes32[]) 
    stake(address, uint256, address, address)
    stakeUsingVault(address, uint256, address, address)
    stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32)
    unstake(address, uint256, address, address)
    claim(bytes32[], bool, address, address)
    claimWithCallback(bytes32[], address, address, bytes)
    exit(address[], bytes32[])
    exitWithCallback(address[], bytes32[], address, bytes)

    // getters for harness
    _lastTimePaymentApplicableHarness(bytes32) returns uint256

    totalAssetsOfUser(address, address) returns uint256 => DISPATCHER(true)
    manageUserBalance((uint8,address,uint256,address,address)[]) => DISPATCHER(true)
    balanceOf(address) returns uint256 => DISPATCHER(true)
    transfer(address, uint256) returns bool => DISPATCHER(true)
    transferFrom(address, address, uint256) returns bool => DISPATCHER(true)
    approve(address, uint256) returns (bool) => DISPATCHER(true)
    
    getUserUnclaimedTokensOfDistribution(bytes32, address, address) returns uint256
    getClaimableTokens(bytes32, address) returns uint256

    distributorCallback(bytes) => NONDET
    permit(address, address, uint256, uint256, uint8, bytes32, bytes32) => NONDET
}

/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////    Definitions    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Dist Not Exist - all parameters are set to default values.
definition distNotExist(bytes32 distId) returns bool = 
        getStakingToken(distId) == 0 &&
        getDistributionToken(distId) == 0 &&
        getOwner(distId) == 0 &&
        getTotalSupply(distId) == 0 &&
        getDuration(distId) == 0 &&
        getPeriodFinish(distId) == 0 &&
        getPaymentRate(distId) == 0 &&
        getLastUpdateTime(distId) == 0 &&
        getGlobalTokensPerStake(distId) == 0;

// Dist Created, but yet to be funded - 4 parameters are non-zero.
definition distNew(bytes32 distId) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 && 
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 && 
        getPeriodFinish(distId) == 0 &&
        getPaymentRate(distId) == 0 && 
        getLastUpdateTime(distId) == 0 && 
        getGlobalTokensPerStake(distId) == 0;

// Dist Funded, hence active - 4 non-zero parameters from distCreated + 4 more.
definition distActive(bytes32 distId, env e) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 &&
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 &&
        (getPeriodFinish(distId) != 0 && getPeriodFinish(distId) >= e.block.timestamp) &&
        // getPaymentRate(distId) != 0 && 
        (getLastUpdateTime(distId) != 0 && getLastUpdateTime(distId) <= getPeriodFinish(distId)); //&&
        // if everybody stake then unstake at some point GTPS, total supply can be 0, yet GTPS != 0
        // if at least 1 user is staked and subscribe then GTPS != 0
        // (getTotalSupply(distId) == 0 ? getGlobalTokensPerStake(distId) == 0 : getGlobalTokensPerStake(distId) != 0);

// Dist Finished, not active - 4 non-zero parameters from distCreated + 4 more.
definition distFinished(bytes32 distId, env e) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 &&
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 &&
        (getPeriodFinish(distId) != 0 && getPeriodFinish(distId) < e.block.timestamp) &&
        // getPaymentRate(distId) != 0 &&
        (getLastUpdateTime(distId) != 0 && getLastUpdateTime(distId) <= getPeriodFinish(distId)); //&& 
        // this is not entierly corret. we should only care for token staked within the active period. This line is commented as globalTPS probably isn't important in this state
        // (getTotalSupply(distId) == 0 ? getGlobalTokensPerStake(distId) == 0 : getGlobalTokensPerStake(distId) != 0);

// Collection of functions that are not distribution specific - they may effect distIds that arent passed to the (mainly by staking/unstaking)
definition nonSpecificDistribution(method f) returns bool = 
    f.selector == stake(address, uint256, address, address).selector || 
    f.selector == stakeUsingVault(address, uint256, address, address).selector || 
    f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector || 
    f.selector == unstake(address, uint256, address, address).selector || 
    f.selector == exit(address[], bytes32[]).selector || 
    f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector;

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Ghost    //////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Ghost that keeps track of the hashing to assume determinism of the hashing operation.
ghost uniqueHashGhost(address, address, address) returns bytes32;


/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Helpers    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Making sure the env does not take any 0 values which aren't realistic anyway
function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

/*
function callCreateDistributionWithSpecificDistId(method f, env e, bytes32 distId){
    address _stakingToken; address _distributionToken; uint256 _duration;
    if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distributionId = createDistribution(e, _stakingToken, _distributionToken, _duration);
        require distributionId == distId;
    } else {
        calldataarg args;
        f(e, args);
    }
}
*/

// Helper function for calling fundDistribution with specifica distId, and all other functions with arbitrary values
function callFundDistributionWithSpecificDistId(method f, env e, bytes32 distId){
    uint256 _amount;
    if (f.selector == fundDistribution(bytes32, uint256).selector) {
        fundDistribution(e, distId, _amount);
    } else {
        calldataarg args;
        f(e, args);
    }
}

// Calling all non-view function with specified parameters.
// A helper function that allows modification of the input args to assure specific values are being passed to the contract's functions when needed
function callAllFunctionsWithParameters(method f, env e, bytes32 distributionId, bytes32[] distributionIds, address stakingToken, address recipient, address[] stakingTokens){
    address distributionToken; uint256 duration; uint256 amount;
    address sender; uint256 deadline; uint8 v; bytes32 r; bytes32 s;
    bool toInternalBalance; address callbackContract; bytes callbackData;

	if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distId = createDistribution(e, stakingToken, distributionToken, duration);
        require distId == distributionId;
	} else if (f.selector == setDistributionDuration(bytes32, uint256).selector) {
        setDistributionDuration(e, distributionId, duration);
	} else if (f.selector == fundDistribution(bytes32, uint256).selector) {
		fundDistribution(e, distributionId, amount);
	} else if (f.selector == subscribeDistributions(bytes32[]).selector) {
        subscribeDistributions(e, distributionIds);
	} else if (f.selector == unsubscribeDistributions(bytes32[]).selector) {
		unsubscribeDistributions(e, distributionIds);
    } else if (f.selector == stake(address, uint256, address, address).selector) {
        stake(e, stakingToken, amount, sender, recipient); 
    } else if (f.selector == stakeUsingVault(address, uint256, address, address).selector) {
        stakeUsingVault(e, stakingToken, amount, sender, recipient);
	} else if (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        stakeWithPermit(e, stakingToken, amount, recipient, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
		unstake(e, stakingToken, amount, sender, recipient);
    } else if (f.selector == claim(bytes32[], bool, address, address).selector) {
        claim(e, distributionIds, toInternalBalance, sender, recipient);
    } else if (f.selector == claimWithCallback(bytes32[], address, address, bytes).selector) {
        claimWithCallback(e, distributionIds, sender, callbackContract,callbackData);
	} else if (f.selector == exit(address[], bytes32[]).selector) {
        exit(e, stakingTokens, distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
		exitWithCallback(e, stakingTokens, distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}

// Assuming the hash is and correlates the trio properly - full paramater set required
function requireDistIdCorrelatedWithTrio(bytes32 distId, address _stakingToken, address _distributionToken, address _owner){
    // given 3 arbitrary args, the hashing function should retrieve the value distId.
    // also the staking token, distribution token and owner associated with this distId must match the arbitrary values.
    require (uniqueHashGhost(_stakingToken, _distributionToken, _owner) == distId && ((getStakingToken(distId) == _stakingToken && getDistributionToken(distId) == _distributionToken && getOwner(distId) == _owner)));
}

// Assuming the hash is deterministic, and correlates the trio properly
function hashUniquness(address stakingToken1, address distributionToken1, address owner1, address stakingToken2, address distributionToken2, address owner2){
    require (((stakingToken1 != stakingToken2) || (distributionToken1 != distributionToken2) || (owner1 != owner2)) <=> 
    (uniqueHashGhost(stakingToken1, distributionToken1, owner1) != uniqueHashGhost(stakingToken2, distributionToken2, owner2)));
}


function integrityHelper(method f, env e, bytes32 distributionId, address user, address distributionToken, address stakingToken){
    uint256 amount; uint256 deadline; uint8 v; 
    bytes32[] distributionIds; 
    bytes32 r; bytes32 s; 
    bytes callbackData; 
    address[] stakingTokens;
    address callbackContract; 
    
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    require stakingTokens.length == 1;
    require stakingTokens[0] == stakingToken;

    uint256 index;
    require index == 0;
    require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  
                && getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;

	if (f.selector == stake(address, uint256, address, address).selector) {
        stake(e, stakingToken, amount, user, user); 
    } else if (f.selector == stakeUsingVault(address, uint256, address, address).selector) {
        stakeUsingVault(e, stakingToken, amount, user, user);
	} else if  (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        stakeWithPermit(e, stakingToken, amount, user, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
		unstake(e, stakingToken, amount, user, user);
    }  else if  (f.selector == exit(address[], bytes32[]).selector) {
        exit(e, stakingTokens, distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
		exitWithCallback(e, stakingTokens, distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}


function solvencyHelper(method f, env e, bytes32 distributionId, address user, address distributionToken, address stakingToken){
    uint256 duration; uint256 amount; uint256 deadline; uint256 index;
    uint8 v; bytes32 r; bytes32 s;
    bytes32[] distributionIds; address[] stakingTokens;
    bool toInternalBalance; address callbackContract; bytes callbackData; 

    require index == 0;

    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    require stakingTokens.length == 1;
    require stakingTokens[0] == stakingToken;

	if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distId = createDistribution(e, stakingToken, distributionToken, duration);
        require distId == distributionId;
	} else if (f.selector == setDistributionDuration(bytes32, uint256).selector) {
        setDistributionDuration(e, distributionId, duration);
	} else if (f.selector == fundDistribution(bytes32, uint256).selector) {
        require e.msg.sender != user;
		fundDistribution(e, distributionId, amount);
	} else if (f.selector == subscribeDistributions(bytes32[]).selector) {
        subscribeDistributions(e, distributionIds);
	} else if (f.selector == unsubscribeDistributions(bytes32[]).selector) {
		unsubscribeDistributions(e, distributionIds);
    } else if (f.selector == stake(address, uint256, address, address).selector) {
        require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        stake(e, stakingToken, amount, user, user); 
    } else if (f.selector == stakeUsingVault(address, uint256, address, address).selector) {
        require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        stakeUsingVault(e, stakingToken, amount, user, user);
	} else if  (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        stakeWithPermit(e, stakingToken, amount, user, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
        require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
		unstake(e, stakingToken, amount, user, user);
    } else if (f.selector == claim(bytes32[], bool, address, address).selector) {
        claim(e, distributionIds, toInternalBalance, user, user);
    } else if (f.selector == claimWithCallback(bytes32[], address, address, bytes).selector) {
        require callbackContract == user;
        claimWithCallback(e, distributionIds, user, callbackContract, callbackData);
	} else if  (f.selector == exit(address[], bytes32[]).selector) {
        require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        exit(e, stakingTokens, distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
        require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        require e.msg.sender == user;
        require callbackContract == user;
		exitWithCallback(e, stakingTokens, distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}