import "multiDistributorPreset.spec"
import "multiDistributorInvs.spec"

/////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////   Invariants usage    ///////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

use invariant distExistInitializedParams
use invariant enumerableSetIsCorrelated
use invariant _userStakingMappingAndSetAreCorrelated
use invariant notSubscribedToNonExistingDistSet
use invariant oneStateAtATime
use invariant gtpsGreaterOrEqualUtps
use invariant lastUpdateTimeNotInFuture
use invariant getLastUpdateTimeLessThanFinish
use invariant userSubStakeCorrelationWithTotalSupply

/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Rules    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// V@V - Creating a dist bringing us from the state distNotExist to distNew (no other function does that). All other functions will leave us in distNotExist state.
// @note that we dont check createDistribution for a distribution_ID != distributionId, counting on another rule, distributionsAreIndependent, that proved any operation on other dists will not effect the one at hand.
rule transition_NotExist_To_DistNew(bytes32 distributionId) {
    method f; env e; calldataarg args; bytes32[] distributionIdsArray; address[] stakingTokensArray;

    require distNotExist(distributionId);
    requireEnvValuesNotZero(e);
    
    address stakingToken; address user; uint256 index; address distributionToken;
    requireDistIdCorrelatedWithTrio(distributionId, stakingToken, distributionToken, user);
    requireInvariant distExistInitializedParams(distributionId, e);
    require index == 0;
    require getUserSetLength(stakingToken, user) == 1;
    require stakingTokensArray.length == 1 && stakingTokensArray[0] == stakingToken;
    require distributionIdsArray.length == 1 && distributionIdsArray[0] == distributionId;
    requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distributionId);
    requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken, user);
    requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);

    // calling all functions, making sure the created distribution id is the distributionId of interest
    callAllFunctionsWithParameters(f, e, distributionId, distributionIdsArray, stakingToken, user, stakingTokensArray);
    assert f.selector != createDistribution(address, address, uint256).selector => distNotExist(distributionId), "distribution changed state without creating a distribution";
    assert f.selector == createDistribution(address, address, uint256).selector => distNew(distributionId), "distribution did not change due to call to createDistribution function";
}


// V@V - Funding a dist bringing us from the state distNew to distActive (no other function does that). All other functions will leave us in distNew state.
rule transition_DistNew_To_DistActive(bytes32 distributionId){
    method f; env e; calldataarg args;
    require distNew(distributionId);
    requireEnvValuesNotZero(e);
    
    callFundDistributionWithSpecificDistId(f, e, distributionId);
    assert f.selector != fundDistribution(bytes32, uint256).selector <=> distNew(distributionId), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector <=> distActive(distributionId, e), "distribution did not change due to call to fundDistribution function";
}


// V@V - All function calls will leave us in distActive state. only time can change a dist state to finished.
// @note that the require on e2 is being done to simulate elapsing time with gurantee to get timestamp that exceed the periodFinished timestamp.
// We make sure to have the same attribute to the environment.
rule transition_DistActive_To_DistFinished(bytes32 distributionId){
    method f;  env e; calldataarg args;
    require distActive(distributionId, e);
    requireEnvValuesNotZero(e);
    f(e, args);
    
    assert distActive(distributionId, e), "distribution changed state";
    
    env e2;
    requireEnvValuesNotZero(e2);
    require e.msg.sender == e2.msg.sender;
    require e2.block.timestamp > getPeriodFinish(distributionId);

    assert distFinished(distributionId, e2), "distribution did not change state to finished even though the finish date has arrived";
}


// V@V - Funding a dist bringing us from the state distFinished back to distActive (no other function does that). All other functions will leave us in distFinished state.
rule transition_DistFinished_To_DistActive(bytes32 distributionId){
    method f; env e; calldataarg args;
    require distFinished(distributionId, e);
    requireEnvValuesNotZero(e);
    
    callFundDistributionWithSpecificDistId(f, e, distributionId);
    assert f.selector != fundDistribution(bytes32, uint256).selector <=> distFinished(distributionId, e), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector <=> distActive(distributionId, e), "distribution did not change due to call to fundDistribution function";
}


