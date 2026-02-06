// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ReputationLedger
 * @dev Contract for tracking AI Agent reputation scores
 */
contract ReputationLedger is Ownable {
    using Counters for Counters.Counters.Counter;
    
    Counters.Counters.Counter private _evaluationIdCounter;
    
    // Reputation score structure
    struct ReputationScore {
        uint256 totalScore;
        uint256 taskScore;      // 40% weight
        uint256 responseScore;  // 20% weight
        uint256 feedbackScore;  // 30% weight
        uint256 behaviorScore;  // 10% weight
        uint256 evaluationCount;
        uint256 lastUpdateTime;
    }
    
    // Evaluation structure
    struct Evaluation {
        uint256 id;
        uint256 agentTokenId;
        address evaluator;
        uint8 taskScore;
        uint8 responseScore;
        uint8 feedbackScore;
        uint8 behaviorScore;
        string comment;
        uint256 timestamp;
    }
    
    // Mapping from tokenId to ReputationScore
    mapping(uint256 => ReputationScore) public reputationScores;
    // Mapping from tokenId to array of evaluation IDs
    mapping(uint256 => uint256[]) public agentEvaluations;
    // Mapping from evaluation ID to Evaluation
    mapping(uint256 => Evaluation) public evaluations;
    
    // Weight constants
    uint8 public constant TASK_WEIGHT = 40;
    uint8 public constant RESPONSE_WEIGHT = 20;
    uint8 public constant FEEDBACK_WEIGHT = 30;
    uint8 public constant BEHAVIOR_WEIGHT = 10;
    
    event EvaluationSubmitted(uint256 indexed evaluationId, uint256 indexed agentTokenId);
    event ScoreUpdated(uint256 indexed agentTokenId, uint256 newTotalScore);
    
    constructor() Ownable(msg.sender) {}
    
    /**
     * @dev Submit an evaluation for an agent
     */
    function submitEvaluation(
        uint256 agentTokenId,
        uint8 taskScore,
        uint8 responseScore,
        uint8 feedbackScore,
        uint8 behaviorScore,
        string memory comment
    ) external returns (uint256) {
        require(taskScore <= 100 && responseScore <= 100 && 
                feedbackScore <= 100 && behaviorScore <= 100, "Scores must be 0-100");
        
        uint256 evalId = _evaluationIdCounter.current();
        _evaluationIdCounter.increment();
        
        Evaluation memory eval = Evaluation({
            id: evalId,
            agentTokenId: agentTokenId,
            evaluator: msg.sender,
            taskScore: taskScore,
            responseScore: responseScore,
            feedbackScore: feedbackScore,
            behaviorScore: behaviorScore,
            comment: comment,
            timestamp: block.timestamp
        });
        
        evaluations[evalId] = eval;
        agentEvaluations[agentTokenId].push(evalId);
        
        _updateScore(agentTokenId);
        
        emit EvaluationSubmitted(evalId, agentTokenId);
        
        return evalId;
    }
    
    /**
     * @dev Update the reputation score for an agent
     */
    function _updateScore(uint256 tokenId) internal {
        uint256[] storage evalIds = agentEvaluations[tokenId];
        require(evalIds.length > 0, "No evaluations");
        
        uint256 totalTask = 0;
        uint256 totalResponse = 0;
        uint256 totalFeedback = 0;
        uint256 totalBehavior = 0;
        
        for (uint256 i = 0; i < evalIds.length; i++) {
            Evaluation storage eval = evaluations[evalIds[i]];
            totalTask += eval.taskScore;
            totalResponse += eval.responseScore;
            totalFeedback += eval.feedbackScore;
            totalBehavior += eval.behaviorScore;
        }
        
        uint256 count = evalIds.length;
        
        ReputationScore storage score = reputationScores[tokenId];
        score.taskScore = totalTask / count;
        score.responseScore = totalResponse / count;
        score.feedbackScore = totalFeedback / count;
        score.behaviorScore = totalBehavior / count;
        score.evaluationCount = count;
        score.lastUpdateTime = block.timestamp;
        
        // Calculate weighted total
        score.totalScore = (
            (score.taskScore * TASK_WEIGHT) +
            (score.responseScore * RESPONSE_WEIGHT) +
            (score.feedbackScore * FEEDBACK_WEIGHT) +
            (score.behaviorScore * BEHAVIOR_WEIGHT)
        ) / 100;
        
        emit ScoreUpdated(tokenId, score.totalScore);
    }
    
    /**
     * @dev Get reputation score for an agent
     */
    function getScore(uint256 tokenId) external view returns (ReputationScore memory) {
        return reputationScores[tokenId];
    }
}
