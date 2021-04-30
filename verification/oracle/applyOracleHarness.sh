# Replace LogExpMath with FakeLogExpMath
perl -0777 -i -pe 's/import \"\.\/LogExpMath\.sol\";/import \"\..\/..\/..\/verification\/oracle\/FakeLogExpMath\.sol\";/g' contracts/lib/math/FixedPoint.sol
perl -0777 -i -pe 's/ LogExpMath/ FakeLogExpMath/g' contracts/lib/math/FixedPoint.sol
perl -0777 -i -pe 's/ LogExpMath/ FakeLogExpMath/g' contracts/pools/weighted/WeightedOracleMath.sol
perl -0777 -i -pe 's/import \"\.\.\/\.\.\/lib\/math\/\/LogExpMath\.sol\";/import \"\..\/..\/..\/verification\/oracle\/FakeLogExpMath\.sol\";/g' contracts/pools/weighted/WeightedOracleMath.sol
perl -0777 -i -pe 's/\(LogExpMath/\(FakeLogExpMath/g' contracts/pools/weighted/WeightedOracleMath.sol
perl -0777 -i -pe 's/exp\(-x\)/3/g' contracts/lib/math/LogExpMath.sol