// V@V - starting from an initial state where dist 1 & 2 does not exist (all fields are in default values),
// creation of 2 dists (with different ids) must result from 2 different trios. 
// @note that hashUniquness is assuming that for different distIds the trios are not equal,
// therefore the rule is basically weaker than intended, it mainly shows that createDistribution from DistNotExist
// populate the mapping with the distinct trios
rule noTwoTripletsAreTheSameFirstStep(env e, env e2, bytes32 distributionId1, bytes32 distributionId2){
    method f; calldataarg args;
    address stakingToken1; address distributionToken1; uint256 dur1;
    address stakingToken2; address distributionToken2; uint256 dur2;

    require (distNotExist(distributionId1) && distNotExist(distributionId2));
    bytes32 distId1_return = createDistribution(e, stakingToken1, distributionToken1, dur1);
    bytes32 distId2_return = createDistribution(e2, stakingToken2, distributionToken2, dur2);
 
    hashUniquness(stakingToken1, distributionToken1, e.msg.sender, stakingToken2, distributionToken2, e2.msg.sender);
    requireDistIdCorrelatedWithTrio(distId1_return, stakingToken1, distributionToken1, e.msg.sender);
    requireDistIdCorrelatedWithTrio(distId2_return, stakingToken2, distributionToken2, e2.msg.sender); 

    assert ((distributionId1 == distId1_return && distributionId2 == distId2_return) => 
            ((getStakingToken(distId1_return) != getStakingToken(distId2_return)) || 
            (getDistributionToken(distId1_return) != getDistributionToken(distId2_return)) || 
            (getOwner(distId1_return) != getOwner(distId2_return))));
}


// CLEANED
// globalTokensPerStake is non-decreasing 
rule gtpsMonotonicity(bytes32 distributionId, method f){
        uint256 gtpsBefore = getGlobalTokensPerStake(distributionId);

        env e;
        calldataarg args;
        f(e, args);

        uint256 gtpsAfter = getGlobalTokensPerStake(distributionId);

        assert gtpsBefore <= gtpsAfter, "gtps was decreased";
}


// CLEANED
// userTokensPerStake is non-decreasing 
rule utpsMonotonicity(bytes32 distributionId, method f, address stakingToken, address user, uint256 index) filtered { f -> f.selector != certorafallback_0().selector} {
        requireInvariant gtpsGreaterOrEqualUtps(distributionId, stakingToken, user);

        uint256 utpsBefore = getUserTokensPerStake(distributionId, stakingToken, user);

        env e;
        calldataarg args;
        f(e, args);

        uint256 utpsAfter = getUserTokensPerStake(distributionId, stakingToken, user);

        assert utpsBefore <= utpsAfter, "utps was decreased";
}


// CLEANED
// lastUpdateTime is non-decreasing 
rule lastUpdateTimeMonotonicity(bytes32 distributionId, address stakingToken, address sender, method f, env e){
        requireInvariant lastUpdateTimeNotInFuture(e, distributionId);
        require !distNotExist(distributionId);
        requireInvariant getLastUpdateTimeLessThanFinish(distributionId);

        uint256 lastUpdateTimeBefore = getLastUpdateTime(distributionId);

        calldataarg args;
        f(e, args);

        uint256 lastUpdateTimeAfter = getLastUpdateTime(distributionId);

        assert lastUpdateTimeBefore <= lastUpdateTimeAfter, "lastUpdateTime was decreased";
}


// CLEANED
// Check that each possible operation changes the balance of at most one user
rule balanceOfChange(address userA, address userB, address stakingToken,  method f) {
	require userA != userB;

	uint256 balanceABefore = getUserBalance(stakingToken, userA);
	uint256 balanceBBefore = getUserBalance(stakingToken, userB);
	 
    env e; 
	calldataarg args;
	f(e, args); 
	
    uint256 balanceAAfter = getUserBalance(stakingToken, userA);
    uint256 balanceBAfter = getUserBalance(stakingToken, userB);

	assert (balanceABefore == balanceAAfter || balanceBBefore == balanceBAfter),"balances of two users were affected";
}


// CLEANED
// The duration cannot be changed if distribution is active
rule unchangedDurationDuringActiveDistribution(bytes32 distributionId, method f, env e){
    require distActive(distributionId, e);

    uint256 durationBefore = getDuration(distributionId);

    calldataarg args;
    f(e, args);

    uint256 durationAfter = getDuration(distributionId);

    assert durationBefore == durationAfter;
}

// CLEANED
// The owner of a distribution cannot be changed
rule permanentOwner(bytes32 distributionId, method f, env e){
    require distNew(distributionId) || distActive(distributionId, e) || distFinished(distributionId, e);

    address ownerBefore = getOwner(distributionId);

    calldataarg args;
    f(e, args);

    address ownerAfter = getOwner(distributionId);

    assert ownerAfter == ownerBefore;
}

