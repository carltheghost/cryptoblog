// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IMWANJESA {
    function mintReward(address to, uint256 amount) external;
}

/// @title TessStaking - MWANJESA PoS staking
contract TessStaking is ReentrancyGuard {
    IERC20 public mwanjesa;
    IMWANJESA public mwanjesaMintable;

    uint256 public constant REWARD_RATE_BPS = 1284; // 12.84% APY approximation
    uint256 public totalStaked;

    struct StakeInfo {
        uint256 amount;
        uint256 stakedAt;
        uint256 lockPeriod;
        uint256 lastClaim;
    }

    mapping(address => StakeInfo) public stakes;

    event Staked(address indexed user, uint256 amount, uint256 lockPeriod);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);

    constructor(address _mwanjesa) {
        mwanjesa = IERC20(_mwanjesa);
        mwanjesaMintable = IMWANJESA(_mwanjesa);
    }

    function stake(uint256 amount, uint256 lockPeriod) external nonReentrant {
        require(amount > 0, "Zero amount");
        mwanjesa.transferFrom(msg.sender, address(this), amount);
        stakes[msg.sender].amount += amount;
        stakes[msg.sender].stakedAt = block.timestamp;
        stakes[msg.sender].lockPeriod = lockPeriod;
        stakes[msg.sender].lastClaim = block.timestamp;
        totalStaked += amount;
        emit Staked(msg.sender, amount, lockPeriod);
    }

    function unstake(uint256 amount) external nonReentrant {
        StakeInfo storage s = stakes[msg.sender];
        require(s.amount >= amount, "Insufficient stake");
        require(block.timestamp >= s.stakedAt + s.lockPeriod, "Still locked");
        s.amount -= amount;
        totalStaked -= amount;
        mwanjesa.transfer(msg.sender, amount);
        emit Unstaked(msg.sender, amount);
    }

    function claimRewards() external nonReentrant {
        StakeInfo storage s = stakes[msg.sender];
        require(s.amount > 0, "No stake");
        uint256 elapsed = block.timestamp - s.lastClaim;
        uint256 reward = (s.amount * REWARD_RATE_BPS * elapsed) / (10000 * 365 days);
        s.lastClaim = block.timestamp;
        mwanjesaMintable.mintReward(msg.sender, reward);
        emit RewardsClaimed(msg.sender, reward);
    }
}
