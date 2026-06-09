// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";

/// @title MWANJESA - Decentralized economy token (PoS rewards)
contract MWANJESAToken is ERC20, ERC20Burnable {
    uint256 public constant MAX_SUPPLY = 10_000_000_000 * 10 ** 18;
    address public stakingContract;

    modifier onlyStaking() {
        require(msg.sender == stakingContract, "Not staking contract");
        _;
    }

    constructor() ERC20("MWANJESA", "MWANJESA") {
        _mint(msg.sender, 500_000_000 * 10 ** decimals());
    }

    function setStakingContract(address _staking) external {
        require(stakingContract == address(0), "Already set");
        stakingContract = _staking;
    }

    function mintReward(address to, uint256 amount) external onlyStaking {
        require(totalSupply() + amount <= MAX_SUPPLY, "Max supply exceeded");
        _mint(to, amount);
    }
}
