import "multiDistributorPreset.spec"

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Invariants    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// V@V - _indexes mapping and _values array are correlated in the enumerable set
invariant enumerableSetIsCorrelated(address stakingToken, address user, uint256 index, bytes32 distributionId)
        // ID in mapping declare "not contained", then the array at the index is not distributionId
        (getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == max_uint256 => 
            (getUserSubscribedDistributionIdByIndex(stakingToken, user, index) != distributionId) && 
        // Id in mapping declare "containd", then the array at index is distributionId <=> ID in mapping retrieve index 
        getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) != max_uint256 =>
            ((getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId && distributionId != 0) <=> 
                (getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index)))
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                require distributionIdArray[0] == distributionId;
            }
        }

// V@V - checks the correlation of the set and _userStaking mapping. If the distributionId is in the set, the stakingToken associated with this distributionId is the same as the stakingToken in the mapping.
// If the stakingToken associated to the distributionId is not the same as the stakingToken leading to the set in the mapping, then the distributionId shouldn't be in the set.
invariant _userStakingMappingAndSetAreCorrelated(bytes32 distributionId, address stakingToken, address user)
        (stakingToken == 0 => !getDistIdContainedInUserSubscribedDistribution(stakingToken, user, distributionId)) &&
        (stakingToken != 0 => (getDistIdContainedInUserSubscribedDistribution(stakingToken, user, distributionId) => 
                getStakingToken(distributionId) == stakingToken))
        {
            preserved createDistribution(address stakingToken2, address distributionToken2, uint256 duration2) with (env e)
            {
                requireInvariant distExistInitializedParams(distributionId, e);
            }
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                require distributionIdArray[0] == distributionId;
            }
        }


// V@V - duration, owner, staking token and dist token are either initialized (!=0) or uninitialized (0) simultaneously
invariant distExistInitializedParams(bytes32 distributionId, env e)
        (getDuration(distributionId) == 0 <=> getOwner(distributionId) == 0) && 
        (getOwner(distributionId) == 0 <=> getStakingToken(distributionId) == 0) && 
        (getStakingToken(distributionId) == 0 <=> getDistributionToken(distributionId) == 0)
        {
            preserved with (env e2)
            { 
                require e.msg.sender == e2.msg.sender;
                require e2.msg.sender != 0;
            }
        }


// V@V - A user cannot be subscribed to a distribution that does not exist, and the other way around - if a user is subscribed to a distribution then it has to exist.
invariant notSubscribedToNonExistingDistSet(bytes32 distributionId, address user)
        (getStakingToken(distributionId) == 0 => !isSubscribed(distributionId, user)) &&
            (isSubscribed(distributionId, user) => getStakingToken(distributionId) != 0)
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                address stakingToken; uint256 index;
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distributionId);
            }
        }
 

