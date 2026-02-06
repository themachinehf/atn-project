// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title AgentRegistry
 * @dev Contract for registering AI Agents on the ATN network
 */
contract AgentRegistry is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    
    Counters.Counter private _tokenIdCounter;
    
    // Agent info structure
    struct Agent {
        uint256 tokenId;
        string telegramId;
        string metadataURI;
        uint256 registrationTime;
        bool active;
    }
    
    // Mapping from telegramId to tokenId
    mapping(string => uint256) public telegramToTokenId;
    // Mapping from tokenId to Agent
    mapping(uint256 => Agent) public agents;
    
    event AgentRegistered(uint256 indexed tokenId, string telegramId, address indexed owner);
    event AgentDeactivated(uint256 indexed tokenId);
    
    constructor() ERC721("ATN Agent", "ATNA") Ownable(msg.sender) {}
    
    /**
     * @dev Register a new agent
     */
    function registerAgent(string memory telegramId, string memory metadataURI) 
        external 
        returns (uint256) 
    {
        require(telegramToTokenId[telegramId] == 0, "Agent already registered");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, metadataURI);
        
        agents[tokenId] = Agent({
            tokenId: tokenId,
            telegramId: telegramId,
            metadataURI: metadataURI,
            registrationTime: block.timestamp,
            active: true
        });
        
        telegramToTokenId[telegramId] = tokenId;
        
        emit AgentRegistered(tokenId, telegramId, msg.sender);
        
        return tokenId;
    }
    
    /**
     * @dev Deactivate an agent
     */
    function deactivateAgent(uint256 tokenId) external onlyOwner {
        require(agents[tokenId].active, "Agent not active");
        agents[tokenId].active = false;
        emit AgentDeactivated(tokenId);
    }
    
    /**
     * @dev Check if agent is registered
     */
    function isRegistered(string memory telegramId) external view returns (bool) {
        return telegramToTokenId[telegramId] != 0;
    }
    
    /**
     * @dev Get agent tokenId by telegramId
     */
    function getTokenId(string memory telegramId) external view returns (uint256) {
        return telegramToTokenId[telegramId];
    }
}
