// cooinTokenManager.ts

import fs from 'fs';
import path from 'path';

const TOKEN_CLAIMS_FILE = path.join(__dirname, 'cooin token.txt');

interface ClaimedToken {
  tokenName: string;
  claimedBy: string; // Wallet address of the claimer
}

function readClaimedTokens(): ClaimedToken[] {
  try {
    const data = fs.readFileSync(TOKEN_CLAIMS_FILE, 'utf-8');
    return data.split('\n')
      .filter(line => line.trim() !== '')
      .map(line => {
        const match = line.match(/^(.+)\s\(claimed by\s(.+)\)$/);
        if (match) {
          return { tokenName: match[1].trim(), claimedBy: match[2].trim() };
        }
        return null;
      })
      .filter((claim): claim is ClaimedToken => claim !== null);
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      return [];
    }
    console.error('Error reading token claims file:', error);
    return [];
  }
}

function addClaimedToken(tokenName: string, walletAddress: string): void {
  const claimedTokens = readClaimedTokens();
  const isAlreadyClaimed = claimedTokens.some(
    (claim) => claim.tokenName === tokenName && claim.claimedBy === walletAddress
  );

  if (isAlreadyClaimed) {
    console.log(`Token '${tokenName}' is already claimed by wallet '${walletAddress}'.`);
    return;
  }

  const newLine = `${tokenName} (claimed by ${walletAddress})`;
  try {
    fs.appendFileSync(TOKEN_CLAIMS_FILE, '\n' + newLine, 'utf-8');
    console.log(`Token '${tokenName}' claimed by wallet '${walletAddress}'. Added to ${TOKEN_CLAIMS_FILE}`);
  } catch (error) {
    console.error('Error writing to token claims file:', error);
  }
}

function findClaimedBy(tokenName: string): string | null {
  const claimedTokens = readClaimedTokens();
  const claim = claimedTokens.find((c) => c.tokenName === tokenName);
  return claim ? claim.claimedBy : null;
}

function getAllClaims(): ClaimedToken[] {
  return readClaimedTokens();
}

export { addClaimedToken, findClaimedBy, getAllClaims };
