//SPDX-License-Identifier:MIT
pragma solidity ^0.6.6;
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol"; 

//VRF consumer base for getting the random number from oracle..
//min 50 usd to enter the lottery

contract Lottery is VRFConsumerBase,Ownable{
    uint256 public usdEntryFee;
    address payable[] public players;
    AggregatorV3Interface internal ethUsdPriceFeed;
    address payable public winner;
    uint256 public randomness;

//CREATING CUSTOM DATA TYPE USING ENUM
    enum LOTTERY_STATE {   
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 public fee; //fees to be paid for getting the random number
    bytes32 public keyhash; //uniquely identifies the chainlink node
    event RequestedRandomness(bytes32 requestId); //creating an event

    constructor (
        address _priceFeedAddress, 
        address _vrfCoordinator, 
        address _link,
        uint256 _fee,
        bytes32 _keyhash
        ) 
        public VRFConsumerBase(_vrfCoordinator,_link)
    {
    usdEntryFee= 50*(10**18);
    ethUsdPriceFeed=AggregatorV3Interface(_priceFeedAddress);
    lottery_state=LOTTERY_STATE.CLOSED;
    fee=_fee;
    keyhash=_keyhash;

}

    function enter() public payable{
        require(lottery_state == LOTTERY_STATE.OPEN); 
        require(msg.value >= getEntranceFee(),
        "Money not enough to enter lottery");
        players.push(msg.sender);
    }
    function getEntranceFee() public view returns(uint256){
        (,int256 price, ,,)=ethUsdPriceFeed.latestRoundData();
        uint adjustedPrice=uint256(price)*10**10;
        uint256 costToEnter= usdEntryFee*10**18/adjustedPrice;
        return costToEnter;
    }
    function startLottery() public onlyOwner{
        require(lottery_state == LOTTERY_STATE.CLOSED,
        "Lottery not opened yet!!"); 

        lottery_state=LOTTERY_STATE.OPEN;
    }
    function endLottery() public onlyOwner{
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyhash, fee); 
        emit RequestedRandomness(requestId);
        //asking for a random number 
        // happens in two transcations ..
        //in the fisrt one the random number is generated and verified for true randomness
        //then its returned by calling an other function called fullfillrandomness
        
}
 function fulfillRandomness(bytes32 _requestId, uint256 _randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "wait for sometime!"
        );
        require(_randomness > 0, "random-not-found");
        uint256 indexOfWinner = _randomness % players.length;
        winner = players[indexOfWinner];
        winner.transfer(address(this).balance);
        // Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}