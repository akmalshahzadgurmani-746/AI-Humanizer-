/**
 * Computes word-level differences between two strings using LCS (Longest Common Subsequence).
 * Retains spaces and punctuation to reconstruct formatting correctly.
 * 
 * Returns an array of objects:
 * { type: 'added' | 'removed' | 'unchanged', value: string }
 */
export function diffWords(oldStr, newStr) {
  if (!oldStr) return [{ type: 'added', value: newStr }];
  if (!newStr) return [{ type: 'removed', value: oldStr }];

  // Split by words, punctuation, and whitespace groups
  const tokenize = (str) => {
    return str.split(/([a-zA-Z0-9']+|[^\s\w]+)/g).filter(x => x !== '');
  };

  const oldTokens = tokenize(oldStr);
  const newTokens = tokenize(newStr);

  const dp = Array(oldTokens.length + 1)
    .fill(null)
    .map(() => Array(newTokens.length + 1).fill(0));

  // Compute LCS length table
  for (let i = 1; i <= oldTokens.length; i++) {
    for (let j = 1; j <= newTokens.length; j++) {
      if (oldTokens[i - 1] === newTokens[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }

  // Backtrack to find diff sequence
  const result = [];
  let i = oldTokens.length;
  let j = newTokens.length;

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && oldTokens[i - 1] === newTokens[j - 1]) {
      result.unshift({ type: 'unchanged', value: oldTokens[i - 1] });
      i--;
      j--;
    } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
      result.unshift({ type: 'added', value: newTokens[j - 1] });
      j--;
    } else {
      result.unshift({ type: 'removed', value: oldTokens[i - 1] });
      i--;
    }
  }

  // Combine adjacent diff segments of the same type for cleaner rendering
  const merged = [];
  for (const token of result) {
    if (merged.length > 0 && merged[merged.length - 1].type === token.type) {
      merged[merged.length - 1].value += token.value;
    } else {
      merged.push(token);
    }
  }

  return merged;
}
