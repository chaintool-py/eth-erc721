SOLC = /usr/bin/solc

all:
	$(SOLC) --bin BadgeToken.sol --evm-version byzantium | awk 'NR>3' > BadgeToken.bin
	$(SOLC) --abi BadgeToken.sol --evm-version byzantium | awk 'NR>3' > BadgeToken.json
	$(SOLC) --metadata BadgeToken.sol --evm-version byzantium | awk 'NR>3' > BadgeToken.metadata.json
	truncate -s -1 BadgeToken.bin

install: all
	cp -v *.json ../python/eth_badgetoken/data/
	cp -v *.bin ../python/eth_badgetoken/data/

