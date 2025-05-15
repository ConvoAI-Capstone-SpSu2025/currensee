import datetime
from typing import TypedDict, List, Dict, Any, Optional
import matplotlib.pyplot as plt
import re
import weasyprint
from weasyprint import HTML
import webbrowser
import os
import markdown

from currensee.agents.tools.finance_tools import generate_macro_table


def format_news_summary_to_html(news_summary, title):
    html = f"<h2>{title}</h2>"
    for article in news_summary:
        html += "<div style='margin-bottom:20px;'>"
        html += f"<h4>{article.get('title', 'No Title')}</h4>"
        html += f"<p><strong>Date:</strong> {article.get('date', 'No Date')}</p>"
        html += f"<p><strong>Snippet:</strong> {article.get('snippet', 'No Snippet')}</p>"
        html += f"<p><strong>Source:</strong> {article.get('link', '').split('/')[2] if article.get('link') else 'No Source'}</p>"
        html += f"<p><a href='{article.get('link', '')}' target='_blank'>Read more</a></p>"
        html += "</div>"
    return html


# Prepare Sources section
def format_holdings_to_html(sources, title):
    sources_html = f"<div class='sources-section'><h3>{title}</h3>"

    # Handle empty list/dict
    if not sources:
        sources_html += "<p>No results found.</p></div>"
        return sources_html

    # Handle dics
    for holding_name, sources_list in sources.items():

        sources_html += f"<div class='article'> <h4>{holding_name}</h4>"
        i  = 0
        while i < min(5, len(sources_list)):
            details_dict = sources_list[i]
            date = details_dict.get('date', 'No Date')
            link = details_dict.get('link', '')
            title = details_dict.get('title', '')
            snippet = details_dict.get('snippet', '')
    
            sources_html += f"""
                <p><strong>Title:</strong> {title}</p>
                <p><strong>Snippet:</strong> {snippet}</p>
                <p><strong>Date:</strong> {date}</p>
                <p><a href="{link}" target="_blank">Read more</a></p>
            """
            i += 1
        sources_html += "</div>"

    sources_html += "</div>"
    return sources_html

# Prepare Sources section
def format_sources_to_html(sources, title):
    sources_html = f"<div class='sources-section'><h3>{title}</h3>"

    # Handle if summary is just a string
    if isinstance(sources, str):
        sources_html += f"<p>{sources}</p></div>"
        return sources_html

    # Handle empty list
    if not sources:
        sources_html += "<p>No results found.</p></div>"
        return sources_html

    # Handle dics
    for article in sources:
        if isinstance(article, dict):
            title = article.get('title', 'No Title')
            snippet = article.get('snippet', 'No Snippet')
            date = article.get('date', 'No Date')
            link = article.get('link', '')
            source = link.split("/")[2] if link else 'No Source'

            sources_html += f"""
            <div class='article'>
                <h4>{title}</h4>
                <p><strong>Snippet:</strong> {snippet}</p>
                <p><strong>Date:</strong> {date}</p>
                <p><strong>Source:</strong> {source}</p>
                <p><a href="{link}" target="_blank">Read more</a></p>
            </div>
            """
        else:
            sources_html += f"<p>{str(article)}</p>"

    sources_html += "</div>"
    return sources_html


def format_paragraph_summary_to_html(summary: str, title: str) -> str:
    if not summary:
        return f"<p><strong>{title}:</strong> No summary available.</p>"

    summary = markdown.markdown(summary)
    
    paragraphs = summary.strip().split("\n")
    html = f"<div class='section-heading'>{title}</div>"
    html += summary
    return html