// V@V - If duration/owner/staking_token/distribution_token are not set, the distribution does not exist
invariant conditionsDistNotExist(bytes32 distributionId)
        getStakingToken(distributionId) == 0 <=> distNotExist(distributionId)
        filtered { f -> f.selector != certorafallback_0().selector }
        {
            preserved with (env e)
            {
                address stakingToken; address user; uint256 index; address distributionToken;
                require index == 0;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken, distributionToken, user);
                requireInvariant distExistInitializedParams(distributionId, e);
                require index == 0;
                require getUserSetLength(stakingToken, user) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken, user);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
                require (
                        getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == max_uint256 &&
                        getUserSubscribedDistributionIdByIndex(stakingToken, user, index) != distributionId 
                    );
            }
            preserved stake(address stakingToken2, uint256 amount, address sender, address recipient) with (env e)
            {
                uint256 index2; address distributionToken2;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken2, distributionToken2, recipient);
                requireInvariant distExistInitializedParams(distributionId, e);
                require index2 == 0;
                require getUserSetLength(stakingToken2, recipient) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken2, recipient, index2, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken2, recipient);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient);
            }
            preserved stakeUsingVault(address stakingToken3, uint256 amount, address sender, address recipient) with (env e)
            {
                uint256 index3; address distributionToken3;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken3, distributionToken3, recipient);
                requireInvariant distExistInitializedParams(distributionId, e);
                require index3 == 0;
                require getUserSetLength(stakingToken3, recipient) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken3, recipient, index3, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken3, recipient);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient);
            }
            preserved stakeWithPermit(address stakingToken4, uint256 amount, address sender, uint256 deadline, uint8 v, bytes32 r, bytes32 s) with (env e)
            {
                uint256 index4; address distributionToken4;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken4, distributionToken4, sender);
                requireInvariant distExistInitializedParams(distributionId, e);
                require index4 == 0;
                require getUserSetLength(stakingToken4, sender) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken4, sender, index4, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken4, sender);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, sender);
            }
            preserved unstake(address stakingToken5, uint256 amount, address sender, address recipient) with (env e)
            {
                uint256 index5; address distributionToken5;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken5, distributionToken5, recipient);
                requireInvariant distExistInitializedParams(distributionId, e);
                require index5 == 0;
                require getUserSetLength(stakingToken5, recipient) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken5, recipient, index5, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken5, recipient);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient);
            
            }
            preserved exit(address[] stakingTokens6, bytes32[] distributionIds) with (env e)
            {
                uint256 index6; address stakingToken6; address distributionToken6; address recipient_exit;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken6, distributionToken6, recipient_exit);
                requireInvariant distExistInitializedParams(distributionId, e);
                require index6 == 0;
                require stakingTokens6.length == 1 && stakingTokens6[0] == distributionToken6;
                require getUserSetLength(stakingToken6, recipient_exit) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken6, recipient_exit, index6, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken6, recipient_exit);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient_exit);
            }
            preserved exitWithCallback(address[] stakingTokens7, bytes32[] distributionIds, address callbackContract, bytes callbackData) with (env e)
            {
                uint256 index7; address stakingToken7; address distributionToken7; address recipient_exitWCB;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken7, distributionToken7, recipient_exitWCB);
                requireInvariant distExistInitializedParams(distributionId, e);
                require index7 == 0;
                require stakingTokens7.length == 1 && stakingTokens7[0] == stakingToken7;
                require distributionIds.length == 1 && distributionIds[0] == distributionId;
                require getUserSetLength(stakingToken7, recipient_exitWCB) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken7, recipient_exitWCB, index7, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken7, recipient_exitWCB);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient_exitWCB);
            }
        }


// V@V - stakingToken != 0 <=> !distNotExist (distExist) => the state is in **one** of the other 3 definitions.
// @note that this invariant might be covered by oneStateAtATime
invariant conditionsDistExist(bytes32 distributionId, env e)
        getStakingToken(distributionId) != 0 => ((distNew(distributionId) && !distActive(distributionId, e) && !distFinished(distributionId, e)) ||
                                        (!distNew(distributionId) && distActive(distributionId, e) && !distFinished(distributionId, e)) ||
                                        (!distNew(distributionId) && !distActive(distributionId, e) && distFinished(distributionId, e)))
        {
            preserved with (env e2)
            {
                require e.msg.sender == e2.msg.sender;
                requireEnvValuesNotZero(e2);
                requireInvariant distExistInitializedParams(distributionId, e2);
                requireInvariant conditionsDistNotExist(distributionId);
            }
        }


// V@V - lastUpdateTime, periodFinished are either initialized (!=0) or uninitialized (0) simultaneously
// @note that the commented line - correlation of paymentRate to the mentioned fields - is planed left as a comment, 
// as the dev team plan to limit values of some properties, and add requires that will ensure paymentRate > 0 in the near future.
invariant distActivatedAtLeastOnceParams(bytes32 distributionId, env e)
        (getLastUpdateTime(distributionId) == 0 <=> getPeriodFinish(distributionId) == 0) //&&
            // (getPeriodFinish(distributionId) == 0 <=> getPaymentRate(distributionId) == 0)
        {
            preserved with (env e2)
            {
                require e.block.timestamp == e2.block.timestamp;
                require e2.block.timestamp > 0;
            }
        }


