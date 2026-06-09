// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title HYB Bridge - Cross-economy token bridge (MGANGA <-> MWANJESA)
contract HYBBridge is Ownable {
    IERC20 public mganga;
    IERC20 public mwanjesa;
    IERC20 public hyb;

    uint256 public exchangeRate = 98; // 0.98 scaled by 100
    uint256 public constant RATE_SCALE = 100;

    mapping(address => uint256) public lockedMganga;
    mapping(address => uint256) public lockedMwanjesa;

    event BridgedToDefi(address indexed user, uint256 mgangaAmount, uint256 mwanjesaReceived);
    event BridgedToCefi(address indexed user, uint256 mwanjesaAmount, uint256 mgangaReceived);

    constructor(address _mganga, address _mwanjesa, address _hyb) Ownable(msg.sender) {
        mganga = IERC20(_mganga);
        mwanjesa = IERC20(_mwanjesa);
        hyb = IERC20(_hyb);
    }

    function bridgeToDefi(uint256 amount) external {
        require(amount > 0, "Zero amount");
        mganga.transferFrom(msg.sender, address(this), amount);
        lockedMganga[msg.sender] += amount;
        uint256 output = (amount * exchangeRate) / RATE_SCALE;
        mwanjesa.transfer(msg.sender, output);
        emit BridgedToDefi(msg.sender, amount, output);
    }

    function bridgeToCefi(uint256 amount) external {
        require(amount > 0, "Zero amount");
        mwanjesa.transferFrom(msg.sender, address(this), amount);
        lockedMwanjesa[msg.sender] += amount;
        uint256 output = (amount * exchangeRate) / RATE_SCALE;
        mganga.transfer(msg.sender, output);
        emit BridgedToCefi(msg.sender, amount, output);
    }

    function setExchangeRate(uint256 _rate) external onlyOwner {
        require(_rate > 0 && _rate <= RATE_SCALE, "Invalid rate");
        exchangeRate = _rate;
    }
}
