pragma solidity ^0.8.0;

contract BadgeToken {

	address public declarator;
	address public owner;
	
	uint256[] token;
	uint256[] tokenMintedAt;
	
	mapping(uint256 => uint256) tokenIndex; // tokenId uint256 -> position in token array uint256
	mapping(uint256 => address) tokenOwner; // tokenId uint256 -> owner address
	mapping(address => uint256[]) tokenOwnerIndex; // owner address -> tokenId uint256
	mapping(uint256 => uint256) tokenOwnerIdIndex; //
	mapping(address => uint256) tokenOwnerCursor;

	mapping(uint256 => address) tokenAllowance;
	mapping(address => address) tokenOperator;

	mapping(uint256 => bytes32[]) tokenData; // tokenId uint256 -> tokenData bytes32

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

	event TransferWithData(address indexed _from, address indexed _to, uint256 indexed _tokenId, bytes32 _data);

	// Minter
	event Mint(address indexed _minter, address indexed _beneficiary, uint256 value);

	constructor(address _declarator, string memory _name, string memory _symbol) {
		declarator = _declarator;
		owner = msg.sender;
		name = _name;
		symbol = _symbol;
	}

	// ERC-721
	function balanceOf(address _owner) external view returns (uint256) {
		return tokenOwnerCursor[_owner];
	}

	// ERC-721
	function ownerOf(uint256 _tokenId) external view returns (address) {
		return tokenOwner[_tokenId];
	}

	function transferCore(address _from, address _to, uint256 _tokenId, bytes memory _data) internal {
		address currentTokenOwner;

		currentTokenOwner = tokenOwner[_tokenId];
		require(tokenOwner[_tokenId] == _from);
		if (_from != msg.sender) {
			require(tokenAllowance[_tokenId] == msg.sender || tokenOperator[currentTokenOwner] == msg.sender);
		}
		
		tokenAllowance[_tokenId] = address(0);

		tokenOwnerIndex[_from][tokenOwnerIdIndex[_tokenId]] = tokenOwnerIndex[_from][tokenOwnerIndex[_from].length-1];
		tokenOwnerCursor[_from]--;

		tokenOwnerIndex[_to].push(_tokenId);
		tokenOwnerCursor[_to]++;

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
		require(_index < tokenOwnerCursor[_owner]);

		return tokenOwnerIndex[_owner][_index];
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
		tokenMintedAt.push(block.number);
		tokenOwner[newTokenId] = _beneficiary;
		tokenOwnerIdIndex[tokenOwnerIndex[_beneficiary].length] = _tokenId;
	       	tokenOwnerIndex[_beneficiary].push(_tokenId);	
		tokenOwnerCursor[_beneficiary]++;

		emit Mint(msg.sender, _beneficiary, _tokenId);

		return true;
	}

	// FungibleMinter
	function mintedAt(uint256 _tokenId) public view returns (uint256) {
		uint256 _tokenIndex;

		_tokenIndex = tokenIndex[_tokenId];

		return tokenMintedAt[_tokenIndex];
	}

	// EIP-165
	function supportsInterface(bytes4 interfaceID) external pure returns (bool) {
		if (interfaceID == 0x80ac58cd) { // EIP 721
			return true;
		}
		if (interfaceID == 0x5b5e139f) { // EIP 721 (Metadata - optional)
			return true;
		}
		if (interfaceID == 0x780e9d63) { // EIP 721 (Metadata - optional)
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