// V@V - The system is in either of the 4 defined states. It cannot be in any other state, nor in more than 1 state at the same time.
invariant oneStateAtATime(bytes32 distributionId, env e)
        ((distNotExist(distributionId) && !distNew(distributionId) && !distActive(distributionId, e) && !distFinished(distributionId, e)) ||
        (!distNotExist(distributionId) && distNew(distributionId) && !distActive(distributionId, e) && !distFinished(distributionId, e)) ||
        (!distNotExist(distributionId) && !distNew(distributionId) && distActive(distributionId, e) && !distFinished(distributionId, e)) ||
        (!distNotExist(distributionId) && !distNew(distributionId) && !distActive(distributionId, e) && distFinished(distributionId, e)))
        filtered { f -> f.selector != certorafallback_0().selector }
        {
            preserved with (env e2)
            {
                require e.block.timestamp == e2.block.timestamp;
                requireEnvValuesNotZero(e2);
                address stakingToken; address user; uint256 index; address distributionToken;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken, distributionToken, user);
                requireInvariant distExistInitializedParams(distributionId, e2);
                require index == 0;
                require getUserSetLength(stakingToken, user) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken, user);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            }
            preserved stake(address stakingToken2, uint256 amount, address sender, address recipient) with (env e3)
            {
                require e.block.timestamp == e3.block.timestamp;
                requireEnvValuesNotZero(e3);
                uint256 index2; address distributionToken2;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken2, distributionToken2, recipient);
                requireInvariant distExistInitializedParams(distributionId, e3);
                require index2 == 0;
                require getUserSetLength(stakingToken2, recipient) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken2, recipient, index2, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken2, recipient);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient);
            }
            preserved stakeUsingVault(address stakingToken3, uint256 amount, address sender, address recipient) with (env e4)
            {
                require e.block.timestamp == e4.block.timestamp;
                requireEnvValuesNotZero(e4);
                uint256 index3; address distributionToken3;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken3, distributionToken3, recipient);
                requireInvariant distExistInitializedParams(distributionId, e4);
                require index3 == 0;
                require getUserSetLength(stakingToken3, recipient) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken3, recipient, index3, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken3, recipient);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient);
            }
            preserved stakeWithPermit(address stakingToken4, uint256 amount, address sender, uint256 deadline, uint8 v, bytes32 r, bytes32 s) with (env e5)
            {
                require e.block.timestamp == e5.block.timestamp;
                requireEnvValuesNotZero(e5);
                uint256 index4; address distributionToken4;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken4, distributionToken4, sender);
                requireInvariant distExistInitializedParams(distributionId, e5);
                require index4 == 0;
                require getUserSetLength(stakingToken4, sender) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken4, sender, index4, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken4, sender);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, sender);
            }
            preserved unstake(address stakingToken5, uint256 amount, address sender, address recipient) with (env e6)
            {
                require e.block.timestamp == e6.block.timestamp;
                requireEnvValuesNotZero(e6);                
                uint256 index5; address distributionToken5;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken5, distributionToken5, recipient);
                requireInvariant distExistInitializedParams(distributionId, e6);
                require index5 == 0;
                require getUserSetLength(stakingToken5, recipient) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken5, recipient, index5, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken5, recipient);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient);
            
            }
            preserved exit(address[] stakingTokens6, bytes32[] distributionIds) with (env e7)
            {
                require e.block.timestamp == e7.block.timestamp;
                requireEnvValuesNotZero(e7);                
                uint256 index6; address stakingToken6; address distributionToken6; address recipient_exit;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken6, distributionToken6, recipient_exit);
                requireInvariant distExistInitializedParams(distributionId, e7);
                require index6 == 0;
                require stakingTokens6.length == 1 && stakingTokens6[0] == stakingToken6;
                require getUserSetLength(stakingToken6, recipient_exit) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken6, recipient_exit, index6, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken6, recipient_exit);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient_exit);
            }
            preserved exitWithCallback(address[] stakingTokens7, bytes32[] distributionIds, address callbackContract, bytes callbackData) with (env e8)
            {
                require e.block.timestamp == e8.block.timestamp;
                requireEnvValuesNotZero(e8);                
                uint256 index7; address stakingToken7; address distributionToken7; address recipient_exitWCB;
                requireDistIdCorrelatedWithTrio(distributionId, stakingToken7, distributionToken7, recipient_exitWCB);
                requireInvariant distExistInitializedParams(distributionId, e8);
                require index7 == 0;
                require stakingTokens7.length == 1 && stakingTokens7[0] == stakingToken7;
                require distributionIds.length == 1 && distributionIds[0] == distributionId;
                require getUserSetLength(stakingToken7, recipient_exitWCB) == 1;
                requireInvariant enumerableSetIsCorrelated(stakingToken7, recipient_exitWCB, index7, distributionId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distributionId, stakingToken7, recipient_exitWCB);
                requireInvariant notSubscribedToNonExistingDistSet(distributionId, recipient_exitWCB);
            }
        }


