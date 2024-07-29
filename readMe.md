# Meridian Arbitrage Bot

This bot can be used to arbitrage the price of USDM, the process works as follows:


- The bot will hold a reserve of USDT
- If USDM dips below $1, the bot will swap USDT to USDM
- The bot then redeems this USDM for $1 worth of TARA tokens through the platform
- The bot then sells the TARA tokens on an DEX for $1 worth of USDT, netting a small profit in the process

## Configuration

Networks can be configured in the config.json file. 

Note: Make sure that the DEX configurations work, it might be necessary to add new swap functions for different types of DEXs. 

## Running

Meridian Arbitrage bot can be run using Docker as follows:
```bash
docker-compose up -d --build
```

## License

[MIT](https://choosealicense.com/licenses/mit/)