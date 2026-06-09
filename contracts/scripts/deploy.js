const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying TessChain contracts with:", deployer.address);

  const MGANGAToken = await hre.ethers.getContractFactory("MGANGAToken");
  const mganga = await MGANGAToken.deploy();
  await mganga.waitForDeployment();
  const mgangaAddr = await mganga.getAddress();
  console.log("MGANGAToken:", mgangaAddr);

  const MWANJESAToken = await hre.ethers.getContractFactory("MWANJESAToken");
  const mwanjesa = await MWANJESAToken.deploy();
  await mwanjesa.waitForDeployment();
  const mwanjesaAddr = await mwanjesa.getAddress();
  console.log("MWANJESAToken:", mwanjesaAddr);

  const HYBToken = await hre.ethers.getContractFactory("HYBToken");
  const hyb = await HYBToken.deploy();
  await hyb.waitForDeployment();
  const hybAddr = await hyb.getAddress();
  console.log("HYBToken:", hybAddr);

  const TessStaking = await hre.ethers.getContractFactory("TessStaking");
  const staking = await TessStaking.deploy(mwanjesaAddr);
  await staking.waitForDeployment();
  const stakingAddr = await staking.getAddress();
  console.log("TessStaking:", stakingAddr);

  const TessGovernance = await hre.ethers.getContractFactory("TessGovernance");
  const governance = await TessGovernance.deploy(hybAddr);
  await governance.waitForDeployment();
  const governanceAddr = await governance.getAddress();
  console.log("TessGovernance:", governanceAddr);

  const LivingRelic = await hre.ethers.getContractFactory("LivingRelic");
  const relic = await LivingRelic.deploy();
  await relic.waitForDeployment();
  const relicAddr = await relic.getAddress();
  console.log("LivingRelic:", relicAddr);

  const HYBBridge = await hre.ethers.getContractFactory("HYBBridge");
  const bridge = await HYBBridge.deploy(mgangaAddr, mwanjesaAddr, hybAddr);
  await bridge.waitForDeployment();
  const bridgeAddr = await bridge.getAddress();
  console.log("HYBBridge:", bridgeAddr);

  const addresses = {
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    deployer: deployer.address,
    MGANGAToken: mgangaAddr,
    MWANJESAToken: mwanjesaAddr,
    HYBToken: hybAddr,
    TessStaking: stakingAddr,
    TessGovernance: governanceAddr,
    LivingRelic: relicAddr,
    HYBBridge: bridgeAddr,
    deployedAt: new Date().toISOString(),
  };

  const outDir = path.join(__dirname, "..", "deployments");
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, `${hre.network.name}.json`);
  fs.writeFileSync(outFile, JSON.stringify(addresses, null, 2));
  console.log("Addresses written to", outFile);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
