# tap-chameleon

A Singer tap for extracting data from the Chameleon API, built using the Singer SDK and designed to work with Meltano.

## Overview

tap-chameleon is a Singer tap that extracts data from Chameleon's REST API, specifically focused on survey responses and associated profile data. It supports incremental replication and pagination through Chameleon's API endpoints.

## Features

- Extracts survey responses and profile data from Chameleon
- Supports incremental replication
- Handles API pagination
- Built with Singer SDK
- Meltano compatible

## Installation

1. Install using pipx and poetry:
```bash
pipx install poetry
poetry install
```

2. Update and install dependencies:
```bash
meltano lock --update --all
meltano install
```

3. Configure the tap using one of these methods:

   a. Set environment variables:
   ```bash
   export TAP_CHAMELEON_API_BASE_URL=https://api.chameleon.io
   export TAP_CHAMELEON_SURVEY_ID=
   export TAP_CHAMELEON_LIMIT=50
   export TAP_CHAMELEON_API_ACCOUNT_SECRET=your_secret_here
   export TAP_CHAMELEON_CREATED_AFTER=2024-12-04T18:51:01.000Z
   export TAP_CHAMELEON_CREATED_BEFORE=2024-12-04T18:51:19.000Z
   export TAP_CHAMELEON_SURVEY_NAME=test_survey
   ```

   OR

   b. Configure interactively:
   ```bash
   meltano config tap-chameleon set --interactive
   ```

4. Run the tap with target-jsonl:
```bash
meltano run tap-chameleon target-jsonl
```


### Required Configuration Fields:

- `api_account_secret`: Your Chameleon API account secret token
- `survey_id`: The ID of the survey to fetch responses for

### Optional Configuration Fields:

- `api_base_url`: Base URL for the Chameleon API (default: https://api.chameleon.io)
- `survey_name`: Name of the survey
- `limit`: Number of records per page (default: 50, max: 500)
- `created_before`: Filter responses created before this timestamp/ID
- `created_after`: Filter responses created after this timestamp/ID

## Usage

### Local Execution

Run the tap in discovery mode:
```bash
poetry run tap-chameleon --discover > catalog.json
```

### Meltano Integration

Add to your Meltano project:

```yaml
plugins:
  extractors:
  - name: tap-chameleon
    namespace: tap_chameleon
    pip_url: git+https://github.com/degreed-data-engineering/tap-chameleon
    capabilities:
    - state
    - catalog
    - discover
    config:
      api_account_secret: $TAP_CHAMELEON_API_ACCOUNT_SECRET
      survey_id: $TAP_CHAMELEON_SURVEY_ID
```

For the complete Meltano configuration, see the `meltano.yml` file in the repository.

## Streams

### Survey Responses
- Endpoint: `/v3/analyze/responses`
- Primary key: `id`
- Replication strategy: FULL_TABLE

### Profiles
- Endpoint: `/v3/analyze/profiles/{id}`
- Primary key: `id`
- Parent stream: survey_responses
- Replication strategy: FULL_TABLE