// CLEANED
// total assets of a user (in Vault and in ERC Token) plus unclaimed tokens should be equal to the total assets of a user after claim function is called
rule claimCorrectnessCheckForOneUser(address distributionToken, address sender, address recipient, bytes32 distributionId, uint256 index){
    env e;
    bool toInternalBalance;
    bytes32[] distributionIds;
    
    require getDistributionToken(distributionId) == distributionToken;
    require Vault != recipient;
    require recipient != currentContract;    
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    uint256 vaultAndTokenBalanceBefore = Vault.totalAssetsOfUser(e, distributionToken, recipient);

    uint256 shouldBeClaimed = getClaimableTokens(e, distributionId, sender);

    claim(e, distributionIds, toInternalBalance, sender, recipient);

    uint256 vaultAndTokenBalanceAfter = Vault.totalAssetsOfUser(e, distributionToken, recipient);

    mathint all = vaultAndTokenBalanceBefore + shouldBeClaimed;

    assert all == to_mathint(vaultAndTokenBalanceAfter), "total asssets are not the same";
}


// CLEANED
// There is no way to claim reward twice at the same block timestamp (check for no reclaim)
rule noReclaim(address distributionToken, address sender, address recipient, bytes32 distributionId, uint256 index){
    env e;
    bool toInternalBalance;
    bytes32[] distributionIds;
    
    require getDistributionToken(distributionId) == distributionToken;
    require Vault != recipient;
    require recipient != currentContract;    
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    claim(e, distributionIds, toInternalBalance, sender, recipient);

    uint256 shouldBeClaimedAfter = getClaimableTokens(e, distributionId, sender);

    assert shouldBeClaimedAfter == 0, "shouldBeClaimedAfter isn't 0";
}


// CLEANED
// user A can't claim user B's reward (no frontrunning)
rule itIsOnlyMyReward(address distributionToken, bytes32 distributionId, address sender){
    env e;
    address userA; address userB;
    bool toInternalBalance;
    bytes32[] distributionIds;

    require isSubscribed(distributionId, sender); require isSubscribed(distributionId, userB);
    require getDistributionToken(distributionId) == distributionToken;
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;
    require sender != userB;
    require userA != userB;

    uint256 userBShouldClaimBefore = getClaimableTokens(e, distributionId, userB);

    claim(e, distributionIds, toInternalBalance, sender, userA);

    uint256 userBShouldClaimAfter = getClaimableTokens(e, distributionId, userB);

    assert userBShouldClaimBefore == userBShouldClaimAfter;
}


// V@V - Once 2 distributions has 2 distinct trios constituting them, their trio fields cannot be changed in such a way that will make them equivalent.
rule noTwoTripletsAreTheSame(env e, bytes32 distributionId1, bytes32 distributionId2){
    method f; calldataarg args;
    address _stakingToken1; address _distributionToken1; address _owner1;
    address _stakingToken2; address _distributionToken2; address _owner2;

    bool distState11 = distNotExist(distributionId1);
    bool distState12 = distNotExist(distributionId2);
    bool distState21 = distNew(distributionId1);
    bool distState22 = distNew(distributionId2);
    bool distState31 = distActive(distributionId1,e);
    bool distState32 = distActive(distributionId2,e);
    bool distState41 = distFinished(distributionId1,e);
    bool distState42 = distFinished(distributionId2,e);

    require (!distState11 && !distState12);

    // require oneStateAtATime for distributionId2
    require ((distState11 && !distState21 && !distState31 && !distState41) ||
            (!distState11 && distState21 && !distState31 && !distState41) ||
            (!distState11 && !distState21 && distState31 && !distState41) ||
            (!distState11 && !distState21 && !distState31 && distState41));

    // require oneStateAtATime for distributionId1
    require ((distState12 && !distState22 && !distState32 && !distState42) ||
            (!distState12 && distState22 && !distState32 && !distState42) ||
            (!distState12 && !distState22 && distState32 && !distState42) ||
            (!distState12 && !distState22 && !distState32 && distState42));

    requireDistIdCorrelatedWithTrio(distributionId1, _stakingToken1, _distributionToken1, _owner1); requireInvariant distExistInitializedParams(distributionId1, e);
    requireDistIdCorrelatedWithTrio(distributionId2, _stakingToken2, _distributionToken2, _owner2); requireInvariant distExistInitializedParams(distributionId2, e);
    require ((getStakingToken(distributionId1) != getStakingToken(distributionId2)) || (getDistributionToken(distributionId1) != getDistributionToken(distributionId2)) || (getOwner(distributionId1) != getOwner(distributionId2)));
    f(e,args);
    assert ((getStakingToken(distributionId1) != getStakingToken(distributionId2)) || (getDistributionToken(distributionId1) != getDistributionToken(distributionId2)) || (getOwner(distributionId1) != getOwner(distributionId2))), "all 3 fields are the same";
}


