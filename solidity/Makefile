SOLC = /usr/bin/solc

all:
	$(SOLC) --bin BadgeToken.sol --evm-version byzantium | awk 'NR>3' > BadgeToken.bin
	truncate -s -1 BadgeToken.bin
	$(SOLC) --abi BadgeToken.sol --evm-version byzantium | awk 'NR>3' > BadgeToken.json

install: all
	cp -v *{json,bin} ../python/eth_badge/data/

