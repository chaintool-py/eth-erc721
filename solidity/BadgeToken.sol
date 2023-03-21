pragma solidity ^0.8.0;

// SPDX-License-Identifier: GPL-3.0-or-later

contract BadgeToken {

	// EIP 173
	address public owner;

	uint256[] token; // token item registry
	uint256[] tokenMintedAt; // block height mapping to token array
	
	mapping(uint256 => uint256) tokenIndex; // tokenId to token array index
	mapping(uint256 => address) tokenOwner; // tokenId to owner address
	mapping(address => uint256[]) tokenOwnerIndex; // index of owned tokens by owner address
	mapping(uint256 => uint256) tokenOwnerIdIndex; // index of owned token ids in tokenOwnerIndex
	mapping(address => uint256) public tokenOwnerCount; // end of token owner index array

	mapping(uint256 => address) tokenAllowance; // backend for approve
	mapping(address => address) tokenOperator; // backend for setApprovalForAll

	mapping(uint256 => bytes32[]) tokenData; // store optional data submitted with safeTransferFrom

	// ERC-721 (Metadata - optional)
	string public name;

	// ERC-721 (Metadata - optional)
	string public symbol;

	// ERC-721
	event Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId);
	// ERC-721
	event Approval(address indexed _owner, address indexed _approved, uint256 indexed _tokenId);
	// ERC-721
	event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved);

	// EIP-173
	event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

	event TransferWithData(address indexed _from, address indexed _to, uint256 indexed _tokenId, bytes32 _data);

	// Minter
	event Mint(address indexed _minter, address indexed _beneficiary, uint256 value);

	constructor(string memory _name, string memory _symbol) {
		owner = msg.sender;
		name = _name;
		symbol = _symbol;
	}

	// ERC-721
	function balanceOf(address _owner) external view returns (uint256) {
		return tokenOwnerCount[_owner];
	}

	// ERC-721
	function ownerOf(uint256 _tokenId) external view returns (address) {
		return tokenOwner[_tokenId];
	}

	// shared function for transfer methods
	function transferCore(address _from, address _to, uint256 _tokenId, bytes memory _data) internal {
		address currentTokenOwner;

		currentTokenOwner = tokenOwner[_tokenId];
		require(tokenOwner[_tokenId] == _from);
		if (_from != msg.sender) {
			require(tokenAllowance[_tokenId] == msg.sender || tokenOperator[currentTokenOwner] == msg.sender);
		}
		
		tokenAllowance[_tokenId] = address(0);

		tokenOwnerIndex[_from][tokenOwnerIdIndex[_tokenId]] = tokenOwnerIndex[_from][tokenOwnerIndex[_from].length-1];
		tokenOwnerCount[_from]--;

		tokenOwnerIndex[_to].push(_tokenId);
		tokenOwnerCount[_to]++;

		tokenOwner[_tokenId] = _to;

		for (uint256 i; i < _data.length; i++) {
			tokenData[_tokenId][i % 32] = _data[i];
		}
	}

	// ERC-721
	function transferFrom(address _from, address _to, uint256 _tokenId) external payable {
		bytes memory _data;

		transferCore(_from, _to, _tokenId, _data);
		emit Transfer(_from, _to, _tokenId);
	}

	// ERC-721
	function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes memory _data) external payable {
		transferCore(_from, _to, _tokenId, _data);
		emit Transfer(_from, _to, _tokenId);
		emit TransferWithData(_from, _to, _tokenId, tokenData[_tokenId][tokenData[_tokenId].length-1]);
	}

	// ERC-721
	function safeTransferFrom(address _from, address _to, uint256 _tokenId) external payable {
		bytes memory _data;

		transferCore(_from, _to, _tokenId, _data);
		emit Transfer(_from, _to, _tokenId);
	}

	// ERC-721
	function approve(address _approved, uint256 _tokenId) external payable {
		require(tokenOwner[_tokenId] == msg.sender);

		tokenAllowance[_tokenId] = _approved;

		emit Approval(msg.sender, _approved, _tokenId);
	}

	// ERC-721
	function setApprovalForAll(address _operator, bool _approved) external {
		if (_approved) {
			require(tokenOperator[msg.sender] == address(0)); // save a few bucks in gas if fail
			tokenOperator[msg.sender] = _operator;
		} else {
			require(tokenOperator[msg.sender] != address(0));
			tokenOperator[msg.sender] = address(0);
		}
		emit ApprovalForAll(msg.sender, _operator, _approved);
	}

	// ERC-721
	function getApproved(uint256 _tokenId) external view returns (address) {
		return tokenAllowance[_tokenId];
	}

	// ERC-721
	function isApprovedForAll(address _owner, address _operator) external view returns (bool) {
		return tokenOperator[_owner] == _operator;
	}

	// ERC-721 (Enumerable - optional)
	function totalSupply() external view returns (uint256) {
		return token.length;
	}

	// ERC-721 (Enumerable - optional)
	function tokenByIndex(uint256 _index) external view returns (uint256) {
		return token[_index];
	}

	// ERC-721 (Enumerable - optional)
	function tokenOfOwnerByIndex(address _owner, uint256 _index) external view returns (uint256) {
		require(_index < tokenOwnerCount[_owner]);

		return tokenOwnerIndex[_owner][_index];
	}

	// create sha256 scheme URI from tokenId
	function toURI(bytes32 _data) public pure returns(string memory) {
		bytes memory out;
		uint8 t;
		uint256 c;

		out = new bytes(64 + 7);
		out[0] = "s";
		out[1] = "h";
		out[2] = "a";
		out[3] = "2";
		out[4] = "5";
		out[5] = "6";
		out[6] = ":";
		
		c = 7;	
		for (uint256 i = 0; i < 32; i++) {
			t = (uint8(_data[i]) & 0xf0) >> 4;
			if (t < 10) {
				out[c] = bytes1(t + 0x30);
			} else {
				out[c] = bytes1(t + 0x57);
			}
			t = uint8(_data[i]) & 0x0f;
			if (t < 10) {
				out[c+1] = bytes1(t + 0x30);
			} else {
				out[c+1] = bytes1(t + 0x57);
			}
			c += 2;
		}
		return string(out);
	}

	// ERC-721 (Metadata - optional)
	function tokenURI(uint256 _tokenId) public view returns (string memory) {
		return toURI(bytes32(token[tokenIndex[_tokenId]]));
	}

	// Minter
	function mintTo(address _beneficiary, uint256 _tokenId) external returns (bool) {
		require(owner == msg.sender);
		require(tokenIndex[_tokenId] == 0x0 || token.length == 0);

		uint256 newTokenIndex;
		uint256 newTokenId;

		newTokenIndex = token.length;
		newTokenId = uint256(_tokenId);

		token.push(newTokenId);
		tokenIndex[newTokenId] = newTokenIndex;
		tokenMintedAt.push(block.number);
		tokenOwner[newTokenId] = _beneficiary;
		tokenOwnerIdIndex[tokenOwnerIndex[_beneficiary].length] = _tokenId;
	       	tokenOwnerIndex[_beneficiary].push(_tokenId);	
		tokenOwnerCount[_beneficiary]++;

		emit Mint(msg.sender, _beneficiary, _tokenId);

		return true;
	}

	// Chrono
	function createdAt(uint256 _tokenId) public view returns (uint256) {
		uint256 _tokenIndex;

		_tokenIndex = tokenIndex[_tokenId];

		return tokenMintedAt[_tokenIndex];
	}

	// EIP-173
	function transferOwnership(address _newOwner) external returns (bool) {
		require(msg.sender == owner);

		bytes memory zeroData;
		address previousOwner;
		uint256[] storage currentTokenOwnerIndex;

		previousOwner = owner;
		currentTokenOwnerIndex = tokenOwnerIndex[previousOwner];

		for (uint256 i; i < currentTokenOwnerIndex.length; i++) {
			transferCore(previousOwner, _newOwner, currentTokenOwnerIndex[i], zeroData);
		}

		owner = _newOwner;

		emit OwnershipTransferred(previousOwner, _newOwner);
		return true;
	}


	// EIP-165
	function supportsInterface(bytes4 interfaceID) external pure returns (bool) {
		if (interfaceID == 0xc22876c3) { // EIP 721
			return true;
		}
		if (interfaceID == 0xd283ef1d) { // EIP 721 (Metadata - optional)
			return true;
		}
		if (interfaceID == 0xdd9d2087) { // EIP 721 (Enumerable - optional)
			return true;
		}
		if (interfaceID == 0x449a52f8) { // Minter
			return true;
		}
		if (interfaceID == 0x01ffc9a7) { // EIP 165
			return true;
		}
		return false;
	}
}
