// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title Living Relic NFT with soul reserve mechanism
contract LivingRelic is ERC721, ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;
    uint256 public soulReserveBps = 5000; // 50%

    struct RelicData {
        string relicType;
        uint256 soulReserve;
        address creator;
        uint256 validatedAt;
        bool validated;
    }

    mapping(uint256 => RelicData) public relics;
    mapping(uint256 => address[]) public validators;

    event RelicMinted(uint256 indexed tokenId, address creator, uint256 soulReserve);
    event RelicValidated(uint256 indexed tokenId, address validator);
    event ShadowProof(uint256 indexed tokenId, bytes32 contentHash);

    constructor() ERC721("LivingRelic", "RELIC") Ownable(msg.sender) {}

    function mintRelic(address to, string memory uri, string memory relicType, uint256 reward) external returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        uint256 soulReserve = (reward * soulReserveBps) / 10000;

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);

        relics[tokenId] = RelicData({
            relicType: relicType,
            soulReserve: soulReserve,
            creator: msg.sender,
            validatedAt: 0,
            validated: false
        });

        emit RelicMinted(tokenId, msg.sender, soulReserve);
        return tokenId;
    }

    function validateRelic(uint256 tokenId) external {
        require(_ownerOf(tokenId) != address(0), "Not minted");
        validators[tokenId].push(msg.sender);
        relics[tokenId].validated = true;
        relics[tokenId].validatedAt = block.timestamp;
        emit RelicValidated(tokenId, msg.sender);
    }

    function recordShadowProof(uint256 tokenId, bytes32 contentHash) external onlyOwner {
        emit ShadowProof(tokenId, contentHash);
    }

    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
