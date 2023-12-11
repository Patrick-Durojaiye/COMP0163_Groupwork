const hre = require("hardhat");

async function main() {

  const PR = await hre.ethers.deployContract("Patient Records", ["Patient_Records", "PR"]);

  await PR.waitForDeployment();

  console.log('Patient Records contract deployed');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
