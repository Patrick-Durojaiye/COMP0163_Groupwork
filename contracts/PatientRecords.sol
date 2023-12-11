// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;

interface ERC721 /* is ERC165 */ {

    event Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId);

    function balanceOf(address _owner) external view returns (uint256);

    function ownerOf(uint256 _tokenId) external view returns (address);

    function transferFrom(address _from, address _to, uint256 _tokenId) external returns (bool);

}

interface ERC165 {
    function supportsInterface(bytes4 interfaceID) external view returns (bool);
}


interface ERC721Metadata /* is ERC721 */ {

    function name() external view returns (string memory);

    function symbol() external view returns (string memory);

    function tokenURI(uint256 _tokenId) external view returns (string memory);
}


contract PatientRecords is ERC721, ERC721Metadata {
    // Total Supply of ERC721 tokens
    uint256 _totalSupply;
    // Symbol of ERC721 tokens
    string public _symbol;
    // String name of ERC721 tokens
    string _name;
    // Mapping of balances
    mapping(address=>uint256) public balances;
    // Mapping token Id's to owners
    mapping(uint256=>address) public tokenId_owner;
    // Address of the owner of the contract 
    address owner;
    //  Mapps the token ID to the tokenURI
    mapping(uint256=>string) public _tokenURI;
    // Event for when the ownership of the contract changes
    event OwnershipChange(address _oldOwner, address _newOwner);
    // Event for when a new token is minted
    event NewMint(address holder, uint256 tokenId);

    constructor(string memory __name, string memory __symbol){
        owner = msg.sender;
        _name = __name;
        _symbol = __symbol;
        _totalSupply = 0;
    }

    modifier onlyOwner() {
        // Checks if the caller is the owner of the contract
        require(msg.sender == owner, "Not the owner of the contract");
        _;
    }

    function mint(address _to, string memory uri) public onlyOwner{
        // Increases total supply
        _totalSupply+=1;
        balances[_to]+=1;
        tokenId_owner[_totalSupply]= _to;
        setTokenURI(uri, _totalSupply);
        emit NewMint(_to, _totalSupply);
    }

    function transferFrom(address _from, address _to, uint256 _tokenId) public override onlyOwner returns (bool) {
        // Transfers balances from previous holder to new holder
        balances[_to]+=1;
        balances[_from]-=1;
        tokenId_owner[_tokenId] = _to;
        emit Transfer(_from, _to, _tokenId);
        return true;
    }

    function burn(uint256 _tokenId) public onlyOwner returns (bool){
        // Transfers token from holder to a dead address
        address holder = tokenId_owner[_tokenId];
        transferFrom(holder, address(0), _tokenId);
        emit Transfer(holder, address(0), _tokenId);
        return true;
    }

    function transferOwnership(address newOwner) public returns (bool){
        // Transfers the ownership of the contract
        address prevOwner = owner;
        owner = newOwner;
        emit OwnershipChange(prevOwner, owner);
        return true;
    }

    function balanceOf(address _owner) public view returns (uint256){
        // Returns amount of tokens of an address
        return balances[_owner];
    }

    function ownerOf(uint256 _tokenId) public view returns (address){
        // Returns the address of owner of the token Id holder
        return tokenId_owner[_tokenId];
    }

    function setTokenURI(string memory uri, uint256 _tokenId) public onlyOwner {
        // Changes the token URI of a specific token Id
        _tokenURI[_tokenId] = uri;
    }

    function tokenURI(uint256 _tokenId) public view returns (string memory){
        // Returns the token URI for a specific token Id
        return _tokenURI[_tokenId];
    }
    function name() public view returns (string memory) {
        // Returns the name of the token
        return _name;
    }

    function symbol() public view returns (string memory) {
        // Returns the symbol of the token
        return _symbol;     
    }

    function totalSupply() public view returns (uint256){
        // Returns the total supply of the token
        return _totalSupply;
    }

    function currentContractOwner() public view returns (address) {
        // Returns the address of the current owner of the contract
        return owner;
    }
}