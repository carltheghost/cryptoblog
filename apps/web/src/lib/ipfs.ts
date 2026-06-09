/** Convert TessStorage / IPFS CID to a display URL */
export function ipfsToUrl(cid: string): string {
  if (!cid) return "";
  const hash = cid.replace(/^ipfs:\/\//, "");
  return `https://ipfs.io/ipfs/${hash}`;
}
