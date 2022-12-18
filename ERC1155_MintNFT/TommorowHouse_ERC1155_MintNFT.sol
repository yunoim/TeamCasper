// SPDX-License-Identifier: MIT
 
 pragma solidity ^0.8.7;

 import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Supply.sol";
 import "@openzeppelin/contracts/utils/Strings.sol";

 contract MintNFT is ERC1155Supply {
    string public metadataURI1;
    string public metadataURI2;
    string public name;
    uint public totalNFT; 
    uint public totalNftItemCnt; // 30 + 20 : 50

    constructor(string memory _metadataURI1, string memory _metadataURI2, string memory _name, uint _totalNFT, uint _totalNftItemCnt) ERC1155(_metadataURI1) {
        metadataURI1 = _metadataURI1;
        metadataURI2 = _metadataURI2;
        name = _name;
        totalNftItemCnt = _totalNftItemCnt;
        totalNFT = _totalNFT;
    }

    function newMintNFT(address _toWalletAdress, uint _tokenId) public payable {
        require(totalNFT > totalSupply(_tokenId), "No more mint.");
        require(msg.value >= 0.01 ether, "Not Enough BNB.");

        _mint(_toWalletAdress, _tokenId, 1, "");
        payable(msg.sender).transfer(msg.value);
    }

    function uri(uint _tokenId) public override view returns(string memory) {
        if (_tokenId <= 30) {
            return string(abi.encodePacked(metadataURI1, '/', Strings.toString(_tokenId), '.json'));
        } else {
            return string(abi.encodePacked(metadataURI2, '/', Strings.toString(_tokenId - 30), '.json'));
        }
    }

    function getNFTs(address _owner) public view returns(uint[] memory) {
        uint[] memory myNFTs = new uint[](totalNftItemCnt);
        
        for(uint i = 0; i < totalNftItemCnt; i++) {
            if (exists(i)) {
                myNFTs[i] = balanceOf(_owner, i);
            } else {
                myNFTs[i] = 0;
            }
        }
 
        return myNFTs;
    }
 }