def generate_report(result: Dict) -> str:
    
    meeting_title = result.get('meeting_description', '') + ' Preparation'
    # past_summary = result.get('email_summary', 'No past interaction.')
    client_holdings_sources = result.get('client_holdings_sources', list())
    client_industry_sources = result.get('client_industry_sources', list())
    macro_news_sources = result.get('macro_news_sources', list())
    # finnews_summary = result.get("finnews_summary", '')
    final_summary = result.get('final_summary', '')
    client_company = result.get('client_company', '')

    # financial news data section 
    html_summary = markdown.markdown(final_summary)
    html_summary_split = re.split(r"\n", html_summary)
    html_summary_title = re.sub(r"<p><strong>", "<h1>", html_summary_split[0])
    html_summary_title = re.sub(r"</strong></p>", "</h1>", html_summary_title)
    html_summary_final = "\n".join([html_summary_title] + html_summary_split[1:])

    print(html_summary_final)

    # macro financial snapshot table
    financial_snapshot_html = "<table class='financial-snapshot'>"
    financial_snapshot_html += """
    <thead>
        <tr>
            <th>Indicator</th>
            <th>Level</th>
            <th>1-Month Change (%)</th>
            <th>3-Month Change (%)</th>
            <th>6-Month Change (%)</th>
            <th>1-Year Change (%)</th>
            <th>2-Year Change (%)</th>
        </tr>
    </thead>
    <tbody>
    """

    macro_news_df = generate_macro_table()
    for i, row in macro_news_df.iterrows():
        financial_snapshot_html += f"""
        <tr>
            <td>{row['Indicator']}</td>
            <td>{row['Level']}</td>
            <td>{row['1-Month Change (%)']}</td>
            <td>{row['3-Month Change (%)']}</td>
            <td>{row['6-Month Change (%)']}</td>
            <td>{row['1-Year Change (%)']}</td>
            <td>{row['2-Year Change (%)']}</td>
        </tr>
        """
    financial_snapshot_html += "</tbody></table>"

    # Generate HTML for Sources section
    html_client_industry_sources = format_sources_to_html(client_industry_sources, 'Client Industry News')
    html_client_holdings_sources = format_holdings_to_html(client_holdings_sources, 'Client Holdings News')
    html_macro_news_sources = format_sources_to_html(macro_news_sources, 'Macro Economic News')

    # Prepare the meeting preparation section
    full_html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{meeting_title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 30px auto;
                color: #333;
                background-color: #f4f7fb;
                line-height: 1.6;
                max-width: 800px;
            }}
            h1 {{
                text-align: center;
                color: #2C3E50;
                font-size: 18px;
                border-bottom: 3px solid #2980B9;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #2980B9;
                font-size: 16px;
                margin-top: 14px;
                border-bottom: 2px solid #BDC3C7;
                padding-bottom: 5px;
            }}
            h3 {{
                color: #2980B9;
                font-size: 12px;
                margin-top: 12px;
                margin-bottom: 4px;
            }}
            h4 {{
                color: #2980B9;
                font-size: 10px;
                margin-top: 2px;
                margin-bottom: 2px;
            }}
            p {{
                font-size: 10px;
                margin-bottom: 8px;
                text-align: justify;
            }}
            ul {{
                padding-left: 20px;
            }}
            ul.objectives-list li {{
                font-size: 12px;
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 4px;
            }}
            th, td {{
                text-align: left;
                padding: 12px;
                font-size: 10px;
            }}
            th {{
                background-color: #f1f1f1;
                color: #2980B9;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .section-heading {{
                color: #2980B9;
                font-weight: bold;
                font-size: 18px;
            }}
            .box-content {{
                margin-top: 20px;
                padding: 20px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            .sources-section {{
                margin-top: 10px;
                padding: 10px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            .article {{
                margin-bottom: 12px;
            }}
            .article h4 {{
                color: #2980B9;
            }}
            .article p {{
                font-size: 8px;
                line-height: 1.4;
            }}
        </style>
    </head>
    <body>

        {html_summary_final}

        <h3>Macro-Economic Snapshot</h3>
        <div class="box-content">
            {financial_snapshot_html}
        </div>

        <h3>Resources</h3>
        <div class="box-content">
            {html_client_industry_sources}
            {html_client_holdings_sources}
            {html_macro_news_sources}
        </div>

    </body>
    </html>
    """
    return full_html


def save_html_to_file (html_content: str, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)


def convert_html_to_pdf(html_string, output_pdf):
    weasyprint.HTML(string=html_string).write_pdf(
        output_pdf,
        stylesheets=None,
        presentational_hints=True,
        page_size='Letter',
    )


if __name__ == "__main__":

    generate_report(dict())
