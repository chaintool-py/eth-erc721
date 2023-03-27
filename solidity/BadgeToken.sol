pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract BadgeToken {
	// EIP 173
	address public owner;

	uint256[] token; // token item registry
	uint256[] tokenMintedAt; // block height mapping to token array
	
	mapping(uint256 => uint256) tokenIndex; // tokenId to token array index
	mapping(uint256 => address) tokenOwner; // tokenId to owner address
	mapping(address => uint256[]) tokenOwnerIndex; // index of owned tokens by owner address
	mapping(uint256 => uint256) tokenOwnerIdIndex; // index of owned token ids in tokenOwnerIndex
	mapping(address => uint256) tokenOwnerCount; // end of token owner index array

	mapping(uint256 => address) tokenAllowance; // backend for approve
	mapping(address => address) tokenOperator; // backend for setApprovalForAll

	mapping(uint256 => bytes32[]) tokenData; // store optional data submitted with safeTransferFrom

	// Implements ERC721Metadata
	string public name;

	// Implements ERC721Metadata
	string public symbol;

	// Implements ERC5007
	int64 constant public endTime = 9223372036854775807; // max int64

	// Implements ERC721
	event Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId);
	// Implements ERC721
	event Approval(address indexed _owner, address indexed _approved, uint256 indexed _tokenId);
	// Implements ERC721
	event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved);

	// Implements ERC173
	event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

	event TransferWithData(address indexed _from, address indexed _to, uint256 indexed _tokenId, bytes32 _data);

	// Implements Minter
	event Mint(address indexed _minter, address indexed _beneficiary, uint256 value);

	constructor(string memory _name, string memory _symbol) {
		owner = msg.sender;
		name = _name;
		symbol = _symbol;
	}
	
	function withdraw(uint256 _amount) public returns(bool) {
		require(msg.sender == owner, 'ERR_ACCESS');
		payable(msg.sender).transfer(_amount);
		return true;
	}

	// Implements ERC721
	function balanceOf(address _owner) external view returns (uint256) {
		return tokenOwnerCount[_owner];
	}

	// Implements ERC721
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

		for (uint256 i = 0; i < _data.length; i++) {
			tokenData[_tokenId][i % 32] = _data[i];
		}
	}

	// Implements ERC721
	function transferFrom(address _from, address _to, uint256 _tokenId) external payable {
		bytes memory _data;

		_data = new bytes(0);
		transferCore(_from, _to, _tokenId, _data);
		emit Transfer(_from, _to, _tokenId);
	}

	// Implements ERC721
	function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes memory _data) external payable {
		transferCore(_from, _to, _tokenId, _data);
		emit Transfer(_from, _to, _tokenId);
		emit TransferWithData(_from, _to, _tokenId, tokenData[_tokenId][tokenData[_tokenId].length-1]);
	}

	// Implements ERC721
	function safeTransferFrom(address _from, address _to, uint256 _tokenId) external payable {
		bytes memory _data;

		_data = new bytes(0);
		transferCore(_from, _to, _tokenId, _data);
		emit Transfer(_from, _to, _tokenId);
	}

	// Implements ERC721
	function approve(address _approved, uint256 _tokenId) external payable {
		require(tokenOwner[_tokenId] == msg.sender);

		tokenAllowance[_tokenId] = _approved;

		emit Approval(msg.sender, _approved, _tokenId);
	}

	// Implements ERC721
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

	// Implements ERC721
	function getApproved(uint256 _tokenId) external view returns (address) {
		return tokenAllowance[_tokenId];
	}

	// Implements ERC721
	function isApprovedForAll(address _owner, address _operator) external view returns (bool) {
		return tokenOperator[_owner] == _operator;
	}

	// Implements ERC721Enumerable
	function totalSupply() external view returns (uint256) {
		return token.length;
	}

	// Implements ERC721Enumerable
	function tokenByIndex(uint256 _index) external view returns (uint256) {
		return token[_index];
	}

	// Implements ERC721Enumerable
	function tokenOfOwnerByIndex(address _owner, uint256 _index) external view returns (uint256) {
		require(_index < tokenOwnerCount[_owner]);

		return tokenOwnerIndex[_owner][_index];
	}

	// TODO: Implement Locator
	// Create sha256 uri from data
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

	// Implements ERC721Metadata
	function tokenURI(uint256 _tokenId) public view returns (string memory) {
		return toURI(bytes32(token[tokenIndex[_tokenId]]));
	}

	// Implements Minter
	function mintTo(address _beneficiary, uint256 _tokenId) public returns (bool) {
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

	// Implements Minter
	function mint(address _beneficiary, uint256 _tokenId, bytes calldata _data) public {
		_data;
		mintTo(_beneficiary, _tokenId);
	}

	// Implements Minter
	function safeMint(address _beneficiary, uint256 _tokenId, bytes calldata _data) public {
		_data;
		mintTo(_beneficiary, _tokenId);
	}

	// Implements Chrono
	function createTime(uint256 _idx) public view returns (int64) {
		uint256 _tokenIndex;

		_tokenIndex = tokenIndex[_idx];

		return int64(uint64(tokenMintedAt[_tokenIndex]));
	}

	// Implements ERC5007
	function startTime(uint256 _tokenId) public view returns (int64) {
		return createTime(_tokenId);
	}

	// Implements ERC173
	function transferOwnership(address _newOwner) external returns (bool) {
		require(msg.sender == owner);

		bytes memory zeroData;
		address previousOwner;
		uint256[] storage currentTokenOwnerIndex;

		previousOwner = owner;
		currentTokenOwnerIndex = tokenOwnerIndex[previousOwner];

		// TODO: Dangerous, may run out of gas
		zeroData = new bytes(0);
		for (uint256 i = 0; i < currentTokenOwnerIndex.length; i++) {
			transferCore(previousOwner, _newOwner, currentTokenOwnerIndex[i], zeroData);
		}

		owner = _newOwner;

		emit OwnershipTransferred(previousOwner, _newOwner);
		return true;
	}


	// Implements ERC165
	function supportsInterface(bytes4 interfaceID) external pure returns (bool) {
		if (interfaceID == 0xc22876c3) { // ERC721
			return true;
		}
		if (interfaceID == 0xd283ef1d) { // ERC721Metadata 
			return true;
		}
		if (interfaceID == 0xdd9d2087) { // ERC721Enumerable
			return true;
		}
		if (interfaceID == 0x5878bcf4) { // Minter
			return true;
		}
		if (interfaceID == 0x01ffc9a7) { // ERC165
			return true;
		}
		if (interfaceID == 0x9493f8b2) { // ERC173
			return true;
		}
		if (interfaceID == 0x7a0cdf92) { // ERC5007
			return true;
		}
		return false;
	}
}