// V@V - When calling a function on a specific distribution (e.g. subscribe, set duration, fund, etc.), no other distributions are being affected
rule distributionsAreIndependent(method f, bytes32 distributionId1, bytes32 distributionId2) {
    env e1; env e2; bytes32[] distIdArray; address stakingToken; address recipient; address[] stakingTokensArray;
    address _sToken = getStakingToken(distributionId1);
    address _dToken = getDistributionToken(distributionId1);
    address _owner = getOwner(distributionId1);
    uint256 _totSupply = getTotalSupply(distributionId1);
    uint256 _duration = getDuration(distributionId1);
    uint256 _pFinished = getPeriodFinish(distributionId1);
    uint256 _pRate = getPaymentRate(distributionId1);
    uint256 _lastUpdateTime = getLastUpdateTime(distributionId1);
    uint256 _globalTokensPerStake = getGlobalTokensPerStake(distributionId1);

    require distributionId2 != distributionId1;
    require distIdArray.length <= 1 && distIdArray[0] != distributionId1;
    callAllFunctionsWithParameters(f, e2, distributionId2, distIdArray, stakingToken, recipient, stakingTokensArray);
    bool isSpecificFunctionCalled = nonSpecificDistribution(f);

    address sToken_ = getStakingToken(distributionId1);
    address dToken_ = getDistributionToken(distributionId1);
    address owner_ = getOwner(distributionId1);
    uint256 totSupply_ = getTotalSupply(distributionId1);
    uint256 duration_ = getDuration(distributionId1);
    uint256 pFinished_ = getPeriodFinish(distributionId1);
    uint256 pRate_ = getPaymentRate(distributionId1);
    uint256 lastUpdateTime_ = getLastUpdateTime(distributionId1);
    uint256 globalTokensPerStake_ = getGlobalTokensPerStake(distributionId1);

    assert sToken_ == _sToken && dToken_ == _dToken && owner_ == _owner && duration_ == _duration && pFinished_ == _pFinished && pRate_ == _pRate, "staking token changed";
    assert ((totSupply_ == _totSupply) || (isSpecificFunctionCalled <=> (totSupply_ != _totSupply))) &&
                ((lastUpdateTime_ == _lastUpdateTime) || (isSpecificFunctionCalled <=> (lastUpdateTime_ != _lastUpdateTime))) &&
                ((globalTokensPerStake_ == _globalTokensPerStake) || (isSpecificFunctionCalled <=> (globalTokensPerStake_ != _globalTokensPerStake))), "totSupply changed not due to stake/unstake/exit";
}


// CLEANED
// Check that the changes to total supply are coherent with the changes to balance
rule integrityBalanceOfTotalSupply(address user, address distributionToken, address stakingToken, bytes32 distributionId, uint256 index, method f, env e) filtered { f -> f.selector != certorafallback_0().selector} {
    require e.msg.sender == user;
    require getStakingToken(distributionId) == stakingToken;
    require getDistributionToken(distributionId) == distributionToken;
    requireInvariant userSubStakeCorrelationWithTotalSupply(distributionId, user, stakingToken, index, e);
    
	uint256 balanceABefore = getUserBalance(stakingToken, user);
	uint256 totalSupplyBefore = getTotalSupply(distributionId);

	integrityHelper(f, e, distributionId, user, distributionToken, stakingToken); 

	uint256 balanceAAfter = getUserBalance(stakingToken, user);
	uint256 totalSupplyAfter = getTotalSupply(distributionId);

	assert (balanceAAfter != balanceABefore) 
                => (balanceAAfter - balanceABefore  == totalSupplyAfter - totalSupplyBefore), "not correlated";
}


// the sum of internal and external balances of a user remains the same
rule solvencyForOneUser(address distributionToken, address stakingToken, bytes32 distributionId, method f) filtered { f -> !f.isView 
                                                    && f.selector != certorafallback_0().selector } {
    env e; 
    
    address user;
    uint256 amount;

    require Vault != user;
    require user != currentContract;
    require distributionToken == stakingToken;
    
    require getDistributionToken(distributionId) == distributionToken;
    require getStakingToken(distributionId) == stakingToken;

    uint256 claimableTokensBefore = getClaimableTokens(e, distributionId, user);
    uint256 userBalanceBefore = getUserBalance(stakingToken, user);
    uint256 vaultAndTokenBalanceBefore = Vault.totalAssetsOfUser(e, distributionToken, user);

    mathint combinedBalanceBefore = claimableTokensBefore + userBalanceBefore + vaultAndTokenBalanceBefore;

    solvencyHelper(f, e, distributionId, user, distributionToken, stakingToken);

    uint256 claimableTokensAfter = getClaimableTokens(e, distributionId, user);
    uint256 userBalanceAfter = getUserBalance(stakingToken, user);
    uint256 vaultAndTokenBalanceAfter = Vault.totalAssetsOfUser(e, distributionToken, user);

    mathint combinedBalanceAfter = claimableTokensAfter + userBalanceAfter + vaultAndTokenBalanceAfter;

    assert combinedBalanceBefore == combinedBalanceAfter, "balances are not equal";
}