// V@V - lastUpdateTime can't be in the future
invariant lastUpdateTimeNotInFuture(env e, bytes32 distributionId)
    getLastUpdateTime(distributionId) <= e.block.timestamp
    {
        preserved with (env e2)
        {
            require e.block.timestamp == e2.block.timestamp;
        }
    }


// V@V - lastUpdateTime cannot be greater than periodFinish
invariant getLastUpdateTimeLessThanFinish(bytes32 distributionId)
    getLastUpdateTime(distributionId) <= getPeriodFinish(distributionId)


// V@V - _lastTimePaymentApplicable is always greater or equal than lastUpdateTime to avoid underflow
invariant validityOfLastTimePaymentApplicable(bytes32 distributionId, env e)
    getLastUpdateTime(distributionId) <= _lastTimePaymentApplicableHarness(e, distributionId)
    {
        preserved with (env e2)
        { 
            require e.block.timestamp == e2.block.timestamp;
        }
    }


// V@V - The global token per stake (gtps) is always greater or equal to the user token per stake (utps) 
invariant gtpsGreaterOrEqualUtps(bytes32 distributionId, address stakingToken, address user)
        getGlobalTokensPerStake(distributionId) >= getUserTokensPerStake(distributionId, stakingToken, user)



// The balance of subscribed and staked user should be less than or equal to the totalSupply of a distribution
invariant userSubStakeCorrelationWithTotalSupply(bytes32 distributionId, address user, address token, uint256 index, env e)
    (isSubscribed(distributionId, user) && getUserBalance(token, user) > 0)
            => (getUserBalance(token, user) <= getTotalSupply(distributionId)) filtered { f -> f.selector != certorafallback_0().selector }
    { 
        preserved with (env e2) 
        {
            require e2.msg.sender == user;
            require getStakingToken(distributionId) == token;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved unsubscribeDistributions(bytes32[] distributionIds) with (env e3)
        {
            require distributionIds.length <= 3;
            require distributionIds[0] == distributionId;
            require user == e3.msg.sender;
            require getStakingToken(distributionId) == token;
        }
        preserved stake(address stakingToken, uint256 amount, address sender, address recipient) with (env e4)
        {   
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            require index == 0;
            require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        }
        preserved stakeUsingVault(address stakingToken, uint256 amount, address sender, address recipient) with (env e5)
        {
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            require index == 0;
            require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        }
        preserved stakeWithPermit(address stakingToken, uint256 amount, address sender, uint256 deadline, uint8 v, bytes32 r, bytes32 s) with (env e6)
        {
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            require index == 0;
            require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        }
        preserved unstake(address stakingToken, uint256 amount, address sender, address recipient) with (env e7)
        {
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved exit(address[] stakingTokens, bytes32[] distributionIds) with (env e8)
        {
            require e8.msg.sender == user;
            require getStakingToken(distributionId) == token;
            require stakingTokens.length <= 3;
            require stakingTokens[0] == token;
            require distributionIds[0] == distributionId;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved exitWithCallback(address[] stakingTokens, bytes32[] distributionIds, address callbackContract, bytes callbackData) with (env e9)
        {
            require e9.msg.sender == user;
            require getStakingToken(distributionId) == token;
            require stakingTokens.length <= 3;
            require distributionIds.length <= 3;
            require stakingTokens[0] == token;
            require distributionIds[0] == distributionId;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved createDistribution(address stakingToken, address distributionToken, uint256 duration) with (env e10)
        {
            require stakingToken == token;
            require getStakingToken(distributionId) == token;
            require getDistributionToken(distributionId) == distributionToken;
            require e10.msg.sender == user;
            require createDistribution(e10, stakingToken, distributionToken, duration) == distributionId;
            require (
                        getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == max_uint256 &&
                        getUserSubscribedDistributionIdByIndex(stakingToken, user, index) != distributionId 
                    ) 
                    ||    
                    (  
                        getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                        getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index
                    );
        }
    }

