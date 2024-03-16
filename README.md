
# CrewAI - Salesforce Sales Report Generator

This application automates the extraction of sales data from Salesforce, analyzes the data, generates visual reports, and compiles a comprehensive sales performance report. It's designed to give insights into the entire sales pipeline, highlighting trends, opportunities, and areas needing attention.

## Features

- **Data Extraction**: Automatically fetches sales opportunities data from Salesforce.
- **Data Analysis**: Analyzes the sales data to identify key metrics and trends.
- **Report Generation**: Generates visual charts and a comprehensive markdown report covering the entire sales pipeline.

## Getting Started

### Prerequisites

- Python 3.8 or newer.
- A Salesforce account with access to the Salesforce API.
- An OpenAI API key if leveraging advanced analytics or AI features.

### Installation

1. Clone this repository to your local machine.
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

#### Renaming the .env.example file

1. Rename the `.env.example` file in the project root directory to `.env`.

#### Adding the appropriate keys in the .env file

1. Open the `.env` file.
2. Add the necessary keys and their corresponding values for your application.

### Running the app with Python


```bash
python app.py
```

