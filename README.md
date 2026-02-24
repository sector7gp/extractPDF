## Set the environment

<code>python -m venv venv</code>


## Install dependencies

<code>pip install -r requirements.txt</code>


## Changelog

### 2026-02-24
- **Regex Update**: Support for two ticket formats: "Exceso de velocidad" and "Multa Velocidad".
- **Amount Formatting**: Normalized amounts to ISO format (e.g., `1234.56`).
- **Infraction Numbers**: Automatic generation of IDs (`YYMMDDRR`) for tickets missing an official infraction number.
- **CSV Format**: Updated separator to comma `,`.
- **Validation**: Added built-in test cases for all formats.
