// ATN Project - Smart Contract Deployment Script

const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying ATN Smart Contracts...\n");

  // Deploy AgentRegistry
  const AgentRegistry = await hre.ethers.getContractFactory("AgentRegistry");
  const agentRegistry = await AgentRegistry.deploy();
  await agentRegistry.waitForDeployment();
  
  const agentRegistryAddress = await agentRegistry.getAddress();
  console.log("✅ AgentRegistry deployed to:", agentRegistryAddress);

  // Deploy ReputationLedger
  const ReputationLedger = await hre.ethers.getContractFactory("ReputationLedger");
  const reputationLedger = await ReputationLedger.deploy();
  await reputationLedger.waitForDeployment();
  
  const reputationLedgerAddress = await reputationLedger.getAddress();
  console.log("✅ ReputationLedger deployed to:", reputationLedgerAddress);

  // Save addresses to file
  const fs = require("fs");
  const path = require("path");
  
  const addresses = {
    AgentRegistry: agentRegistryAddress,
    ReputationLedger: reputationLedgerAddress,
    deployedAt: new Date().toISOString(),
    network: hre.network.name
  };
  
  const addressesPath = path.join(__dirname, "..", "..", "deployed_addresses.json");
  fs.writeFileSync(addressesPath, JSON.stringify(addresses, null, 2));
  
  console.log("\n📄 Addresses saved to:", addressesPath);
  console.log("\n🎉 Deployment complete!");
  
  return { agentRegistryAddress, reputationLedgerAddress };
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
