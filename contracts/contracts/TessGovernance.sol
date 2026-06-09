// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @title TessGovernance - HYB token holder voting
contract TessGovernance {
    IERC20 public hybToken;

    struct Proposal {
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 deadline;
        bool executed;
        mapping(address => bool) hasVoted;
    }

    Proposal[] public proposals;

    event ProposalCreated(uint256 indexed id, string description, uint256 deadline);
    event Voted(uint256 indexed proposalId, address voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId);

    constructor(address _hybToken) {
        hybToken = IERC20(_hybToken);
    }

    function createProposal(string memory description, uint256 duration) external returns (uint256) {
        uint256 id = proposals.length;
        proposals.push();
        Proposal storage p = proposals[id];
        p.description = description;
        p.deadline = block.timestamp + duration;
        emit ProposalCreated(id, description, p.deadline);
        return id;
    }

    function vote(uint256 proposalId, bool support) external {
        Proposal storage p = proposals[proposalId];
        require(block.timestamp < p.deadline, "Voting ended");
        require(!p.hasVoted[msg.sender], "Already voted");
        uint256 weight = hybToken.balanceOf(msg.sender);
        require(weight > 0, "No voting power");
        p.hasVoted[msg.sender] = true;
        if (support) p.votesFor += weight;
        else p.votesAgainst += weight;
        emit Voted(proposalId, msg.sender, support, weight);
    }

    function getProposal(uint256 id) external view returns (string memory description, uint256 votesFor, uint256 votesAgainst, uint256 deadline, bool executed) {
        Proposal storage p = proposals[id];
        return (p.description, p.votesFor, p.votesAgainst, p.deadline, p.executed);
    }
}
