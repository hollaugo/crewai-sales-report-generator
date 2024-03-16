import os 
from dotenv import load_dotenv
from crewai import Agent
from crewai_tools import tool
from crewai import Task
from crewai import Crew, Process
from simple_salesforce import Salesforce
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict


# Load the environment variables
load_dotenv()


#Initialize the Salesforce client
# Replace these with your Salesforce login credentials
SALESFORCE_USERNAME = os.environ["SALESFORCE_USERNAME"]
SALESFORCE_PASSWORD = os.environ["SALESFORCE_PASSWORD"]
SALESFORCE_SECURITY_TOKEN = os.environ["SALESFORCE_SECURITY_TOKEN"]
SALESFORCE_INSTANCE = os.environ["SALESFORCE_INSTANCE"]
SALESFORCE_INSTANCE_URL = os.environ["SALESFORCE_INSTANCE_URL"]

# Create a Salesforce client
sf = Salesforce(instance=SALESFORCE_INSTANCE, session_id='')
sf = Salesforce(username=SALESFORCE_USERNAME, password=SALESFORCE_PASSWORD, security_token=SALESFORCE_SECURITY_TOKEN)



# Create a Salesforce Tool 
@tool("Fetches all Opportunities from Salesforce and returns a summary.")
def fetch_all_opportunities_with_account() -> str:
    """
    Fetches all opportunities from Salesforce, including Account information, and returns a summary.

    Returns:
        str: A formatted summary of all Opportunities including Account Name.
    """
    try:
        # Query all opportunities with relevant fields including Account Name
        query = "SELECT Id, Name, Amount, StageName, CloseDate, Account.Name FROM Opportunity"
        opportunities = sf.query_all(query)

        # Check if any opportunities were found
        if opportunities['totalSize'] == 0:
            return "No Opportunities found."

        # Initialize summary
        summary = "Opportunities with Account Summary:\n\n"

        # Process each opportunity
        for opp in opportunities['records']:
            account_name = opp['Account']['Name'] if opp.get('Account') else 'N/A'
            summary += f"- Opportunity Name: {opp['Name']}, Account Name: {account_name}, Amount: {opp.get('Amount', 'N/A')}, " \
                       f"Stage: {opp.get('StageName', 'N/A')}, Close Date: {opp.get('CloseDate', 'N/A')}\n"

        return summary

    except Exception as e:
        return f"Error fetching opportunities with account information: {str(e)}"


#Tool to create graphs for Sales report
@tool("Generates and saves comprehensive sales performance charts from opportunities data.")
def plot_opportunity_graphs(opportunities: List[Dict]) -> List[str]:
    """
    Generates and saves comprehensive sales performance charts from opportunities data.
    Intended to reflect overall sales department performance and key observations, including
    total sales over time and opportunity stage distribution.
    
    Parameters:
        opportunities (List[Dict]): A list of opportunities where each opportunity is a dictionary
                                    containing at least 'Amount', 'StageName', and 'CloseDate'.
    
    Returns:
        List[str]: Paths to the saved chart images.
    """
    # Preparation steps...
    cleaned_opportunities = [opp for opp in opportunities if 'CloseDate' in opp and opp['CloseDate']]
    df = pd.DataFrame(cleaned_opportunities)

    # Proceed only if there's data to work with
    if not df.empty:
        df['CloseDate'] = pd.to_datetime(df['CloseDate'], errors='coerce')  # Convert CloseDate to datetime, coerce errors
        df = df.dropna(subset=['CloseDate'])  # Drop rows where CloseDate conversion failed

        chart_paths = []
        base_path = 'charts_sales_performance'
        os.makedirs(base_path, exist_ok=True)

        # Chart 1: Total Sales Over Time
        fig, ax = plt.subplots(figsize=(10, 6))
        df.resample('M', on='CloseDate')['Amount'].sum().plot(ax=ax)
        ax.set_title('Total Sales Over Time')
        ax.set_ylabel('Total Sales Amount')
        ax.set_xlabel('Month')
        chart_path = os.path.join(base_path, 'total_sales_over_time.png')
        plt.savefig(chart_path)
        plt.close(fig)
        chart_paths.append(chart_path)

        # Chart 2: Opportunity Stage Distribution
        plt.figure(figsize=(10, 6))
        df['StageName'].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=90, counterclock=False)
        plt.title('Opportunity Stage Distribution')
        plt.ylabel('')  # Hide the y-label as it's not necessary for pie charts
        chart_path_stage_dist = os.path.join(base_path, 'opportunity_stage_distribution.png')
        plt.savefig(chart_path_stage_dist)
        plt.close()
        chart_paths.append(chart_path_stage_dist)

        return chart_paths
    else:
        return ["No valid opportunities data available for chart generation."]




#Sales Analyst Agent
sales_analyst = Agent(
    role='Sales Data Analyst',
    goal='Analyze Salesforce opportunities and visualize data across the entire sales pipeline',
    verbose=True,
    memory=True,
    backstory=(
        "Equipped with analytical skills and a knack for visualization, you delve into Salesforce data to "
        "draw out key insights across the entire sales pipeline. Through meticulous analysis and chart plotting, "
        "you transform raw data into visual stories that highlight overall trends and opportunities, "
        "setting the stage for strategic decisions."
    ),
    tools=[fetch_all_opportunities_with_account, plot_opportunity_graphs],  # Tools for fetching and plotting
    allow_delegation=True
)

#Report Writer Agent
report_writer = Agent(
    role='Report Writer',
    goal='Compile analysis and charts into a comprehensive sales performance report',
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for synthesis and narrative, you adeptly combine analytical insights and visualizations "
        "into compelling reports. Your work not only informs but also engages stakeholders, making complex data "
        "accessible and actionable for the entire sales department."
    ),
    tools=[],  # No specific tools, but responsible for compiling the final report
    allow_delegation=False
)


# Task for sales analyst to perform data analysis and create charts for the entire sales pipeline
analysis_and_charting_task = Task(
    description=(
        "Extract Salesforce opportunities, analyze the data, and create visualizations that cover the entire sales pipeline. "
        "Summarize your findings and include generated charts in a Markdown document, providing a foundation "
        "for the comprehensive sales performance report."
    ),
    expected_output='A Markdown document with analysis and charts covering the entire sales pipeline.',
    tools=[fetch_all_opportunities_with_account, plot_opportunity_graphs],
    agent=sales_analyst,
    output_file='pipeline_analysis.md'  # Markdown file for analysis and charts
)

# Task for report writer to compile the final comprehensive sales performance report
final_report_task = Task(
    description=(
        "Using the provided analysis and charts, craft a detailed sales performance report that encompasses the entire sales pipeline. "
        "Ensure the report is comprehensive, integrating both textual analysis and visual data representations. "
        "Compile the final report into a Markdown document."
    ),
    expected_output='A comprehensive sales performance report in Markdown format, with embedded charts.',
    tools=[],
    agent=report_writer,
    output_file='final_sales_report.md'  # Markdown document for the final report
)

# Crew to orchestrate the sales report creation process
sales_crew = Crew(
    agents=[sales_analyst, report_writer],
    tasks=[analysis_and_charting_task, final_report_task],
    process=Process.sequential  # Sequential execution ensures analysis and charting precede report writing
)

# Initiating the process to create a comprehensive sales report
result = sales_crew.kickoff(inputs={})
print(result)
