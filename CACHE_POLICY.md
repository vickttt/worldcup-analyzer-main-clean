# Cache Policy

The project must check cache before adding or calling any external data module.

## API-Football

- Team Info: 24 hours
- Team Logo: 24 hours
- Recent Form: 24 hours
- Injuries: 24 hours
- Lineups: 24 hours
- Fixture: 12 hours
- Match Overview: 12 hours

## The Odds API

- Match Winner: 15 minutes
- Asian Handicap: 15 minutes
- Over/Under: 15 minutes

## Polymarket

- Market prices, volume, and liquidity: 5 minutes

## Implementation

Prefer `st.cache_data` for Streamlit-facing data access.

If a future module cannot use `st.cache_data`, add a small local file cache before making repeated API requests.
