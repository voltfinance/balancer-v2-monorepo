# Replace LogExpMath with SmartFakeLogExpMath
perl -0777 -i -pe 's/import \"\.\/LogExpMath\.sol\";/import \"\..\/..\/..\/verification\/oracle\/SmartFakeLogExpMath\.sol\";/g' contracts/lib/math/FixedPoint.sol
perl -0777 -i -pe 's/ LogExpMath/ SmartFakeLogExpMath/g' contracts/lib/math/FixedPoint.sol
perl -0777 -i -pe 's/ LogExpMath/ SmartFakeLogExpMath/g' contracts/pools/weighted/WeightedOracleMath.sol
perl -0777 -i -pe 's/import \"\.\.\/\.\.\/lib\/math\/\/LogExpMath\.sol\";/import \"\..\/..\/..\/verification\/oracle\/SmartFakeLogExpMath\.sol\";/g' contracts/pools/weighted/WeightedOracleMath.sol
perl -0777 -i -pe 's/\(LogExpMath/\(SmartFakeLogExpMath/g' contracts/pools/weighted/WeightedOracleMath.sol
perl -0777 -i -pe 's/exp\(-x\)/3/g' contracts/lib/math/LogExpMath.sol

# virtualize

perl -0777 -i -pe 's/\) internal {/\) internal virtual {/g' contracts/pools/weighted/WeightedPool2Tokens.sol
